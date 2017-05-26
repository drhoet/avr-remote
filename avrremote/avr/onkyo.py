from .base import AbstractAvr

import eiscp

class Onkyo(AbstractAvr):

	def __init__(self, config, listener):
		self.listener = listener
		self.ip = config['ip']
		self.zones = ['main', 'zone2']
		self.sources = [ ('dvd', 'hdmi'), ('fm', 'radio'), ('network', 'cloud'), ('am', 'radio'), ('strm-box', 'hdmi'), ('video2', 'hdmi'), ('bluetooth', 'bluetooth_audio') ]
		self.source_ids = [x[0] for x in self.sources]
			
	@property
	def static_info(self):
		return { 'name': 'Onkyo', 'ip': self.ip, 'zones': self.zones, 'sources': self.sources , 'volume_step': 1 }
	
	def get_power(self, zoneId):
		with eiscp.eISCP(self.ip) as receiver:
			resp = receiver.command('power', arguments=['query'], zone=self.zones[zoneId])
			return resp[1] == 'on'
	
	def set_power(self, zoneId, value):
		with eiscp.eISCP(self.ip) as receiver:
			resp = receiver.command('power', ['on' if value else 'standby'], zone=self.zones[zoneId])
			return resp

	def get_volume(self, zoneId):
		with eiscp.eISCP(self.ip) as receiver:
			resp = receiver.command('volume', arguments=['query'], zone=self.zones[zoneId])
		return resp[1]	
	
	def set_volume(self, zoneId, value):
		with eiscp.eISCP(self.ip) as receiver:
			return receiver.command('volume', [str(value)], zone=self.zones[zoneId])
	
	def get_selected_input(self, zoneId):
		with eiscp.eISCP(self.ip) as receiver:
			resp = receiver.command('input-selector' if zoneId == 0 else 'selector', arguments=['query'], zone=self.zones[zoneId])
			sourceid = resp[1][0] if isinstance(resp[1], tuple) else resp[1]
		return self.source_ids.index(sourceid)
	
	def select_input(self, zoneId, inputId):
		pass