from abc import ABCMeta, abstractmethod

import aiohttp
import json
import traceback
import datetime
import aiohttp.web
import importlib

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

class AvrListener(metaclass=ABCMeta):
    @abstractmethod
    async def on_update(self, msg):
        pass

class AvrMultiplexer:
    """ This class is responsible for handling the complexity of having multiple clients to one avr.
    It makes sure that all listeners get all information, and the all listeners can send information to the one avr.
    """
    def __init__(self, avr):
        self.avr = avr
        self.static_info = None
        self.listeners = set()

    async def run(self):
        """ Start listening to the AVR and send status updates to the listener. """
        await self.avr.connect()
        self.static_info = AvrStaticInfoMessage(await self.avr.static_info)

        try:
            await self._notify_listeners(self.static_info)
            async for updates in self.avr.listen():
                print('In the async for loop', updates, datetime.datetime.now())
                for avr_update in updates:
                    await self._notify_listeners(AvrMessage.create(avr_update))
        except Exception:
            traceback.print_exc()
            raise
        finally:
            await self.avr.disconnect()

    async def send_update(self, update):
        await self.avr.send(update)

    async def executeInternalCommand(self, internalId, command, arguments):
        await self.avr.executeInternalCommand(internalId, command, arguments)

    async def register_listener(self, listener):
        if self.static_info is not None: # if this is None, we are not connected yet and will send the info in run()
            await listener.on_update(self.static_info)
        self.listeners.add(listener)

    async def unregister_listener(self, listener):
        self.listeners.remove(listener)

    async def _notify_listeners(self, msg):
        for listener in self.listeners:
            await listener.on_update(msg)


class Client(AvrListener):
    def __init__(self, client_id, ws, avr_multiplexer):
        self.client_id = client_id
        self.ws = ws
        self.avr_multiplexer = avr_multiplexer

    async def on_update(self, msg):
        """ Send an message to the client

        Keyword arguments:
        ws -- the websocket over which to send the message
        msg -- the message to send. Must be an AvrMessage or subclass.
        """
        print('<< [Client{0}] {1}'.format(self.client_id, msg))
        await self.ws.send_json(msg.to_dict())

    async def listen(self):
        """ Listens to the client, processing its requests, until the connection is closed. """
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    json = msg.json()
                    print('>> [{0}] {1}'.format(json['type'], json))
                    try:
                        await self.process_request(json)
                    except (UnsupportedUpdateException, AvrCommandError) as err:
                        traceback.print_exc()
                        await self.send_message(AvrError('websocket_handler', err.message))
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print('ws connection closed with exception %s' % self.ws.exception())
        except Exception:
            traceback.print_exc()
            raise

    async def process_request(self, request):
        """ Processes one request from the client. """
        if request['type'] == 'zone':
            zoneId = request['zoneId']
            state = request['state']
            for key, value in state.items():
                avr_update = AvrZonePropertyUpdate(zoneId, key, value)
                await self.avr_multiplexer.send_update(avr_update)
        elif request['type'] == 'tuner': # TODO: make this generic for all internals
            internalId = request['internalId']
            if 'state' in request:
                state = request['state']
                for key, value in state.items():
                    avr_update = AvrTunerPropertyUpdate(internalId, key, value)
                    await self.avr_multiplexer.send_update(avr_update)
            if 'command' in request:
                command = request['command']
                arguments = request['arguments'] if 'arguments' in request else None
                await self.avr_multiplexer.executeInternalCommand(internalId, command, arguments)


class Server:
    def __init__(self, host, port, avr_config, socket_activation=False, serve_static=False):
        """ Creates a new server, listening on /ws for websocket connections from clients.

        host -- the host ip to listen on (ignored if socket_activation==True)
        port -- the port to listen on (ignored if socket_activation==True)
        avr_config -- the configuration of the AVR
        socket_activation -- set to true to use systemd socket activation
        serve_static -- set to True to serve the static content
        """
        self.host = host
        self.port = port
        self.socket_activation = socket_activation

        avr_class = getattr(importlib.import_module(avr_config['avr_module']), avr_config['avr_class'])
        avr = avr_class(avr_config['avr_connection'])
        self.avr_multiplexer = AvrMultiplexer(avr)

        self.app = aiohttp.web.Application()
        self.app['config'] = avr_config

        if serve_static:
            self.app.router.add_static('/static', 'avrremote/static')
        self.app.router.add_get('/ws', self.websocket_handler)

        self.task = None
        self.client_count = 0

    def start(self):
        if self.socket_activation:
            if os.environ.get('LISTEN_PID', None) == str(os.getpid()):
                import socket
                # systemd will give us a socket at fd = 3
                sock = socket.fromfd(3, socket.AF_UNIX, socket.SOCK_STREAM)
                aiohttp.web.run_app(self.app, sock=sock)
            else:
                print('No socket received from systemd. Are you using socket activation?')
        else:
            aiohttp.web.run_app(self.app, host=self.host, port=self.port)

    async def websocket_handler(self, request):
        """ The handler of the websocket. This one is listening for requests of the clients
        When a request is received, most of the handling is passed over to the process_request method.
        """
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(request)
        client_id = request.transport.get_extra_info('peername')
        client = Client(client_id, ws, self.avr_multiplexer)

        await self._add_client(client)
        print('Client {0} connected'.format(client_id))

        await client.listen()

        print('Client {0} disconnected: connection closed'.format(client_id))
        await self._remove_client(client)
        return ws

    async def _add_client(self, client):
        await self.avr_multiplexer.register_listener(client)

        if self.client_count == 0:
            print('First client! Going to start avr handler')
            self.task = self.app.loop.create_task(self.avr_multiplexer.run())

        self.client_count += 1

    async def _remove_client(self, client):
        self.client_count -= 1

        if self.client_count == 0:
            print('No more clients. Stopping avr handler')
            self.task.cancel()
            self.task = None
        await self.avr_multiplexer.unregister_listener(client)
