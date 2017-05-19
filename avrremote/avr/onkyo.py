from .base import AbstractAvr

import eiscp

class Onkyo(AbstractAvr):

	def __init__(self, config, listener):
		self.listener = listener
		self.ip = config['ip']
		
	@property
	def static_info(self):
		return { 'name': 'Onkyo', 'ip': self.config['ip'], 'zones': 2, 'sources': [ 'CBL/SAT', 'DVD', 'Blu-Ray' ] }
	
	def get_power(self, zoneId):
		with eiscp.eISCP(self.ip) as receiver:
			return receiver.command('power query')
	
	def set_power(self, zoneId, value):
		with eiscp.eISCP(self.ip) as receiver:
			return receiver.command('power on' if value else 'power off' )

	def get_volume(self, zoneId):
		return 20
	
	def set_volume(self, zoneId, value):
		with eiscp.eISCP(self.ip) as receiver:
			return receiver.raw('MVL' + str(value))