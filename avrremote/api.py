from flask import jsonify
from . import app, avr

@app.route('/api/v1.0/volume', methods=['GET'])
def get_volume():
	return jsonify({ 'value': avr.get_volume() })

@app.route('/api/v1.0/volume', methods=['POST'])
def set_volume():
	avr.set_volume( request.get_json()['value'] )
	return ('', 202)