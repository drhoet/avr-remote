from flask import jsonify, request
from . import app, avr

@app.route('/api/v1.0/status', methods=['GET'])
def status():
	return jsonify( avr.status )

@app.route('/api/v1.0/zone/<int:zoneId>/power', methods=['PUT'])
def set_power(zoneId):
	avr.set_power( zoneId, request.get_json()['value'] )
	return ('', 202)

@app.route('/api/v1.0/zone/<int:zoneId>/volume', methods=['PUT'])
def set_volume(zoneId):
	avr.set_volume( zoneId, request.get_json()['value'] )
	return ('', 202)