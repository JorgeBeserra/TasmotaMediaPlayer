"""The switch entities for musiccast."""
from typing import Any
import logging
import asyncio

# from aiomusiccast.capabilities import BinarySetter

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform, service
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

#from . import DOMAIN, MusicCastCapabilityEntity, MusicCastDataUpdateCoordinator

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
    
    monoprice = hass.data[DOMAIN][config_entry.entry_id][MONOPRICE_OBJECT]

    switch_entities = []

    zone_id = 1

    switch_entities.append(SwitchCapability(hass, monoprice, "3D", config_entry, config_entry.unique_id or config_entry.entry_id, zone_id))    
    switch_entities.append(SwitchCapability(hass, monoprice, "TONE", config_entry, config_entry.unique_id or config_entry.entry_id, zone_id))

    # only call update before add if it's the first run so we can try to detect zones
    first_run = hass.data[DOMAIN][config_entry.entry_id][FIRST_RUN]
    async_add_entities(switch_entities, first_run)


class SwitchCapability(SwitchEntity):
    """Representation of a Monoprice switch entity."""

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

        self._temp_lock = asyncio.Lock()
        
        self._controller = get_controller(
            self.hass,
            self._supported_controller,
            self._commands_encoding,
            unique_id,
            self._controller_data,
            self._delay
        )
            
        self._update_success = True

    @property
    def is_on(self) -> bool:
        """Return the current status."""
        #return self.capability.current

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the capability."""
        await self.send_command(self._commands['3d'], 0)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the capability."""
        await self.send_command(self._commands['tone'], 0)

    async def send_command(self, command, level):
        async with self._temp_lock:
            try:
                await self._controller.send(command, level)
            except Exception as e:
                _LOGGER.exception(e)