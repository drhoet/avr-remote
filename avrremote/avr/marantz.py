from .base import AbstractAvr

import requests
from xml.etree import ElementTree

class Marantz(AbstractAvr):

	def __init__(self, config, listener):
		self.listener = listener
		self.baseUri = 'http://{0}/'.format(config['ip'])

	def get_volume(self):
		status = self._post_app_command( 'GetVolumeLevel' )
		root = ElementTree.fromstring( status )
		return float(root.findtext( 'cmd/volume' )) + 80
	
	def set_volume(self, value):
		if value > 98:
			value = 98
		elif value < 0:
			value = 0
		
		volume = value - 80
		self._get( '/goform/formiPhoneAppVolume.xml?1+{1:0{0}.1f}'.format(4 if volume >= 0 else 5, volume) )
	
	def _get(self, path):
		return requests.get( self.baseUri + path ).text
	
	def _post_app_command(self, command):
		xml = """<?xml version="1.0" encoding="utf-8"?>
<tx>
 <cmd id="1">{0}</cmd>
</tx>
		""".format(command)
		headers = {'Content-Type': 'text/xml'}
		return requests.post( self.baseUri + '/goform/AppCommand.xml', data = xml, headers = headers).text