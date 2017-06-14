from .base import AbstractAvr

import eiscp

class Onkyo(AbstractAvr):

	def __init__(self, config, listener):
		self.listener = listener
		self.ip = config['ip']
		self.zones = ['main', 'zone2']
		self.inputs = [ ('BD/DVD', 'hdmi'), ('Tuner fm', 'radio'), ('Network', 'cloud'), ('Tuner am', 'radio'), ('STRM BOX', 'hdmi'), ('CBL/SAT', 'hdmi'), ('BLUETOOTH', 'bluetooth-audio'), ('PC', 'hdmi'), ('GAME', 'videogame'), ('AUX', 'hdmi'), ('CD', 'cd'), ('PHONO', 'hdmi'), ('TV', 'tv') ]
		self.input_real_names = [ ('dvd', 'BD/DVD'), ('fm', 'Tuner fm'), ('network', 'Network'), ('am', 'Tuner am'), ('strm-box', 'STRM BOX'), ('video2', 'CBL/SAT'), ('bluetooth', 'BLUETOOTH'), ('video6', 'PC'), ('video3', 'GAME'), ('video4', 'AUX'), ('cd', 'CD'), ('phono', 'PHONO'), ('tv', 'TV') ]
		self.input_ids = [x[0] for x in self.input_real_names]

	@property
	async def connected(self):
		return True

	async def connect(self):
		pass

	async def disconnect():
		pass

	@property
	async def static_info(self):
		augmented_zones = [{'name': z, 'inputs': self.inputs} for z in self.zones]
		return { 'name': 'Onkyo', 'ip': self.ip, 'zones': augmented_zones, 'inputs': self.inputs , 'volume_step': 1 }

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
			inputid = resp[1][0] if isinstance(resp[1], tuple) else resp[1]
		return self.input_ids.index(inputid)

	def select_input(self, zoneId, inputId):
		with eiscp.eISCP(self.ip) as receiver:
			resp = (receiver.raw('SLI12' if zoneId == 0 else 'SLZ12')) if self.input_real_names[inputId][0] == 'tv' else (receiver.command('input-selector' if zoneId == 0 else 'selector', arguments=[self.input_real_names[inputId][0]], zone=self.zones[zoneId]))
			return resp

	def get_tuning_freq(self, zoneId):
		with eiscp.eISCP(self.ip) as receiver:
			resp = receiver.raw('TUNQSTN')
			return int(resp[3:])/100

	def set_tuning_freq(self, zoneId, freq):
		with eiscp.eISCP(self.ip) as receiver:
			resp = receiver.raw('TUN' + '{0:05.0f}'.format(freq))
			return resp

	def get_preset(self, zoneId):
		with eiscp.eISCP(self.ip) as receiver:
			return receiver.command('preset', arguments=['query'], zone=self.zones[zoneId])

	def set_selected_preset(self, zoneId, preset):
		with eiscp.eISCP(self.ip) as receiver:
			return receiver.command('preset', [preset], zone=self.zones[zoneId])

	def set_selected_preset_memory(self, zoneId, preset):
		with eiscp.eISCP(self.ip) as receiver:
			return receiver.raw('PRM' + '{0:02x}'.format(preset))
