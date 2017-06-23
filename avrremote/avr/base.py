from abc import ABCMeta, abstractmethod, abstractproperty
import asyncio

class UnsupportedUpdateException(BaseException):
    """ Exception raised by AbstractAvr when an unrecognized update is received

    Attributes:
        message -- explanation of the error
        update -- the offending AvrUpdate
    """
    def __init__(self, message, update):
        self.update = update
        self.message = message


class AvrUpdate:
    pass


class AvrZonePropertyUpdate(AvrUpdate):
    def __init__(self, zoneId, prop, value):
        """Creates a new AvrZonePropertyUpdate object

        Keyword arguments:
        zoneId -- the zone id of the zone, int, index in static_info.zones
        property -- the name of the property to be updated. Currently supported are:
            power: boolean
            volume: float [0..100]
            input: the id of the input source to select. Corresponds to the index in the static_info.sources list
            mute: boolean
        value -- the new value of the property. For the type, see the documentation of property.
        """
        self.zoneId = zoneId
        self.property = prop
        self.value = value


class AvrTunerPropertyUpdate(AvrUpdate):
    def __init__(self, internalId, prop, value):
        """Creates a new AvrTunerPropertyUpdate object

        Keyword arguments:
        internalId -- the id of the internal, int, index in static_info.internals
        property -- the name of the property to be updated. Currently supported are:
            freq: float
            band: 'AM' or 'FM'
        value -- the new value of the property. For the type, see the documentation of property.
        """
        self.internalId = internalId
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
    async def disconnect(self):
        pass

    # must return a dictionary with at least the following keys: name (string), volume_step (float),
    # zones (list of dicts, { 'name': <name>, 'inputs': <list of tuples: (input name, input icon)> }),
    # internal (list of dicts, {'name': <name>, 'type': <currently supported: 'tuner'>})
    @property
    @abstractmethod
    async def static_info(self):
        pass

    @abstractmethod
    async def listen(self):
        """ Async method that returns when an update was done on the Avr.
        The return value should be a list of AvrUpdate objects.
        """
        pass

    @abstractmethod
    async def send(self, avr_update):
        """ Apply the given AvrUpdate to the avr.

        Keyword arguments:
        avr_update -- an AvrUpdate object (or subclass) containing the update to be sent to the AVR.
        Exceptions:
        UnsupportedUpdateException -- when an object in avr_updates is of unsupported type
        """
        pass

    @classmethod
    def __subclasshook__(cls, C):
        if cls is AbstractAvr:
            return true
        return NotImplemented

class EndpointProperty:
    def __init__(self, value, sender):
        self.value = value
        self.send = sender


class AbstractEndpoint(metaclass=ABCMeta):
    """ An endpoint of a receiver. This can be a zone, or a virtual input (e.g. a tuner)
    An endpoint has properties that can be updated by the receiver, or new values can
    be sent to the receiver.
    """

    def __init__(self, avr):
        self.avr = avr
        self.properties = {}

    @abstractmethod
    def create_property_update(self, property_name, property_value):
        pass

    def _register_property(self, name, sender):
        """ Call this method from your constructor, to register a propery in the endpoint
        Keyword arguments:
        name -- a name for the property
        sender -- the method that should be used when an update of the property must be sent to the endpoint.
            Must be an async callable with one parameter (the value), which returns
            the value that was set on the endpoint
        """
        self.properties[name] = EndpointProperty(None, sender)

    def _property_updated(self, name, value):
        """ Call this when an endpoint property got updated. This happens when an update is received from the AVR """
        if self.properties[name].value != value:
            self.properties[name].value = value
            return self.create_property_update(name, value)

    async def send(self, avr_update):
        """ Sends an update to the endpoint """
        if avr_update.property in self.properties:
            set_value = await self.properties[avr_update.property].send(avr_update.value)
            self.properties[avr_update.property].value = set_value
        else:
            raise UnsupportedUpdateException('Property \'{}\' not supported by endpoint'.format(avr_update.property), avr_update)
