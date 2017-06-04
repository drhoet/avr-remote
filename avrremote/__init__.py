import sys
import importlib

from flask import Flask, render_template, send_from_directory
from .avr.base import AvrListener

app = Flask(__name__)
app.config.from_object( 'avrremote.default_config' )
app.config.from_envvar( 'AVRREMOTE_SETTINGS' )

avr_listener = AvrListener()
avr_class = getattr( importlib.import_module( app.config['AVR_MODULE'] ), app.config['AVR_CLASS'] )
avr = avr_class( app.config['AVR_CONNECTION'], avr_listener )

from . import api

@app.route('/') 
def index(): 
  return render_template('index.html', status = avr.status, static_info = avr.static_info, config = app.config)

@app.route('/static-new/<path:filename>')
def base_static(filename):
	return send_from_directory(app.root_path + '/static-new/', filename)