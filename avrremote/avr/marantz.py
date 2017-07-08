from .base import AbstractAvr, AbstractEndpoint, AvrZonePropertyUpdate, AvrTunerPropertyUpdate, UnsupportedUpdateException, AvrCommandError

import asyncio
import aiohttp
import requests
import traceback
from xml.etree import ElementTree


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
        """ Polls the state of the AVR and returns a list of changed properties """
        if(self.zoneId == 0):
            data = await self.avr._get('/goform/formMainZone_MainZoneXmlStatusLite.xml')
        else:
            data = await self.avr._get('/goform/formZone{0}_Zone{0}XmlStatusLite.xml'.format(self.zoneId + 1))
        xml = ElementTree.fromstring(data)

        result = [
            self._property_updated('power', xml.findtext('Power/value') == 'ON'),
            self._property_updated('input', self.avr._map_input(xml.findtext('InputFuncSelect/value'))),
            self._property_updated('volume', float(xml.findtext('MasterVolume/value')) + 80),
            self._property_updated('mute', xml.findtext('Mute/value') == 'on')
        ]
        return filter(None, result)

    async def set_power(self, value):
        await self.avr._get('/goform/formiPhoneAppPower.xml?{0}+{1}'.format(self.zoneId + 1, 'PowerOn' if value else 'PowerStandby'))
        return True if value else False

    async def set_volume(self, value):
        if value > 98:
            value = 98
        elif value < 0:
            value = 0

        volume = value - 80
        await self.avr._get('/goform/formiPhoneAppVolume.xml?{0}+{2:0{1}.1f}'.format(self.zoneId + 1, 4 if volume >= 0 else 5, volume))
        return value

    async def select_input(self, inputId):
        await self.avr._get('/goform/formiPhoneAppDirect.xml?{0}{1}'.format('SI' if self.zoneId == 0 else 'Z{0}'.format(self.zoneId + 1), self.avr.input_ids[inputId]))
        return inputId

    async def mute(self, value):
        await self.avr._get('/goform/formiPhoneAppMute.xml?{0}+{1}'.format(self.zoneId + 1, 'MuteOn' if value else 'MuteOff'))
        return True if value else False


