from abc import ABC, abstractmethod
from base64 import b64encode
import binascii
import requests
import logging
import json

from homeassistant.const import ATTR_ENTITY_ID
from . import Helper

_LOGGER = logging.getLogger(__name__)

MQTT_CONTROLLER = 'MQTT'
LOOKIN_CONTROLLER = 'LOOKin'
ESPHOME_CONTROLLER = 'ESPHome'

ENC_BASE64 = 'Base64'
ENC_HEX = 'Hex'
ENC_PRONTO = 'Pronto'
ENC_RAW = 'Raw'

BROADLINK_COMMANDS_ENCODING = [ENC_BASE64, ENC_HEX, ENC_PRONTO]
XIAOMI_COMMANDS_ENCODING = [ENC_PRONTO, ENC_RAW]
MQTT_COMMANDS_ENCODING = [ENC_RAW]
LOOKIN_COMMANDS_ENCODING = [ENC_PRONTO, ENC_RAW]
ESPHOME_COMMANDS_ENCODING = [ENC_RAW]


def get_controller(hass, controller, encoding, unique_id, controller_data, delay):
    """Return a controller compatible with the specification provided."""
    controllers = {
        MQTT_CONTROLLER: MQTTController,
        LOOKIN_CONTROLLER: LookinController,
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
    async def send(self, command):
        """Send a command."""
        pass

class MQTTController(AbstractController):
    """Controls a MQTT device."""

    def check_encoding(self, encoding):
        """Check if the encoding is supported by the controller."""
        if encoding not in MQTT_COMMANDS_ENCODING:
            raise Exception("The encoding is not supported "
                            "by the mqtt controller.")

    async def send(self, command):
        """Send a command."""

        service_data = {
            'topic': 'cmnd/' + self._unique_id + '/driver129',
            'payload': command
        }

        await self.hass.services.async_call(
            'mqtt', 'publish', service_data)


class LookinController(AbstractController):
    """Controls a Lookin device."""

    def check_encoding(self, encoding):
        """Check if the encoding is supported by the controller."""
        if encoding not in LOOKIN_COMMANDS_ENCODING:
            raise Exception("The encoding is not supported "
                            "by the LOOKin controller.")

    async def send(self, command):
        """Send a command."""
        encoding = self._encoding.lower().replace('pronto', 'prontohex')
        url = f"http://{self._controller_data}/commands/ir/" \
                f"{encoding}/{command}"
        await self.hass.async_add_executor_job(requests.get, url)


class ESPHomeController(AbstractController):
    """Controls a ESPHome device."""

    def check_encoding(self, encoding):
        """Check if the encoding is supported by the controller."""
        if encoding not in ESPHOME_COMMANDS_ENCODING:
            raise Exception("The encoding is not supported "
                            "by the ESPHome controller.")
    
    async def send(self, command):
        """Send a command."""
        service_data = {'command':  json.loads(command)}

        await self.hass.services.async_call(
            'esphome', self._controller_data, service_data)