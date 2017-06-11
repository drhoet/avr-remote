import aiohttp
import importlib
import os
import json
import traceback

from .avr.base import AvrListener
from .default_config import default_config as config


class AvrHandler:

    def __init__(self, avr):
        self.avr = avr
        self.client_count = 0

    async def send_message(self, ws, type, props, state):
        msg = {'type': type, 'state': state}
        msg.update(props)
        print('<< [{0}] {1}'.format(type, msg))
        await ws.send_json(msg)

    # The handler of the AVR. This one is listening for status updates of the avr.
    async def avr_handler(self, ws):
        if not await self.avr.connected:
            await self.avr.connect()
        self.client_count = self.client_count + 1

        try:
            static_info = await self.avr.static_info
            await self.send_message(ws, 'static_info', {}, static_info)

            async for msg in self.avr.listen_for_updates(5):
                print('In the async for loop', msg)
                for zoneId, state in enumerate(msg):
                    await self.send_message(ws, 'zone', {'zoneId': zoneId}, state)
        finally:
            self.client_count = self.client_count - 1
            if self.client_count <= 0:
                await self.avr.disconnect()

    # processes requests from the clients
    async def process_request(self, request):
        if request['type'] == 'zone':
            zoneId = request['zoneId']
            state = request['state']
            if 'power' in state:
                self.avr.set_power(zoneId, state['power'])
            if 'volume' in state:
                self.avr.set_volume(zoneId, state['volume'])
            if 'input' in state:
                self.avr.select_input(zoneId, state['input'])

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
                    await self.process_request(json)
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

    avr_listener = AvrListener()
    avr_class = getattr(importlib.import_module(app['config']['avr_module']), app['config']['avr_class'])
    avr = avr_class(app['config']['avr_connection'], avr_listener)
    avr_handler = AvrHandler(avr)

    app.router.add_static('/static-new', 'avrremote/static-new')
    app.router.add_get('/ws', avr_handler.websocket_handler)

    aiohttp.web.run_app(app, host='0.0.0.0', port=5000)
