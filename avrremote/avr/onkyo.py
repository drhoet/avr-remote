from .base import AbstractAvr

import eiscp

class Onkyo(AbstractAvr):

	def __init__(self, config, listener):
		self.listener = listener
		self.ip = config['ip']
		self.zones = ['main', 'zone2']
		self.sources = [ ('BD/DVD', 'hdmi'), ('Tuner fm', 'radio'), ('Network', 'cloud'), ('Tuner am', 'radio'), ('STRM BOX', 'hdmi'), ('CBL/SAT', 'hdmi'), ('BLUETOOTH', 'bluetooth-audio'), ('PC', 'hdmi'), ('GAME', 'videogame'), ('AUX', 'hdmi'), ('CD', 'cd'), ('PHONO', 'hdmi'), ('TV', 'tv') ]
		self.source_real_names = [ ('dvd', 'BD/DVD'), ('fm', 'Tuner fm'), ('network', 'Network'), ('am', 'Tuner am'), ('strm-box', 'STRM BOX'), ('video2', 'CBL/SAT'), ('bluetooth', 'BLUETOOTH'), ('video6', 'PC'), ('video3', 'GAME'), ('video4', 'AUX'), ('cd', 'CD'), ('phono', 'PHONO'), ('tv', 'TV') ]
		self.source_ids = [x[0] for x in self.source_real_names]
			
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
		with eiscp.eISCP(self.ip) as receiver:
			return receiver.command('input-selector' if zoneId == 0 else 'selector', arguments=[self.source_real_names[inputId][0]], zone=self.zones[zoneId])