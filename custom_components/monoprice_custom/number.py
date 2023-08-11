"""Support for interfacing with Monoprice 6 zone home audio controller."""
from code import interact
import logging

from serial import SerialException

from homeassistant import core
try:
    from homeassistant.components.number import (
        NumberEntity as NumberEntity,
    )
except ImportError:
    from homeassistant.components.number import NumberEntity

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform, service
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    FIRST_RUN,
    MONOPRICE_OBJECT,
    CONF_DELAY,
    CONF_CONTROLLER_DATA,
    COMMANDS,
    COMMANDS_ENCODING,
    SUPPORTED_CONTROLLER
)

from .controller import get_controller

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 1

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Monoprice 6-zone amplifier platform."""
    port = config_entry.data[CONF_PORT]
    monoprice = hass.data[DOMAIN][config_entry.entry_id][MONOPRICE_OBJECT]

    entities = []
    #for i in range(1, 4):
    #    for j in range(1, 7):
    zone_id = 1
    _LOGGER.info("Adding number entities for zone %d for port %s", zone_id, port)
    entities.append(MonopriceZone(hass, monoprice, "FrontLeft", config_entry, config_entry.unique_id or config_entry.entry_id, zone_id))
    entities.append(MonopriceZone(hass, monoprice, "FrontRight", config_entry, config_entry.unique_id or config_entry.entry_id, zone_id))
    entities.append(MonopriceZone(hass, monoprice, "Center", config_entry, config_entry.unique_id or config_entry.entry_id, zone_id))
    entities.append(MonopriceZone(hass, monoprice, "RearLeft", config_entry, config_entry.unique_id or config_entry.entry_id, zone_id))
    entities.append(MonopriceZone(hass, monoprice, "RearRight", config_entry, config_entry.unique_id or config_entry.entry_id, zone_id))
    entities.append(MonopriceZone(hass, monoprice, "Subwoofer", config_entry, config_entry.unique_id or config_entry.entry_id, zone_id))

    entities.append(MonopriceZone(hass, monoprice, "Balance", config_entry, config_entry.unique_id or config_entry.entry_id, zone_id))
    entities.append(MonopriceZone(hass, monoprice, "Bass", config_entry, config_entry.unique_id or config_entry.entry_id, zone_id))
    entities.append(MonopriceZone(hass, monoprice, "Middle", config_entry, config_entry.unique_id or config_entry.entry_id, zone_id))
    entities.append(MonopriceZone(hass, monoprice, "Treble", config_entry, config_entry.unique_id or config_entry.entry_id, zone_id))

    # only call update before add if it's the first run so we can try to detect zones
    first_run = hass.data[DOMAIN][config_entry.entry_id][FIRST_RUN]
    async_add_entities(entities, first_run)

    platform = entity_platform.async_get_current_platform()

    @service.verify_domain_control(hass, DOMAIN)
    async def async_service_handle(service_call: core.ServiceCall) -> None:
        """Handle for services."""
        entities = await platform.async_extract_from_service(service_call)

        if not entities:
            return

class MonopriceZone(NumberEntity):
    """Representation of a Monoprice amplifier zone."""

    def __init__(self, hass, monoprice, control_type, config_entry, unique_id, zone_id):
        """Initialize new zone controls."""
        self.hass = hass
        self._monoprice = monoprice
        self._control_type = control_type
        self._zone_id = zone_id

        self._delay = CONF_DELAY
        self._controller_data = CONF_CONTROLLER_DATA
        self._supported_controller = SUPPORTED_CONTROLLER
        self._commands_encoding = COMMANDS_ENCODING
        self._commands = COMMANDS
        
        self._attr_unique_id = f"{unique_id}_{self._control_type}"
        self._attr_has_entity_name = True
        self._attr_name = f"{control_type} level"
        self._attr_native_step = 1
        self._attr_native_value = None
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._zone_id, unique_id)},
            manufacturer="Monoprice",
            model="6-Zone Amplifier",
            name=f"Zone {self._zone_id}"
        )

        if(control_type == "FrontLeft"):
            self._attr_native_min_value = 0
            self._attr_native_max_value = 20
            self._attr_icon = "mdi:speaker"
        elif(control_type == "FrontRight"):
            self._attr_native_min_value = 0
            self._attr_native_max_value = 20
            self._attr_icon = "mdi:speaker"
        elif(control_type == "Center"):
            self._attr_native_min_value = 0
            self._attr_native_max_value = 20
            self._attr_icon = "mdi:speaker"
        elif(control_type == "RearLeft"):
            self._attr_native_min_value = 0
            self._attr_native_max_value = 20
            self._attr_icon = "mdi:speaker"
        elif(control_type == "RearRight"):
            self._attr_native_min_value = 0
            self._attr_native_max_value = 20
            self._attr_icon = "mdi:speaker"
        elif(control_type == "Subwoofer"):
            self._attr_native_min_value = 0
            self._attr_native_max_value = 20
            self._attr_icon = "mdi:speaker"
        elif(control_type == "Balance"):
            self._attr_native_min_value = 0
            self._attr_native_max_value = 20
            self._attr_icon = "mdi:scale-balance"
        elif(control_type == "Bass"):
            self._attr_native_min_value = -7
            self._attr_native_max_value =  7
            self._attr_icon = "mdi:speaker"
        elif(control_type == "Middle"):
            self._attr_native_min_value = -7
            self._attr_native_max_value =  7
            self._attr_icon = "mdi:speaker"
        elif(control_type == "Treble"):
            self._attr_native_min_value = -7
            self._attr_native_max_value =  7
            self._attr_icon = "mdi:surround-sound"
        
        self._controller = get_controller(
            self.hass,
            self._supported_controller,
            self._commands_encoding,
            unique_id,
            self._controller_data,
            self._delay
        )
            
        self._update_success = True
        
    def update(self):
        """Retrieve latest value."""
        # try:
        #     state = self._monoprice.zone_status(self._zone_id)
        # except SerialException:
        #     self._update_success = False
        #     _LOGGER.warning("Could not update zone %d", self._zone_id)
        #     return

        #if not state:
        self._update_success = True
        #    return
        state = {'balance': 0, 'bass': 0, 'treble': 0}

        if(self._control_type == "FrontLeft"):
            self._attr_native_value = 0
        elif(self._control_type == "FrontRight"):
            self._attr_native_value = 0
        elif(self._control_type == "Center"):
            self._attr_native_value = 0
        elif(self._control_type == "RearLeft"):
            self._attr_native_value = 0
        elif(self._control_type == "RearRight"):
            self._attr_native_value = 0
        elif(self._control_type == "Subwoofer"):
            self._attr_native_value = 0
        elif(self._control_type == "Balance"):
            self._attr_native_value = 0
        elif(self._control_type == "Bass"):
            self._attr_native_value = 0
        elif(self._control_type == "Middle"):
            self._attr_native_value = 0
        elif(self._control_type == "Treble"):
            self._attr_native_value = 0

    def set_native_value(self, value: float) -> None:
        """Update the current value."""
        if(self._control_type == "FrontLeft"):
            self.send_command(self._commands['frontLeft'], int(value))
        elif(self._control_type == "FrontRight"):
            self.send_command(self._commands['frontRight'], int(value))
        elif(self._control_type == "Center"):
            self.send_command(self._commands['center'], int(value))
        elif(self._control_type == "RearLeft"):
            self.send_command(self._commands['rearLeft'], int(value))
        elif(self._control_type == "RearRight"):
            self.send_command(self._commands['rearRight'], int(value))
        elif(self._control_type == "Subwoofer"):
            self.send_command(self._commands['subwoofer'], int(value))
        elif(self._control_type == "Balance"):
            self.send_command(self._commands['balance'], int(value))
        elif(self._control_type == "Bass"):
            self.send_command(self._commands['bass'], int(value))
        elif(self._control_type == "Middle"):
            self.send_command(self._commands['middle'], int(value))
        elif(self._control_type == "Treble"):
            self.send_command(self._commands['treble'], int(value))

    def send_command(self, command, level):
        try:
            self._controller.send(command, level)
        except Exception as e:
            _LOGGER.exception(e)
