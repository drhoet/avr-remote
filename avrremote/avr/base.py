class AbstractAvr:
	# returns an int 0..100 representing the volume
	def get_volume(self):
		raise NotImplementedError

	# set the volume to the specified value
	# value: an int 0..100 representing the new volume
	def set_volume(self, value):
		raise NotImplementedError