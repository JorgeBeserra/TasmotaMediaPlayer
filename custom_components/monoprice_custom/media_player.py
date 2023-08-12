"""Support for interfacing with Monoprice 6 zone home audio controller."""
import asyncio
import json
import logging

from serial import SerialException

from homeassistant import core
from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform, service
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import voluptuous as vol

from .controller import get_controller

from .const import (
    CONF_NAME,
    CONF_SOURCES,
    DOMAIN,
    FIRST_RUN,
    MONOPRICE_OBJECT,
    SERVICE_RESTORE,
    SERVICE_SNAPSHOT,
    SERVICE_SET_FRONT_LEFT,
    SERVICE_SET_FRONT_RIGHT,
    SERVICE_SET_CENTER,
    SERVICE_SET_REAR_LEFT,
    SERVICE_SET_REAR_RIGHT,
    SERVICE_SET_SUBWOOFER,
    SERVICE_SET_BALANCE,
    SERVICE_SET_BASS,
    SERVICE_SET_MIDDLE,
    SERVICE_SET_TREBLE,
    ATTR_FRONT_LEFT,
    ATTR_FRONT_RIGHT,
    ATTR_CENTER,
    ATTR_REAR_LEFT,
    ATTR_REAR_RIGHT,
    ATTR_SUBWOOFER,
    ATTR_BALANCE,
    ATTR_BASS,
    ATTR_MIDDLE,
    ATTR_TREBLE,
    CONF_DELAY,
    CONF_CONTROLLER_DATA,
    COMMANDS,
    COMMANDS_ENCODING,
    SUPPORTED_CONTROLLER
)

SET_FRONT_LEFT_SCHEMA = vol.Schema(
    {
        vol.Optional("entity_id", default=[]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_FRONT_LEFT, default=0): vol.All(int, vol.Range(min=0, max=21))
    }
)

SET_FRONT_RIGHT_SCHEMA = vol.Schema(
    {
        vol.Optional("entity_id", default=[]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_FRONT_RIGHT, default=0): vol.All(int, vol.Range(min=0, max=21))
    }
)

SET_CENTER_SCHEMA = vol.Schema(
    {
        vol.Optional("entity_id", default=[]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_CENTER, default=0): vol.All(int, vol.Range(min=0, max=21))
    }
)

SET_REAR_LEFT_SCHEMA = vol.Schema(
    {
        vol.Optional("entity_id", default=[]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_REAR_LEFT, default=0): vol.All(int, vol.Range(min=0, max=21))
    }
)

SET_REAR_RIGHT_SCHEMA = vol.Schema(
    {
        vol.Optional("entity_id", default=[]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_REAR_RIGHT, default=0): vol.All(int, vol.Range(min=0, max=21))
    }
)

SET_SUBWOOFER_SCHEMA = vol.Schema(
    {
        vol.Optional("entity_id", default=[]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_SUBWOOFER, default=0): vol.All(int, vol.Range(min=0, max=21))
    }
)

SET_BALANCE_SCHEMA = vol.Schema(
    {
        vol.Optional("entity_id", default=[]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_BALANCE, default=0): vol.All(int, vol.Range(min=0, max=21))
    }
)

SET_BASS_SCHEMA = vol.Schema(
    {
        vol.Optional("entity_id", default=[]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_BASS, default=5): vol.All(int, vol.Range(min=0, max=15))
    }
)

SET_MIDDLE_SCHEMA = vol.Schema(
    {
        vol.Optional("entity_id", default=[]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_MIDDLE, default=5): vol.All(int, vol.Range(min=0, max=15))
    }
)

SET_TREBLE_SCHEMA = vol.Schema(
    {
        vol.Optional("entity_id", default=[]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_TREBLE, default=5): vol.All(int, vol.Range(min=0, max=15))
    }
)

_LOGGER = logging.getLogger(__name__)

MAX_VOLUME = 38
PARALLEL_UPDATES = 1


