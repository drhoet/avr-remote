class AvrListener:
	# Call when the volume got updated
	# value: the new volume value. float [0..100]
	def onVolumeUpdated( self, value ):
		raise NotImplementedError

class AbstractAvr:
	# A constructor like this must be implemented in all subclasses.
	# config: the configuration. This is read from the configuration file and passed to your constructor. Use it to pass any necessary parameters.
	# listener: the instance of AvrListener. If your AVR supports async callbacks, use this listener to update the UI when you received updated values from your AVR.
	def __init__( self, config, listener ):
		raise NotImplementedError

	# returns a float [0..100] representing the volume
	def get_volume(self):
		raise NotImplementedError

	# set the volume to the specified value
	# value: a float [0..100] representing the new volume
	def set_volume(self, value):
		raise NotImplementedError