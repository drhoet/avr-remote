import aiohttp
import importlib
import os
import json
import traceback

from .default_config import default_config as config
from .avr.base import AvrZonePropertyUpdate, AvrTunerPropertyUpdate, UnsupportedUpdateException

class AvrMessage:
    """ A message that can be sent to the Avr. """
    def __init__(self, type, extras, state):
        self.type = type
        self._state = state
        self._extras = extras

    def to_dict(self):
        """ Convert to a dict that can be sent over the web socket to the clients"""
        msg = {'type': self.type, 'state': self._state}
        msg.update(self._extras)
        return msg

    def __repr__(self):
        return "{0}({1}, {2}, {3})".format(self.__class__.__name__, self.type, self._state, self._extras)

    def create(update):
        if isinstance(update, AvrZonePropertyUpdate):
            return AvrZoneMessage(update)
        elif isinstance(update, AvrTunerPropertyUpdate):
            return AvrTunerMessage(update)


class AvrStaticInfoMessage(AvrMessage):
    """ An AvrMessage containing the static avr information """
    def __init__(self, state):
        super().__init__('static_info', {}, state)


class AvrZoneMessage(AvrMessage):
    """ An AvrMessage that is specific to one zone"""
    def __init__(self, avr_update):
        """ Creates a new AvrZoneMessage based on a AvrZonePropertyUpdate """
        super().__init__('zone', {'zoneId': avr_update.zoneId}, {avr_update.property: avr_update.value})


class AvrTunerMessage(AvrMessage):
    """ An AvrMessage for a tuner"""
    def __init__(self, avr_update):
        """ Creates a new AvrTunerMessage based on a AvrTunerPropertyUpdate """
        super().__init__('tuner', {}, {avr_update.property: avr_update.value})


class AvrError(AvrMessage):
    """An error occurred."""
    def __init__(self, source, message):
        super().__init__('error', {'source': source}, {'message': message})

class AvrHandler:

    def __init__(self, avr):
        self.avr = avr
        self.client_count = 0

    async def send_message(self, ws, msg):
        """ Send an message to the clients

        Keyword arguments:
        ws -- the websocket over which to send the message
        msg -- the message to send. Must be an AvrMessage or subclass.
        """
        print('<< {0}'.format(msg))
        await ws.send_json(msg.to_dict())

    # The handler of the AVR. This one is listening for status updates of the avr.
    async def avr_handler(self, ws):
        if not await self.avr.connected:
            await self.avr.connect()
        self.client_count = self.client_count + 1

        try:
            static_info = AvrStaticInfoMessage(await self.avr.static_info)
            await self.send_message(ws, static_info)

            async for updates in self.avr.listen():
                print('In the async for loop', updates)
                for avr_update in updates:
                    await self.send_message(ws, AvrMessage.create(avr_update))
        except:
            import traceback
            traceback.print_exc()
            raise
        finally:
            self.client_count = self.client_count - 1
            if self.client_count <= 0:
                await self.avr.disconnect()

    # processes requests from the clients
    async def process_request(self, request):
        if request['type'] == 'zone':
            zoneId = request['zoneId']
            state = request['state']
            for key, value in state.items():
                avr_update = AvrZonePropertyUpdate(zoneId, key, value)
                await self.avr.send(avr_update)

    # The handler of the websocket. This one is listening for requests of the clients
    # When a request is received, most of the handling is passed over to the process_request method.
    async def websocket_handler(self, request):
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(request)

        task = request.app.loop.create_task(self.avr_handler(ws))

        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    json = msg.json()
                    print('>> [{0}] {1}'.format(json['type'], json))
                    try:
                        await self.process_request(json)
                    except UnsupportedUpdateException as err:
                        await self.send_message(ws, AvrError('websocket_handler', err.message))
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print('ws connection closed with exception %s' % ws.exception())
        except:
            traceback.print_exc()
            raise
        finally:
            task.cancel()

        print('websocket connection closed')
        return ws


def create_app(loop):
    config_file = os.getenv('AVRREMOTE_SETTINGS', None)
    if config_file is not None:
        with open(config_file) as f:
            config.update(json.load(f))

    app = aiohttp.web.Application()
    app['config'] = config

    avr_class = getattr(importlib.import_module(app['config']['avr_module']), app['config']['avr_class'])
    avr = avr_class(app['config']['avr_connection'])
    avr_handler = AvrHandler(avr)

    app.router.add_static('/static-new', 'avrremote/static-new')
    app.router.add_get('/ws', avr_handler.websocket_handler)

    aiohttp.web.run_app(app, host='0.0.0.0', port=5000)
