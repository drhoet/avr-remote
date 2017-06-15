from .base import AbstractAvr, AvrZonePropertyUpdate

import asyncio
import eiscp

class Zone():

    def __init__(self, avr, zoneId, name, inputs):
        self.avr = avr
        self.zoneId = zoneId
        self.name = name
        self.inputs = inputs
        self.props = {
            'volume': None,
            'power': None,
            'input': None,
            'mute': None
        }

    def _update_prop(self, name, value):
        if self.props[name] != value:
            self.props[name] = value
            return AvrZonePropertyUpdate(self.zoneId, name, value)

    async def update(self):
        """ Updates the state by polling the AVR and returns a list of changed properties """
        result = [
            self._update_prop('power', self.get_power()),
            self._update_prop('input', self.get_selected_input()),
            self._update_prop('volume', self.get_volume()),
            self._update_prop('mute', False)
        ]
        return filter(None, result)

    def get_power(self):
        with eiscp.eISCP(self.avr.ip) as receiver:
            resp = receiver.command('power', arguments=['query'], zone=self.name)
            return resp[1] == 'on'

    def get_volume(self):
        with eiscp.eISCP(self.avr.ip) as receiver:
            resp = receiver.command('volume', arguments=['query'], zone=self.name)
        return float(resp[1])

    def get_selected_input(self):
        with eiscp.eISCP(self.avr.ip) as receiver:
            resp = receiver.command('input-selector' if zoneId == 0 else 'selector', arguments=['query'], zone=self.name)
            inputid = resp[1][0] if isinstance(resp[1], tuple) else resp[1]
            return self.avr.input_ids.index(inputid)


class Onkyo(AbstractAvr):

    def __init__(self, config):
        self.ip = config['ip']
        self.inputs = [ ('BD/DVD', 'hdmi'), ('Tuner fm', 'radio'), ('Network', 'cloud'), ('Tuner am', 'radio'), ('STRM BOX', 'hdmi'), ('CBL/SAT', 'hdmi'), ('BLUETOOTH', 'bluetooth-audio'), ('PC', 'hdmi'), ('GAME', 'videogame'), ('AUX', 'hdmi'), ('CD', 'cd'), ('PHONO', 'hdmi'), ('TV', 'tv') ]
        self.input_real_names = [ ('dvd', 'BD/DVD'), ('fm', 'Tuner fm'), ('network', 'Network'), ('am', 'Tuner am'), ('strm-box', 'STRM BOX'), ('video2', 'CBL/SAT'), ('bluetooth', 'BLUETOOTH'), ('video6', 'PC'), ('video3', 'GAME'), ('video4', 'AUX'), ('cd', 'CD'), ('phono', 'PHONO'), ('tv', 'TV') ]
        self.input_ids = [x[0] for x in self.input_real_names]
        self.zones = [Zone(self, 0, 'main', self.inputs), Zone(self, 1, 'zone2', self.inputs)]

    @property
    async def connected(self):
        return True

    async def connect(self):
        pass

    async def disconnect():
        pass

    @property
    async def static_info(self):
        augmented_zones = [{'name': z.name, 'inputs': z.inputs} for z in self.zones]
        return { 'name': 'Onkyo', 'ip': self.ip, 'zones': augmented_zones, 'volume_step': 1, 'internals': {}}

    async def listen_for_updates(self):
        print('listen_for_updates')
        while True:
            all_zone_updates = await asyncio.gather(*[ zone.update() for zone in self.zones ])
            flattened_updates = [zone_update for zone_updates in all_zone_updates for zone_update in zone_updates]
            yield flattened_updates
            await asyncio.sleep(5)

    async def set_power(self, zoneId, value):
        with eiscp.eISCP(self.ip) as receiver:
            resp = receiver.command('power', ['on' if value else 'standby'], zone=self.zones[zoneId].name)
            return resp

    def set_volume(self, zoneId, value):
        with eiscp.eISCP(self.ip) as receiver:
            return receiver.command('volume', [str(value)], zone=self.zones[zoneId].name)

    def select_input(self, zoneId, inputId):
        with eiscp.eISCP(self.ip) as receiver:
            resp = (receiver.raw('SLI12' if zoneId == 0 else 'SLZ12')) if self.input_real_names[inputId][0] == 'tv' else (receiver.command('input-selector' if zoneId == 0 else 'selector', arguments=[self.input_real_names[inputId][0]], zone=self.zones[zoneId].name))
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
