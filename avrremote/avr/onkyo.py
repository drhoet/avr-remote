from .base import AbstractAvr, AbstractEndpoint, AvrZonePropertyUpdate, AvrTunerPropertyUpdate, UnsupportedUpdateException

import asyncio
import eiscp

class Zone(AbstractEndpoint):

    def __init__(self, avr, zoneId, name, inputs):
        super().__init__(avr)
        self.zoneId = zoneId
        self.name = name
        self.inputs = inputs
        self._register_property('volume', self.set_volume)
        self._register_property('power', self.set_power)
        self._register_property('input', self.select_input)
        self._register_property('mute', self.mute)

    def create_property_update(self, property_name, property_value):
        return AvrZonePropertyUpdate(self.zoneId, property_name, property_value)

    async def poll(self):
        """ Updates the state by polling the AVR and returns a list of changed properties """
        with eiscp.eISCP(self.avr.ip) as receiver:
            resp = receiver.command('power', arguments=['query'], zone=self.name)
            power = resp[1] == 'on'

            resp = receiver.command('volume', arguments=['query'], zone=self.name)
            volume = float(0 if resp[1] == 'N/A' else resp[1])

            resp = receiver.command('input-selector' if self.zoneId == 0 else 'selector', arguments=['query'], zone=self.name)
            inputid = resp[1][0] if isinstance(resp[1], tuple) else resp[1]
            selected_input = self.avr.input_ids.index(inputid)

        result = [
            self._property_updated('power', power),
            self._property_updated('input', selected_input),
            self._property_updated('volume', volume),
            self._property_updated('mute', False)
        ]
        return filter(None, result)

    async def set_power(self, value):
        with eiscp.eISCP(self.avr.ip) as receiver:
            receiver.command('power', ['on' if value else 'standby'], zone=self.name)
        return True if value else False

    async def set_volume(self, value):
        with eiscp.eISCP(self.avr.ip) as receiver:
            receiver.command('volume', [str(value)], zone=self.name)
        return value

    async def select_input(self, inputId):
        with eiscp.eISCP(self.avr.ip) as receiver:
            (receiver.raw('SLI12' if self.zoneId == 0 else 'SLZ12')) if self.avr.input_real_names[inputId][0] == 'tv' else (receiver.command('input-selector' if self.zoneId == 0 else 'selector', arguments=[self.avr.input_real_names[inputId][0]], zone=self.name))
        return inputId

    async def mute(self, value):
        return True


class Tuner(AbstractEndpoint):

    def __init__(self, avr, internalId):
        super().__init__(avr)
        self.internalId = internalId
        self._register_property('band', self.set_band)
        self._register_property('freq', self.set_freq)

    def create_property_update(self, property_name, property_value):
        return AvrTunerPropertyUpdate(self.internalId, property_name, property_value)

    async def poll(self):
        """ Polls the state of the AVR and returns a list of changed properties """
        with eiscp.eISCP(self.avr.ip) as receiver:
            resp = receiver.raw('TUNQSTN')
            freq = int(resp[3:])/100

        result = [
            self._property_updated('band', 'FM'),
            self._property_updated('freq', freq),
        ]
        return filter(None, result)

    async def set_band(self, value):
        return 'FM'

    async def set_freq(self, value):
        with eiscp.eISCP(self.avr.ip) as receiver:
            resp = receiver.raw('TUN' + '{0:05.0f}'.format(value*100))
        return value


class Onkyo(AbstractAvr):

    def __init__(self, config):
        self.ip = config['ip']
        self.inputs = [ ('BD/DVD', 'hdmi'), ('Tuner fm', 'radio'), ('Network', 'cloud'), ('Tuner am', 'radio'), ('STRM BOX', 'hdmi'), ('CBL/SAT', 'hdmi'), ('BLUETOOTH', 'bluetooth-audio'), ('PC', 'hdmi'), ('GAME', 'videogame'), ('AUX', 'hdmi'), ('CD', 'cd'), ('PHONO', 'hdmi'), ('TV', 'tv') ]
        self.input_real_names = [ ('dvd', 'BD/DVD'), ('fm', 'Tuner fm'), ('network', 'Network'), ('am', 'Tuner am'), ('strm-box', 'STRM BOX'), ('video2', 'CBL/SAT'), ('bluetooth', 'BLUETOOTH'), ('video6', 'PC'), ('video3', 'GAME'), ('video4', 'AUX'), ('cd', 'CD'), ('phono', 'PHONO'), ('tv', 'TV') ]
        self.input_ids = [x[0] for x in self.input_real_names]
        self.zones = [Zone(self, 0, 'main', self.inputs), Zone(self, 1, 'zone2', self.inputs)]
        self.internals = [Tuner(self, 0)]

    @property
    async def connected(self):
        return True

    async def connect(self):
        pass

    async def disconnect(self):
        pass

    @property
    async def static_info(self):
        augmented_zones = [{'name': z.name, 'inputs': z.inputs} for z in self.zones]
        return { 'name': 'Onkyo', 'ip': self.ip, 'zones': augmented_zones, 'volume_step': 1, 'internals': [('tuner', 'radio')]}

    async def listen(self):
        print('listen_for_updates')
        while True:
            all_updates = await asyncio.gather(*[ zone.poll() for zone in self.zones ], *[ internal.poll() for internal in self.internals ])
            flattened_updates = [update for updates in all_updates for update in updates]
            yield flattened_updates
            await asyncio.sleep(5)

    async def send(self, avr_update):
        if isinstance(avr_update, AvrZonePropertyUpdate):
            await self.zones[avr_update.zoneId].send(avr_update)
        elif isinstance(avr_update, AvrTunerPropertyUpdate):
            await self.internals[avr_update.internalId].send(avr_update)
        else:
            raise UnsupportedUpdateException('Update type {} not supported'.format(avr_update.__class__.__name__), avr_update)

    def get_preset(self, zoneId):
        with eiscp.eISCP(self.ip) as receiver:
            return receiver.command('preset', arguments=['query'], zone=self.zones[zoneId])

    def set_selected_preset(self, zoneId, preset):
        with eiscp.eISCP(self.ip) as receiver:
            return receiver.command('preset', [preset], zone=self.zones[zoneId])

    def set_selected_preset_memory(self, zoneId, preset):
        with eiscp.eISCP(self.ip) as receiver:
            return receiver.raw('PRM' + '{0:02x}'.format(preset))
