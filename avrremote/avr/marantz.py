from .base import AbstractAvr

class Marantz(AbstractAvr):
	def get_volume(self):
		return 81
	
	def set_volume(self):
		return