import sys
if sys.version_info < (3,6):
    print("This script requires Python version >= 3.6")
    sys.exit(1)

import aiohttp.web
import importlib
import os
import json
import argparse

from avrremote.default_config import default_config as config
from avrremote.main import AvrHandler

def create_backend(config_file=None):
    if config_file is None:
        # try the env variable as a backup
        config_file = os.getenv('AVRREMOTE_SETTINGS', None)
    if config_file is not None:
        with open(config_file) as f:
            config.update(json.load(f))

    avr_class = getattr(importlib.import_module(config['avr_module']), config['avr_class'])
    avr = avr_class(config['avr_connection'])
    return AvrHandler(avr)

def create_app(loop):
    """ Entry point used by the developer tools of asyncio. """
    avr_handler = create_backend()

    app = aiohttp.web.Application()
    app['config'] = config

    app.router.add_static('/static', 'avrremote/static')
    app.router.add_get('/ws', avr_handler.websocket_handler)
    aiohttp.web.run_app(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--socket-activation', action="store_true", help="Use the port number assigned by systemd socket activation")
    parser.add_argument('--config-file', help="Specify the config file to use. If not specified, will check if a config file path is defined in environment variable AVRREMOTE_SETTINGS. If also this is not specified, the default configuration is used.")
    parser.add_argument('--port', type=int, default=8080, help="The port to listen on (8080 if omitted). Ignored when --socket-activation is specified.")
    parser.add_argument('--host', default='127.0.0.1', help="The IP address to listen on (127.0.0.1 if omitted). Ignored when --socket-activation is specified.")
    parser.add_argument('--serve-static', '--static', action='store_true', help='Serve the static content on /static. You should be using some web server to do this.')

    args = parser.parse_args()

    avr_handler = create_backend(args.config_file)

    app = aiohttp.web.Application()
    app['config'] = config
    app.router.add_get('/ws', avr_handler.websocket_handler)
    if args.serve_static:
        app.router.add_static('/static', 'avrremote/static')

    if args.socket_activation:
        if os.environ.get('LISTEN_PID', None) == str(os.getpid()):
            import socket
            # systemd will give us a socket at fd = 3
            sock = socket.fromfd(3, socket.AF_UNIX, socket.SOCK_STREAM)
            aiohttp.web.run_app(app, sock=sock)
        else:
            print('No socket received from systemd. Are you using socket activation?')
    else:
        aiohttp.web.run_app(app, host=args.host, port=args.port)
