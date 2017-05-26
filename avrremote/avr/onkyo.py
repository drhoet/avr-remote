from .base import AbstractAvr

import eiscp

class Onkyo(AbstractAvr):

	def __init__(self, config, listener):
		self.listener = listener
		self.ip = config['ip']
		self.zones = ['main', 'zone2']
			
	@property
	def static_info(self):
		return { 'name': 'Onkyo', 'ip': self.ip, 'zones': self.zones, 'sources': [ 'CBL/SAT', 'DVD', 'Blu-Ray' ], 'volume_step': 1 }
	
	def get_power(self, zoneId):
		with eiscp.eISCP(self.ip) as receiver:
			resp = receiver.command('power', arguments=['query'], zone=self.zones[zoneId])
			return resp[1] == 'on'
	
	def set_power(self, zoneId, value):
		with eiscp.eISCP(self.ip) as receiver:
			resp = receiver.command('power', ['on' if value else 'standby'], zone=self.zones[zoneId])
			print(resp)
			return resp

	def get_volume(self, zoneId):
		with eiscp.eISCP(self.ip) as receiver:
			resp = receiver.command('volume', arguments=['query'], zone=self.zones[zoneId])
		return resp[1]	
	
	def set_volume(self, zoneId, value):
		with eiscp.eISCP(self.ip) as receiver:
			return receiver.command('volume', [str(value)], zone=self.zones[zoneId])
	
	def get_selected_input(self, zoneId):
		return 0;
	
	def select_input(self, zoneId, inputId):
		pass