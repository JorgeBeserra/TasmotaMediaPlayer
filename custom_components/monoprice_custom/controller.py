from abc import ABC, abstractmethod
import json
import logging

_LOGGER = logging.getLogger(__name__)

MQTT_CONTROLLER = 'MQTT'
ESPHOME_CONTROLLER = 'ESPHome'

ENC_RAW = 'Raw'

MQTT_COMMANDS_ENCODING = [ENC_RAW]
ESPHOME_COMMANDS_ENCODING = [ENC_RAW]


def get_controller(hass, controller, encoding, unique_id, controller_data, delay):
    """Return a controller compatible with the specification provided."""
    controllers = {
        MQTT_CONTROLLER: MQTTController,
        ESPHOME_CONTROLLER: ESPHomeController
    }
    try:
        return controllers[controller](hass, controller, encoding, unique_id, controller_data, delay)
    except KeyError:
        raise Exception("The controller is not supported.")


class AbstractController(ABC):
    """Representation of a controller."""
    def __init__(self, hass, controller, encoding, unique_id, controller_data, delay):
        self.check_encoding(encoding)
        self.hass = hass
        self._controller = controller
        self._encoding = encoding
        self._unique_id = unique_id
        self._controller_data = controller_data
        self._delay = delay

    @abstractmethod
    def check_encoding(self, encoding):
        """Check if the encoding is supported by the controller."""
        pass

    @abstractmethod
    async def send(self, command, level: int):
        """Send a command."""
        pass


class MQTTController(AbstractController):
    """Controls a MQTT device."""

    def check_encoding(self, encoding):
        """Check if the encoding is supported by the controller."""
        if encoding not in MQTT_COMMANDS_ENCODING:
            raise Exception("The encoding is not supported by the MQTT controller.")

    async def send(self, command, level: int):
        """Send a command."""
        service_data = {
            'topic': f'cmnd/{self.unique_id}/driver129',
            'payload': f'{command} {level}'
        }

        try:
            await self.hass.services.async_call('mqtt', 'publish', service_data)
        except Exception as e:
            _LOGGER.error("Error sending MQTT command: %s", e)

    async def exist(self):
        try:
            return self.hass.services.has_service('mqtt', 'publish')
        except Exception as e:
            _LOGGER.error("Error checking MQTT service existence: %s", e)


class ESPHomeController(AbstractController):
    """Controls a ESPHome device."""

    def check_encoding(self, encoding):
        """Check if the encoding is supported by the controller."""
        if encoding not in ESPHOME_COMMANDS_ENCODING:
            raise Exception("The encoding is not supported by the ESPHome controller.")

    async def send(self, command, level: int):
        """Send a command."""
        service_data = {'command': json.loads(command) + ' ' + json.loads(command)}

        try:
            await self.hass.services.async_call('esphome', self._controller_data, service_data)
        except Exception as e:
            _LOGGER.error("Error sending ESPHome command: %s", e)

    async def exist(self):
        try:
            return self.hass.services.has_service('esphome', self._controller_data)
        except Exception as e:
            _LOGGER.error("Error checking ESPHome service existence: %s", e)
