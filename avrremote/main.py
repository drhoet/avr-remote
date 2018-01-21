import aiohttp
import json
import traceback
import datetime

from .avr.base import AvrZonePropertyUpdate, AvrTunerPropertyUpdate, UnsupportedUpdateException, AvrCommandError

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
        super().__init__('tuner', {'internalId': avr_update.internalId}, {avr_update.property: avr_update.value})


class AvrError(AvrMessage):
    """An error occurred."""
    def __init__(self, source, message):
        super().__init__('error', {'source': source}, {'message': message})

class AvrHandler:

    def __init__(self, avr):
        self.avr = avr
        self.clients = set()
        self.task = None
        self.static_info = None

    async def add_client(self, ws, loop): #TODO: ugly loop parameter here...
        """ Adds a client to this avr handler. Updates from the avr will be sent over the given websocket to this client

        Keyword arguments:
        ws -- the client websocket connection
        """
        self.clients.add(ws)

        if len(self.clients) == 1:
            print('First client! Going to start avr handler')
            self.task = loop.create_task(self.avr_handler())
        else:
            await self.send_message(ws, self.static_info)

    async def remove_client(self, ws):
        """ Removes a client. Must be called when the client disconnected.

        Keyword arguments:
        ws -- the client websocket avr_connection
        """
        self.clients.remove(ws)

        if len(self.clients) == 0:
            print('No more clients. Stopping avr handler')
            self.task.cancel()

    async def send_message(self, ws, msg):
        """ Send an message to the clients

        Keyword arguments:
        ws -- the websocket over which to send the message
        msg -- the message to send. Must be an AvrMessage or subclass.
        """
        print('<< {0}'.format(msg))
        await ws.send_json(msg.to_dict())

    # The handler of the AVR. This one is listening for status updates of the avr.
    async def avr_handler(self):
        if not await self.avr.connected:
            await self.avr.connect()

        try:
            self.static_info = AvrStaticInfoMessage(await self.avr.static_info)
            for ws in self.clients:
                await self.send_message(ws, self.static_info)

            async for updates in self.avr.listen():
                print('In the async for loop', updates, datetime.datetime.now())
                for avr_update in updates:
                    for ws in self.clients:
                        await self.send_message(ws, AvrMessage.create(avr_update))
        except Exception:
            traceback.print_exc()
            raise
        finally:
            await self.avr.disconnect()

    # processes requests from the clients
    async def process_request(self, request):
        if request['type'] == 'zone':
            zoneId = request['zoneId']
            state = request['state']
            for key, value in state.items():
                avr_update = AvrZonePropertyUpdate(zoneId, key, value)
                await self.avr.send(avr_update)
        elif request['type'] == 'tuner': # TODO: make this generic for all internals
            internalId = request['internalId']
            if 'state' in request:
                state = request['state']
                for key, value in state.items():
                    avr_update = AvrTunerPropertyUpdate(internalId, key, value)
                    await self.avr.send(avr_update)
            if 'command' in request:
                command = request['command']
                arguments = request['arguments'] if 'arguments' in request else None
                await self.avr.executeInternalCommand(internalId, command, arguments)

    # The handler of the websocket. This one is listening for requests of the clients
    # When a request is received, most of the handling is passed over to the process_request method.
    async def websocket_handler(self, request):
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(request)
        client_id = request.transport.get_extra_info('peername')

        await self.add_client(ws, request.loop)
        print('Client {0} connected'.format(client_id))

        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    json = msg.json()
                    print('>> [{0}] {1}'.format(json['type'], json))
                    try:
                        await self.process_request(json)
                    except (UnsupportedUpdateException, AvrCommandError) as err:
                        traceback.print_exc()
                        await self.send_message(ws, AvrError('websocket_handler', err.message))
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print('ws connection closed with exception %s' % ws.exception())
        except Exception:
            traceback.print_exc()
            raise

        print('Client {0} disconnected: connection closed'.format(client_id))
        await self.remove_client(ws)
        return ws
