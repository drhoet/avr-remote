import sys
import importlib

from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object( 'avrremote.default_config' )
app.config.from_envvar( 'AVRREMOTE_SETTINGS' )

avr_class = getattr( importlib.import_module( app.config['AVR_MODULE'] ), app.config['AVR_CLASS'] )
avr = avr_class()

from . import api

@app.route('/')
def index():
	return render_template('index.html')