from abc import ABCMeta, abstractmethod, abstractproperty

class AvrListener:
	# Call when the volume got updated
	# value: the new volume value. float [0..100]
	def onVolumeUpdated( self, value ):
		raise NotImplementedError

class AbstractAvr(metaclass=ABCMeta):
	
	@property
	@abstractmethod
	def static_info(self):
		pass

	# A constructor like this must be implemented in all subclasses.
	# config: the configuration. This is read from the configuration file and passed to your constructor. Use it to pass any necessary parameters.
	# listener: the instance of AvrListener. If your AVR supports async callbacks, use this listener to update the UI when you received updated values from your AVR.
	@staticmethod
	@abstractmethod
	def __init__( self, config, listener ):
		pass

	# returns a float [0..100] representing the volume
	@abstractmethod
	def get_volume(self):
		pass

	# set the volume to the specified value
	# value: a float [0..100] representing the new volume
	@abstractmethod
	def set_volume(self, value):
		pass
	
	@classmethod
	def __subclasshook__(cls, C):
		if cls is AbstractAvr:
			return true;
		return NotImplemented