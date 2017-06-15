from .base import AbstractAvr, AvrZonePropertyUpdate

import asyncio
import aiohttp
import requests
from xml.etree import ElementTree

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
        if(self.zoneId == 0):
            data = await self.avr._get('/goform/formMainZone_MainZoneXmlStatusLite.xml')
        else:
            data = await self.avr._get('/goform/formZone{0}_Zone{0}XmlStatusLite.xml'.format(self.zoneId + 1))
        xml = ElementTree.fromstring(data)

        result = [
            self._update_prop('power', xml.findtext('Power/value') == 'ON'),
            self._update_prop('input', self.avr._map_input(xml.findtext('InputFuncSelect/value'))),
            self._update_prop('volume', float(xml.findtext('MasterVolume/value')) + 80),
            self._update_prop('mute', xml.findtext('Mute/value') == 'on')
        ]
        return filter(None, result)


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
            self._connected = True
            print('all is good and well!')
        except asyncio.CancelledError:
            if self.session:
                self.session.close()
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
        return {'name': 'Marantz NR1605', 'ip': self.config['ip'], 'zones': augmented_zones, 'volume_step': 0.5, 'internals': {}}

    async def listen_for_updates(self):
        print('listen_for_updates')
        while await self.connected:
            all_zone_updates = await asyncio.gather(*[ zone.update() for zone in self.zones ])
            flattened_updates = [zone_update for zone_updates in all_zone_updates for zone_update in zone_updates]
            yield flattened_updates
            await asyncio.sleep(5)

    async def set_power(self, zoneId, value):
        await self._get('/goform/formiPhoneAppPower.xml?{0}+{1}'.format(zoneId + 1, 'PowerOn' if value else 'PowerStandby'))

    async def set_volume(self, zoneId, value):
        if value > 98:
            value = 98
        elif value < 0:
            value = 0

        volume = value - 80
        await self._get('/goform/formiPhoneAppVolume.xml?{0}+{2:0{1}.1f}'.format(zoneId + 1, 4 if volume >= 0 else 5, volume))

    def _map_input(self, input):
        if input == 'Online Music' or input == 'Favorites' or input == 'Flickr' or input == 'Media Server' or input == 'Internet Radio':
            return self.input_ids.index('NET')
        else:
            return self.input_ids.index(input)

    async def select_input(self, zoneId, inputId):
        await self._get('/goform/formiPhoneAppDirect.xml?{0}{1}'.format(
            'SI'if zoneId == 0 else 'Z{0}'.format(zoneId + 1), self.input_ids[inputId]))

    async def _get(self, path):
        async with self.session.get(self.baseUri + path) as response:
            resp_text = await response.text()
        return resp_text

    async def _post_app_command(self, *args):
        req_data = '<?xml version="1.0" encoding="utf-8"?>\n<tx><cmd id="1">{0}</cmd></tx>'.format('</cmd><cmd id="1">'.join(args))
        headers = {'Content-Type': 'text/xml'}
        async with self.session.post(self.baseUri + '/goform/AppCommand.xml', data=req_data, headers=headers) as response:
            resp_data = await response.text()
        return ElementTree.fromstring(resp_data).findall('cmd')