class Tuner(AbstractEndpoint):

    def __init__(self, avr, internalId):
        super().__init__(avr)
        self.internalId = internalId
        self._register_property('band', self.set_band)
        self._register_property('freq', self.set_freq)
        self._register_command('seekUp', self.seek_up)
        self._register_command('seekDown', self.seek_down)

        self._register_property('selectedPreset', self.select_preset)
        self._register_property('presets', None)
        self._register_property('presetCount', None)
        self._register_command('savePreset', self.save_preset)

    def create_property_update(self, property_name, property_value):
        return AvrTunerPropertyUpdate(self.internalId, property_name, property_value)

    def _parse_raw_presets(self, raw_presets):
        for index, preset in enumerate(raw_presets):
            text = preset.get('param', '')
            name = text[:8].strip()
            if name != '':
                freq = float(text[-6:]) / 100
                band = 'AM' if freq > 500.00 else 'FM'
                yield {'index': float(preset.get('index')), 'name': name, 'freq': freq, 'band': band}

    async def poll(self):
        """ Polls the state of the AVR and returns a list of changed properties """
        data = await self.avr._get('/goform/formTuner_TunerXml.xml')
        xml = ElementTree.fromstring(data)

        band = xml.findtext('Band/value')
        if band == '': # sometimes, this value is empty. Posting the app command GetTunerStatus seems to fix it
            cmds = await self.avr._post_app_command('GetTunerStatus')
            data = await self.avr._get('/goform/formTuner_TunerXml.xml')
            xml = ElementTree.fromstring(data)
            band = xml.findtext('Band/value')

        freq = float(xml.findtext('Frequency/value'))
        raw_presets = [preset for preset in xml.iterfind('PresetLists/value') if preset.get('index', '0') != '0']
        presets = [p for p in self._parse_raw_presets(raw_presets)]
        selected_preset = next((preset['index'] for preset in presets if preset['freq']==freq), -1)
        preset_count = len(raw_presets)

        result = [
            self._property_updated('band', band),
            self._property_updated('freq', freq),
            self._property_updated('selectedPreset', selected_preset),
            self._property_updated('presets', presets),
            self._property_updated('presetCount', preset_count)
        ]
        return filter(None, result)

    async def set_band(self, value):
        if value == 'AM':
            band = 'AM'
        else:
            band = 'FM'
        await self.avr._get('/goform/formiPhoneAppDirect.xml?TMAN{0}'.format(band))
        return band

    async def set_freq(self, value):
        freq_str = '{0:06.0f}'.format(100 * value)
        await self.avr._get('/goform/formiPhoneAppDirect.xml?TFAN{0}'.format(freq_str))
        return value

    async def seek_up(self, _):
        await self.avr._get('/goform/formiPhoneAppDirect.xml?TFANUP')

    async def seek_down(self, _):
        await self.avr._get('/goform/formiPhoneAppDirect.xml?TFANDOWN')

    async def select_preset(self, preset):
        await self.avr._get('/goform/formiPhoneAppDirect.xml?TPAN{0:02d}'.format(preset))

    async def save_preset(self, arguments):
        if len(arguments) == 2 and arguments[0] >= 1 and arguments[0] <= 56 and isinstance(arguments[1], str):
            index = arguments[0]
            name = arguments[1][:8]
            freq = self._property_value('freq')
            await self.avr._post('/Tuner/TunerPreset/sendS-3_4_1.asp', {
                'textPresetName{0:02d}'.format(index): name,
                'setPresetName{0:02d}'.format(index): 'on',
                'listPresetCh': '{0:02d}'.format(index),
                'listPresetFreq{0:02d}'.format(index): '{0:06.0f}'.format(100 * freq)
            } )
        else:
            raise AvrCommandError('Invalid arguments: must be 1. int [1..56] 2. string', 'savePreset', arguments, None)


