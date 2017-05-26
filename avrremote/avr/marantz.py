from .base import AbstractAvr

import requests
from xml.etree import ElementTree

class Marantz(AbstractAvr):

	INPUT_NAME_TO_ID_MAPPING = {
		# name : source_id mapping
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
		'SPOTIFYCONNECT': 'SPOTIFY', # Virtual input --> NET?
		'VCR': 'VCR', # from xls
		'V.AUX': 'V.AUX', # from xls
		'SIRIUS': 'SIRIUS', # from xls
		'SIRIUSXM': 'SIRIUSXM', # from xls
		'RHAPSODY': 'RHAPSODY', # from xls
		'PANDORA': 'PANDORA', # from xls. Virtual input --> NET?
		'NAPSTER': 'NAPSTER', # from xls. Virtual input --> NET?
		'LASTFM': 'LASTFM', # from xls. Virtual input --> NET?
		'FLICKR': 'FLICKR', # from xls. Virtual input --> NET?
		'IRADIO': 'IRADIO', # from xls. Virtual input --> NET?
		'FAVORITES': 'FAVORITES', # from xls. Virtual input --> NET?
		'CDR': 'CDR', # from xls
		'NET/USB': 'NET/USB', # from xls
		'M-XPORT': 'MXPORT' # from xls
	}
	
	INPUT_ID_TO_ICON_MAPPING = {
		# source_id : icon mapping
		'AUX1': 'settings_input_hdmi',
		'AUX2': 'settings_input_hdmi',
		'AUX3': 'settings_input_hdmi',
		'AUX4': 'settings_input_hdmi',
		'AUX5': 'settings_input_hdmi',
		'AUX6': 'settings_input_hdmi',
		'AUX7': 'settings_input_hdmi',
		'BT': 'bluetooth_audio',
		'BD': 'album',
		'SAT/CBL': 'settings_input_hdmi',
		'SAT': 'settings_input_hdmi',
		'CD': 'album',
		'DVD': 'album',
		'GAME': 'videogame_asset',
		'HDRADIO': 'radio',
		'IRP': 'radio',
		'USB/IPOD': 'usb',
		'MPLAY': 'movie', #'fiber_dvr',
		'SERVER': 'cloud',
		'NET': 'cloud',
		'PHONO': 'settings_input_hdmi',
		'TUNER': 'radio',
		'TV': 'tv',
		'SPOTIFY': 'cloud' # add missing!
	}

	def __init__(self, config, listener):
		self.listener = listener
		self.config = config
		self.baseUri = 'http://{0}'.format(config['ip'])
		
		cmds = self._post_app_command('GetZoneName', 'GetRenameSource')
		self.zones = [ x.text.strip() for x in cmds[0] ]

		self.source_ids = [ Marantz.INPUT_NAME_TO_ID_MAPPING[x.findtext('name').strip().upper()] for x in cmds[1].findall('functionrename/list') ]
		self.sources = [ (x.findtext('rename').strip(), Marantz.INPUT_ID_TO_ICON_MAPPING[Marantz.INPUT_NAME_TO_ID_MAPPING[x.findtext('name').strip().upper()]]) for x in cmds[1].findall('functionrename/list') ]
		
	@property
	def static_info(self):
		return { 'name': 'Marantz NR1605', 'ip': self.config['ip'], 'zones': self.zones, 'sources': self.sources, 'volume_step': 0.5 }
	
	def get_power(self, zoneId):
		return self._get_zone_status( zoneId )['power']
	
	def set_power(self, zoneId, value):
		self._get( '/goform/formiPhoneAppPower.xml?{0}+{1}'.format(zoneId + 1, 'PowerOn' if value else 'PowerStandby') )

	def get_volume(self, zoneId):
		return self._get_zone_status( zoneId )['volume']
	
	def set_volume(self, zoneId, value):
		if value > 98:
			value = 98
		elif value < 0:
			value = 0
		
		volume = value - 80
		self._get( '/goform/formiPhoneAppVolume.xml?{0}+{2:0{1}.1f}'.format(zoneId + 1, 4 if volume >= 0 else 5, volume) )
	
	def get_selected_input(self, zoneId):
		input = self._get_zone_status( zoneId )['input']
		if input == 'Online Music' or input == 'Favorites' or input == 'Flickr' or input == 'Media Server' or input == 'Internet Radio':
			return self.source_ids.index( 'NET' )
		else:
			return self.source_ids.index( input )
	
	def select_input(self, zoneId, inputId):
		pass
	
	def _get(self, path):
		return requests.get( self.baseUri + path ).text
	
	def _post_app_command(self, *args):
		req_data = '<?xml version="1.0" encoding="utf-8"?>\n<tx><cmd id="1">{0}</cmd></tx>'.format('</cmd><cmd id="1">'.join(args))
		headers = {'Content-Type': 'text/xml'}
		resp_data = requests.post( self.baseUri + '/goform/AppCommand.xml', data = req_data, headers = headers).text
		return ElementTree.fromstring( resp_data ).findall('cmd')
	
	def _get_zone_status(self, zoneId):
		if(zoneId == 0):
			data = self._get('/goform/formMainZone_MainZoneXmlStatusLite.xml')
		else:
			data = self._get('/goform/formZone{0}_Zone{0}XmlStatusLite.xml'.format(zoneId + 1))
		xml = ElementTree.fromstring( data )
		return { 'power': xml.findtext( 'Power/value' ) == 'ON',
			'input': xml.findtext( 'InputFuncSelect/value' ),
			'volume': float(xml.findtext( 'MasterVolume/value' )) + 80,
			'mute': xml.findtext( 'Mute/value') == 'on' }
		