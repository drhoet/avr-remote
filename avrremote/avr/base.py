from abc import ABCMeta, abstractmethod, abstractproperty

class AvrListener:
	# Call when the volume got updated
	# value: the new volume value. float [0..100]
	def onVolumeUpdated( self, value ):
		raise NotImplementedError

class AbstractAvr(metaclass=ABCMeta):
	# must return a dictionary with at least the following keys: name (string), zones (int), sources (list).
	@property
	@abstractmethod
	def static_info(self):
		pass
	
	@property
	def status(self):
		return {
			'zones': [ {
				'power': self.get_power(zoneId),
				'volume': self.get_volume(zoneId)
			} for zoneId in range(self.static_info['zones']) ]
		}

	# A constructor like this must be implemented in all subclasses.
	# config: the configuration. This is read from the configuration file and passed to your constructor. Use it to pass any necessary parameters.
	# listener: the instance of AvrListener. If your AVR supports async callbacks, use this listener to update the UI when you received updated values from your AVR.
	@staticmethod
	@abstractmethod
	def __init__( self, config, listener ):
		pass
	
	# returns a bool representing the main power of the device
	# zoneId: the zone id, int [0..static_info.zones[
	@abstractmethod
	def get_power(self, zoneId):
		pass

	# switches a certain zone on/off
	# zoneId: the zone id, int [0..static_info.zones[
	# value: a boolean
	@abstractmethod
	def set_power(self, zoneId, value):
		pass

	# returns a float [0..100] representing the volume
	# zoneId: the zone id, int [0..static_info.zones[
	@abstractmethod
	def get_volume(self, zoneId):
		pass

	# set the volume to the specified value
	# zoneId: the zone id, int [0..static_info.zones[
	# value: a float [0..100] representing the new volume
	@abstractmethod
	def set_volume(self, zoneId, value):
		pass
	
	@classmethod
	def __subclasshook__(cls, C):
		if cls is AbstractAvr:
			return true;
		return NotImplemented