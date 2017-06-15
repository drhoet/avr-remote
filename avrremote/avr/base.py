from abc import ABCMeta, abstractmethod, abstractproperty
import asyncio

class AvrUpdate:
    pass


class AvrZonePropertyUpdate(AvrUpdate):
    def __init__(self, zoneId, prop, value):
        self.zoneId = zoneId
        self.property = prop
        self.value = value


class AbstractAvr(metaclass=ABCMeta):
    # A constructor like this must be implemented in all subclasses.
    # config: the configuration. This is read from the configuration file and passed to your constructor. Use it to pass any necessary parameters.
    # listener: the instance of AvrListener. If your AVR supports async callbacks, use this listener to update the UI when you received updated values from your AVR.
    @staticmethod
    @abstractmethod
    def __init__(self, config):
        pass

    @property
    @abstractmethod
    async def connected(self):
        pass

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect():
        pass

    # must return a dictionary with at least the following keys: name (string), volume_step (float),
    # zones (list of dicts, { 'name': <name>, 'inputs': <list of tuples: (input name, input icon)> }),
    # internal (list of dicts, {'name': <name>, 'type': <currently supported: 'tuner'>})
    @property
    @abstractmethod
    async def static_info(self):
        pass

    @abstractmethod
    async def listen_for_updates(self):
        """ Async method that returns when an update was done on the Avr.
        The return value should be a list of AvrUpdate objects.
        """
        pass

    # switches a certain zone on/off
    # zoneId: the zone id, int, index in static_info.zones of the zone
    # value: a boolean
    @abstractmethod
    async def set_power(self, zoneId, value):
        pass

    # set the volume to the specified value
    # zoneId: the zone id, int, index in static_info.zones of the zone
    # value: a float [0..100] representing the new volume
    @abstractmethod
    async def set_volume(self, zoneId, value):
        pass

    # selects an input source
    # inputId: the id of the input source to select. Corresponds to the index in the static_info.sources list
    # zoneId: the zone id, int, index in static_info.zones of the zone
    @abstractmethod
    async def select_input(self, zoneId, inputId):
        pass

    @classmethod
    def __subclasshook__(cls, C):
        if cls is AbstractAvr:
            return true
        return NotImplemented