class Marantz(AbstractAvr):

    INPUT_NAME_TO_ID_MAPPING = {
        # name : input_id mapping
        'AUX': 'AUX1',
        'AUX1': 'AUX1',
        'AUX2': 'AUX2',
        'AUX3': 'AUX3',
        'AUX4': 'AUX4',
        'AUX5': 'AUX5',
        'AUX6': 'AUX6',
        'AUX7': 'AUX7',
        'BLUETOOTH': 'BT',
        'BLU-RAY': 'BD',
        'CBL/SAT': 'SAT/CBL',
        'SAT': 'SAT',
        'CD': 'CD',
        'DVD/BLU-RAY': 'DVD',
        'DVD': 'DVD',
        'GAME': 'GAME',
        'HD RADIO': 'HDRADIO',
        'IPOD/USB': 'USB/IPOD',
        'MEDIA PLAYER': 'MPLAY',
        'NETWORK': 'NET',
        'PHONO': 'PHONO',
        'TUNER': 'TUNER',
        'TV AUDIO': 'TV',
        'SPOTIFYCONNECT': 'SPOTIFY',  # Virtual input --> NET?
        'VCR': 'VCR',  # from xls
        'V.AUX': 'V.AUX',  # from xls
        'SIRIUS': 'SIRIUS',  # from xls
        'SIRIUSXM': 'SIRIUSXM',  # from xls
        'RHAPSODY': 'RHAPSODY',  # from xls
        'PANDORA': 'PANDORA',  # from xls. Virtual input --> NET?
        'NAPSTER': 'NAPSTER',  # from xls. Virtual input --> NET?
        'LASTFM': 'LASTFM',  # from xls. Virtual input --> NET?
        'FLICKR': 'FLICKR',  # from xls. Virtual input --> NET?
        'IRADIO': 'IRADIO',  # from xls. Virtual input --> NET?
        'FAVORITES': 'FAVORITES',  # from xls. Virtual input --> NET?
        'CDR': 'CDR',  # from xls
        'NET/USB': 'NET/USB',  # from xls
        'M-XPORT': 'MXPORT'  # from xls
    }

    INPUT_ID_TO_ICON_MAPPING = {
        # input_id : icon mapping
        'AUX1': 'hdmi',
        'AUX2': 'hdmi',
        'AUX3': 'hdmi',
        'AUX4': 'hdmi',
        'AUX5': 'hdmi',
        'AUX6': 'hdmi',
        'AUX7': 'hdmi',
        'BT': 'bluetooth-audio',
        'BD': 'blu-ray',
        'SAT/CBL': 'satellite',
        'SAT': 'satellite',
        'CD': 'cd',
        'DVD': 'dvd',
        'GAME': 'videogame',
        'HDRADIO': 'radio',
        'IRP': 'radio',
        'USB/IPOD': 'usb',
        'MPLAY': 'dvr',
        'SERVER': 'cloud',
        'NET': 'cloud',
        'PHONO': 'hdmi',
        'TUNER': 'radio',
        'TV': 'tv',
        'SPOTIFY': 'spotify'  # add missing!
    }

    def __init__(self, config):
        self.config = config
        self.baseUri = 'http://{0}'.format(config['ip'])
        self.session = None
        self._connected = False
        self.zones = []
        self.internals = []

    @property
    async def connected(self):
        print('I am {}connected'.format('' if self._connected else 'not '))
        return self._connected

    async def connect(self):
        print('going to connect')
        self.session = aiohttp.ClientSession()
        try:
            cmds = await self._post_app_command('GetZoneName', 'GetRenameSource')
            self.input_ids = [Marantz.INPUT_NAME_TO_ID_MAPPING[x.findtext('name').strip().upper()]
                              for x in cmds[1].findall('functionrename/list')]
            self.inputs = [(x.findtext('rename').strip(),
                            Marantz.INPUT_ID_TO_ICON_MAPPING[Marantz.INPUT_NAME_TO_ID_MAPPING[x.findtext('name').strip().upper()]])
                           for x in cmds[1].findall('functionrename/list')]
            self.zones = [Zone(self, i, x.text.strip(), self.inputs) for i, x in enumerate(cmds[0])]
            self.internals = [Tuner(self, 0)]
            self._connected = True
            print('all is good and well!')
        except asyncio.CancelledError:
            if self.session:
                self.session.close()
            raise
        except Exception:
            traceback.print_exc()
            raise

    async def disconnect(self):
        print('going to disconnect')
        if self.session:
            self.session.close()
        self._connected = False

    @property
    async def static_info(self):
        print('im in static info')
        augmented_zones = [{'name': z.name, 'inputs': z.inputs} for z in self.zones]
        return {'name': 'Marantz NR1605', 'ip': self.config['ip'], 'zones': augmented_zones, 'volume_step': 0.5, 'internals': [('tuner', 'radio')]}

    async def listen(self):
        print('listen_for_updates')
        while await self.connected:
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

    async def executeInternalCommand(self, internalId, commandName, arguments):
        internal = self.internals[internalId]
        await internal.executeCommand(commandName, arguments)

    def _map_input(self, input):
        if input == 'Online Music' or input == 'Favorites' or input == 'Flickr' or input == 'Media Server' or input == 'Internet Radio':
            return self.input_ids.index('NET')
        else:
            return self.input_ids.index(input)

    async def _get(self, path):
        async with self.session.get(self.baseUri + path) as response:
            resp_text = await response.text()
        return resp_text

    async def _post(self, path, data, headers = None):
        async with self.session.post(self.baseUri + path, data = data, headers = headers) as response:
            resp_text = await response.text()
        return resp_text

    async def _post_app_command(self, *args):
        req_data = '<?xml version="1.0" encoding="utf-8"?>\n<tx><cmd id="1">{0}</cmd></tx>'.format('</cmd><cmd id="1">'.join(args))
        headers = {'Content-Type': 'text/xml'}
        async with self.session.post(self.baseUri + '/goform/AppCommand.xml', data=req_data, headers=headers) as response:
            resp_data = await response.text()
        return ElementTree.fromstring(resp_data).findall('cmd')
