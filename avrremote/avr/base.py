from abc import ABCMeta, abstractmethod, abstractproperty


class AvrListener:
    # Call when the volume got updated
    # value: the new volume value. float [0..100]
    def onVolumeUpdated(self, value):
        raise NotImplementedError


class AbstractAvr(metaclass=ABCMeta):
    @property
    @abstractmethod
    async def connected(self):
        pass

    @abstractmethod
    async def connect(self):
        pass

    # must return a dictionary with at least the following keys: name (string), zones (list of zone names),
    # inputs (list of tuples: (input names, input icon)), volume_step (float).
    @property
    @abstractmethod
    async def static_info(self):
        pass

    @property
    def status(self):
        return {
            'zones': [{
                'power': self.get_power(zoneId),
                'volume': self.get_volume(zoneId),
                'input': self.get_selected_input(zoneId)
            } for zoneId in range(len(self.static_info['zones']))]
        }

    # A constructor like this must be implemented in all subclasses.
    # config: the configuration. This is read from the configuration file and passed to your constructor. Use it to pass any necessary parameters.
    # listener: the instance of AvrListener. If your AVR supports async callbacks, use this listener to update the UI when you received updated values from your AVR.
    @staticmethod
    @abstractmethod
    def __init__(self, config, listener):
        pass

    # returns a bool representing the main power of the device
    # zoneId: the zone id, int, index in static_info.zones of the zone
    @abstractmethod
    def get_power(self, zoneId):
        pass

    # switches a certain zone on/off
    # zoneId: the zone id, int, index in static_info.zones of the zone
    # value: a boolean
    @abstractmethod
    def set_power(self, zoneId, value):
        pass

    # returns a float [0..100] representing the volume
    # zoneId: the zone id, int, index in static_info.zones of the zone
    @abstractmethod
    def get_volume(self, zoneId):
        pass

    # set the volume to the specified value
    # zoneId: the zone id, int, index in static_info.zones of the zone
    # value: a float [0..100] representing the new volume
    @abstractmethod
    def set_volume(self, zoneId, value):
        pass

    # returns the index of the selected input. The returned value is the index in the static_info.sources list
    # zoneId: the zone id, int, index in static_info.zones of the zone
    @abstractmethod
    def get_selected_input(self, zoneId):
        pass

    # selects an input source
    # inputId: the id of the input source to select. Corresponds to the index in the static_info.sources list
    # zoneId: the zone id, int, index in static_info.zones of the zone
    @abstractmethod
    def select_input(self, zoneId, inputId):
        pass

    @classmethod
    def __subclasshook__(cls, C):
        if cls is AbstractAvr:
            return true
        return NotImplemented