# @core.callback
# def _get_sources_from_dict(data):
#     sources_config = data[CONF_SOURCES]
#     source_id_name = {int(index): name for index, name in sources_config.items()}
#     source_name_id = {v: k for k, v in source_id_name.items()}
#     source_names = sorted(source_name_id.keys(), key=lambda v: source_name_id[v])

#     return [source_id_name, source_name_id, source_names]


# @core.callback
# def _get_sources(config_entry):
#     if CONF_SOURCES in config_entry.options:
#         data = config_entry.options
#     else:
#         data = config_entry.data
#     return _get_sources_from_dict(data)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Monoprice 6-zone amplifier platform."""
    

    monoprice = hass.data[DOMAIN][config_entry.entry_id][MONOPRICE_OBJECT]

    #sources = _get_sources(config_entry)
    port = config_entry.data[CONF_PORT]

    entities = []
    #for i in range(1, 4):
    #    for j in range(1, 7):
    zone_id = 1
    _LOGGER.info("Adding zone %d for port %s", zone_id, port)
    entities.append(
        MonopriceZone(hass, monoprice, config_entry.entry_id, config_entry.unique_id or config_entry.entry_id, zone_id)
    )

    # only call update before add if it's the first run so we can try to detect zones
    first_run = hass.data[DOMAIN][config_entry.entry_id][FIRST_RUN]

    async_add_entities(entities, first_run)

    platform = entity_platform.async_get_current_platform()

    def _call_service(entities, service_call):
        for entity in entities:
            if service_call.service == SERVICE_SNAPSHOT:
                entity.snapshot()
            elif service_call.service == SERVICE_RESTORE:
                entity.restore()
            elif service_call.service == SERVICE_SET_FRONT_LEFT:
                entity.set_front_left(service_call)
            elif service_call.service == SERVICE_SET_FRONT_RIGHT:
                entity.set_front_right(service_call)
            elif service_call.service == SERVICE_SET_CENTER:
                entity.set_center(service_call)
            elif service_call.service == SERVICE_SET_REAR_LEFT:
                entity.set_rear_left(service_call)
            elif service_call.service == SERVICE_SET_REAR_RIGHT:
                entity.set_front_right(service_call)
            elif service_call.service == SERVICE_SET_SUBWOOFER:
                entity.set_subwoofer(service_call)
            elif service_call.service == SERVICE_SET_BALANCE:
                entity.set_balance(service_call)
            elif service_call.service == SERVICE_SET_BASS:
                entity.set_bass(service_call)
            elif service_call.service == SERVICE_SET_MIDDLE:
                entity.set_middle(service_call)
            elif service_call.service == SERVICE_SET_TREBLE:
                entity.set_treble(service_call)

    @service.verify_domain_control(hass, DOMAIN)
    async def async_service_handle(service_call: core.ServiceCall) -> None:
        """Handle for services."""
        entities = await platform.async_extract_from_service(service_call)

        if not entities:
            return

        hass.async_add_executor_job(_call_service, entities, service_call)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SNAPSHOT,
        async_service_handle,
        schema=cv.make_entity_service_schema({}),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_RESTORE,
        async_service_handle,
        schema=cv.make_entity_service_schema({}),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_FRONT_LEFT,
        async_service_handle,
        schema=SET_FRONT_LEFT_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_FRONT_RIGHT,
        async_service_handle,
        schema=SET_FRONT_RIGHT_SCHEMA,
    )    

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_CENTER,
        async_service_handle,
        schema=SET_CENTER_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_REAR_LEFT,
        async_service_handle,
        schema=SET_REAR_LEFT_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_REAR_RIGHT,
        async_service_handle,
        schema=SET_REAR_RIGHT_SCHEMA,
    )    

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SUBWOOFER,
        async_service_handle,
        schema=SET_SUBWOOFER_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_BALANCE,
        async_service_handle,
        schema=SET_BALANCE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_BASS,
        async_service_handle,
        schema=SET_BASS_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_MIDDLE,
        async_service_handle,
        schema=SET_MIDDLE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_TREBLE,
        async_service_handle,
        schema=SET_TREBLE_SCHEMA,
    )

