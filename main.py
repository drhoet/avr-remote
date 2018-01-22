import sys
if sys.version_info < (3,6):
    print("This script requires Python version >= 3.6")
    sys.exit(1)

import os
import json
import argparse

from avrremote.default_config import default_config as config
from avrremote.server import Server

def _load_config(config_file=None):
    if config_file is None:
        # try the env variable as a fallback
        config_file = os.getenv('AVRREMOTE_SETTINGS', None)
    if config_file is not None:
        with open(config_file) as f:
            config.update(json.load(f))

def create_app(loop):
    """ Entry point used by the developer tools of asyncio. """
    _load_config()
    server = Server('0.0.0.0', 5000, config, serve_static=True)
    server.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--socket-activation', action="store_true", help="Use the port number assigned by systemd socket activation")
    parser.add_argument('--config-file', help="Specify the config file to use. If not specified, will check if a config file path is defined in environment variable AVRREMOTE_SETTINGS. If also this is not specified, the default configuration is used.")
    parser.add_argument('--port', type=int, default=8080, help="The port to listen on (8080 if omitted). Ignored when --socket-activation is specified.")
    parser.add_argument('--host', default='127.0.0.1', help="The IP address to listen on (127.0.0.1 if omitted). Ignored when --socket-activation is specified.")
    parser.add_argument('--serve-static', '--static', action='store_true', help='Serve the static content on /static. You should be using some web server to do this.')

    args = parser.parse_args()

    _load_config(args.config_file)
    server = Server(args.host, args.port, config, socket_activation=args.socket_activation, serve_static=args.serve_static)
    server.start()
