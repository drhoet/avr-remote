from .base import AbstractAvr

import requests
from xml.etree import ElementTree

class Marantz(AbstractAvr):

	def __init__(self, config, listener):
		self.listener = listener
		self.config = config
		self.baseUri = 'http://{0}'.format(config['ip'])
		
	@property
	def static_info(self):
		return { 'name': 'Marantz NR1605', 'ip': self.config['ip'], 'zones': 2, 'sources': [ 'CBL/SAT', 'DVD', 'Blu-Ray' ] }
	
	def get_power(self, zoneId):
		status = self._post_app_command( 'GetAllZonePowerStatus' )
		root = ElementTree.fromstring( status )
		return root.findtext( 'cmd/zone' + str(zoneId + 1) ) == 'ON'
	
	def set_power(self, zoneId, value):
		self._get( '/goform/formiPhoneAppPower.xml?{0}+{1}'.format(zoneId + 1, 'PowerOn' if value else 'PowerStandby') )

	def get_volume(self, zoneId):
		status = self._post_app_command( 'GetVolumeLevel' )
		root = ElementTree.fromstring( status )
		return float(root.findtext( 'cmd/volume' )) + 80
	
	def set_volume(self, zoneId, value):
		if value > 98:
			value = 98
		elif value < 0:
			value = 0
		
		volume = value - 80
		self._get( '/goform/formiPhoneAppVolume.xml?{0}+{2:0{1}.1f}'.format(zoneId + 1, 4 if volume >= 0 else 5, volume) )
	
	def _get(self, path):
		print(self.baseUri + path)
		return requests.get( self.baseUri + path ).text
	
	def _post_app_command(self, command):
		xml = """<?xml version="1.0" encoding="utf-8"?>
<tx>
 <cmd id="1">{0}</cmd>
</tx>
		""".format(command)
		headers = {'Content-Type': 'text/xml'}
		return requests.post( self.baseUri + '/goform/AppCommand.xml', data = xml, headers = headers).text