class MonopriceZone(MediaPlayerEntity):
    """Representation of a Monoprice amplifier zone."""
    
    _attr_device_class = MediaPlayerDeviceClass.RECEIVER
    _attr_supported_features = (
         MediaPlayerEntityFeature.VOLUME_SET
         | MediaPlayerEntityFeature.VOLUME_MUTE
         | MediaPlayerEntityFeature.VOLUME_STEP
         | MediaPlayerEntityFeature.TURN_ON
         | MediaPlayerEntityFeature.TURN_OFF
         | MediaPlayerEntityFeature.SELECT_SOURCE
         | MediaPlayerEntityFeature.SELECT_SOUND_MODE
    )
    _attr_has_entity_name = True
    _attr_name = None
    _attr_sound_mode_list = ["Normal", "High Bass", "Medium Bass", "Low Bass"]
    _attr_sound_mode = None

    def __init__(self, hass, monoprice, config_entry, unique_id, zone_id):
        """Initialize new zone."""
        self.hass = hass
        self._monoprice = monoprice
        # dict source_id -> source name
        self._source_id_name = 1
        # dict source name -> source_id
        self._source_name_id = 1

        self._delay = CONF_DELAY
        self._controller_data = CONF_CONTROLLER_DATA
        self._supported_controller = SUPPORTED_CONTROLLER
        self._commands_encoding = COMMANDS_ENCODING
        self._commands = COMMANDS

        # ordered list of all source names
        self._attr_source_list = 1
        self._zone_id = zone_id
        self._attr_unique_id = unique_id
        self._attr_has_entity_name = True
        self._attr_name = None
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._zone_id, unique_id)},
            manufacturer="Monoprice",
            model="6-Zone Amplifier",
            name=f"Zone {self._zone_id}"
        )
        # self._attr_sound_mode_list = ["Normal", "High Bass", "Medium Bass", "Low Bass"]

        self._snapshot = None
        self._update_success = True

        self._temp_lock = asyncio.Lock()

        self._controller = get_controller(
            self.hass,
            self._supported_controller,
            self._commands_encoding,
            unique_id,
            self._controller_data,
            self._delay
        )

    def update(self) -> None:
        """Retrieve latest state."""
        # try:
        #     state = self._monoprice.zone_status(self._zone_id)
        # except SerialException:
        #     self._update_success = False
        #     _LOGGER.warning("Could not update zone %d", self._zone_id)
        #     return

        # if not state:
        #     self._update_success = False
        #     return
        #state = {'power':true, 'volume': 10, 'mute': false}

        #self._attr_state = MediaPlayerState.ON if state.power else MediaPlayerState.OFF
        self._attr_state = MediaPlayerState.ON
        self._attr_volume_level = 0 / MAX_VOLUME
        self._attr_is_volume_muted = False
        # idx = state.source
        # self._attr_source = self._source_id_name.get(idx)

    #@property
    #def entity_registry_enabled_default(self) -> bool:
    #    """Return if the entity should be enabled when first added to the entity registry."""
    #    if(self._zone_id == 10 or self._zone_id == 20 or self._zone_id == 30):
    #        return False
    #    return self._zone_id < 20 or self._update_success

    @property
    def media_title(self):
        """Return the current source as medial title."""
        return self.source

    def snapshot(self):
        """Save zone's current state."""
        #self._snapshot = self._monoprice.zone_status(self._zone_id)
        self._snapshot = self.send_command(self._commands['status'], 0)

    def restore(self):
        """Restore saved state."""
        if self._snapshot:
            #self._monoprice.restore_zone(self._snapshot)
            self.send_command(self._commands['snapshot'], 1)
            self.schedule_update_ha_state(True)

    def select_source(self, source: str) -> None:
        """Set input source."""
        if source not in self._source_name_id:
            return
        #idx = self._source_name_id[source]
        #self._monoprice.set_source(self._zone_id, idx)

    def turn_on(self) -> None:
        """Turn the media player on."""
        self.send_command(self._commands['off'], 1)

    def turn_off(self) -> None:
        """Turn the media player off."""
        self.send_command(self._commands['off'], 0)

    def mute_volume(self, mute: bool) -> None:
        """Mute (true) or unmute (false) media player."""
        self.send_command(self._commands['mute'])

    async def set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        await self.send_command(self._commands['volumeSet'], round(volume * MAX_VOLUME))

    async def volume_up(self) -> None:
        """Volume up the media player."""
        if self.volume_level is None:
            return
        volume = round(self.volume_level * MAX_VOLUME)
        #self._monoprice.set_volume(self._zone_id, min(volume + 1, MAX_VOLUME))
        await self.send_command(self._commands['volumeUp'], 0)

    async def volume_down(self) -> None:
        """Volume down media player."""
        if self.volume_level is None:
            return
        volume = round(self.volume_level * MAX_VOLUME)
        #self._monoprice.set_volume(self._zone_id, max(volume - 1, 0))
        await self.send_command(self._commands['volumeDown'], 0)

    def set_front_left(self, call) -> None:
        """Set front left level."""
        level = int(call.data.get(ATTR_FRONT_LEFT))
        self.send_command(self._commands['frontLeft'], level)

    def set_front_right(self, call) -> None:
        """Set front right level."""
        level = int(call.data.get(ATTR_FRONT_RIGHT))
        self.send_command(self._commands['frontRight'], level)

    def set_center(self, call) -> None:
        """Set center level."""
        level = int(call.data.get(ATTR_CENTER))
        self.send_command(self._commands['center'], level)

    def set_rear_left(self, call) -> None:
        """Set rear left level."""
        level = int(call.data.get(ATTR_REAR_LEFT))
        self.send_command(self._commands['rearLeft'], level)

    def set_rear_right(self, call) -> None:
        """Set rear right level."""
        level = int(call.data.get(ATTR_REAR_RIGHT))
        self.send_command(self._commands['rearRight'], level)

    def set_subwoofer(self, call) -> None:
        """Set subwoofer level."""
        level = int(call.data.get(ATTR_SUBWOOFER))
        self.send_command(self._commands['subwoofer'], level)

    def set_balance(self, call) -> None:
        """Set balance level."""
        level = int(call.data.get(ATTR_BALANCE))
        self.send_command(self._commands['balance'], level)
 
    def set_bass(self, call) -> None:
        """Set bass level."""
        level = int(call.data.get(ATTR_BASS))
        self.send_command(self._commands['bass'], level)
    
    def set_middle(self, call) -> None:
        """Set middle level."""
        level = int(call.data.get(ATTR_MIDDLE))
        self.send_command(self._commands['middle'], level)

    def set_treble(self, call) -> None:
        """Set treble level."""
        level = int(call.data.get(ATTR_TREBLE))
        self.send_command(self._commands['treble'], level)

    def select_sound_mode(self, sound_mode) -> None:
        """Switch the sound mode of the entity."""
        self._sound_mode = sound_mode
        if(sound_mode == "Normal"):
            self.send_command(self._commands['setNormalBass'], 1)
        elif(sound_mode == "High Bass"):
            self.send_command(self._commands['setHighBass'], 1)
        elif(sound_mode == "Medium Bass"):
            self.send_command(self._commands['setMediumBass'], 1)
        elif(sound_mode == "Low Bass"):
            self.send_command(self._commands['setLowBass'], 1)
    
    async def send_command(self, command, level):
        try:
            await self._controller.send(command, level)
        except Exception as e:
            _LOGGER.exception(e)