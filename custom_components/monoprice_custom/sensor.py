"""Support for interfacing with Monoprice 6 zone home audio controller."""
from code import interact
import logging

from serial import SerialException

from homeassistant import core
try:
    from homeassistant.components.sensor import (
        SensorEntity as SensorEntity,
    )
except ImportError:
    from homeassistant.components.sensor import SensorEntity

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform, service
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    FIRST_RUN,
    MONOPRICE_OBJECT
)

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
        #for j in range(1, 7):
        #zone_id = (i * 10) + j
    zone_id = 1
    _LOGGER.info("Adding sensor entities for zone %d for port %s", zone_id, port)
    entities.append(MonopriceZone(monoprice, "Mute", config_entry, config_entry.unique_id or config_entry.entry_id, zone_id))
    entities.append(MonopriceZone(monoprice, "3D", config_entry, config_entry.unique_id or config_entry.entry_id, zone_id))
    entities.append(MonopriceZone(monoprice, "Tone", config_entry, config_entry.unique_id or config_entry.entry_id, zone_id))

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

class MonopriceZone(SensorEntity):
    """Representation of a Monoprice amplifier zone."""

    def __init__(self, monoprice, sensor_type, config_entry, unique_id,zone_id):
        """Initialize new zone sensors."""
        self._monoprice = monoprice
        self._sensor_type = sensor_type
        self._zone_id = zone_id
        self._attr_unique_id = f"{unique_id}_{self._sensor_type}"
        self._attr_has_entity_name = True
        self._attr_name = f"{sensor_type}"
        self._attr_native_value = None
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            manufacturer="Monoprice",
            model="6-Zone Amplifier",
            name=f"Zone"
        )

        if(sensor_type == "Mute"):
            self._attr_icon = "mdi:volume-mute"
        elif(sensor_type == "3D"):
            self._attr_icon = "mdi:3d-rotate"
        elif(sensor_type == "Tone"):
            self._attr_icon = "mdi:tune"
            
        self._update_success = True

        # Tópico para escutar as mensagens MQTT
        self._mqtt_topic = f"stat/{unique_id}/RESULT"
        self._hass.loop.create_task(self._subscribe_to_mqtt())

    async def _subscribe_to_mqtt(self):
        """Subscribe to the MQTT topic and handle updates."""
        async def message_callback(msg):
            """Handle incoming MQTT messages."""
            try:
                payload = json.loads(msg.payload)
                if "PT2322" in payload:
                    self._update_from_payload(payload["PT2322"])
            except json.JSONDecodeError:
                _LOGGER.warning("Invalid JSON in MQTT payload: %s", msg.payload)

        await self._hass.components.mqtt.async_subscribe(self._mqtt_topic, message_callback)
        _LOGGER.info("Subscribed to MQTT topic: %s", self._mqtt_topic)

    def _update_from_payload(self, payload):
        """Update the sensor based on the payload."""
        if self._sensor_type == "Mute":
            self._attr_native_value = payload.get("Mute", "Unknown")
        elif self._sensor_type == "3D":
            self._attr_native_value = payload.get("3D", "Unknown")
        elif self._sensor_type == "Tone":
            self._attr_native_value = payload.get("Tone", "Unknown")

        self.async_write_ha_state()  # Atualiza o estado no Home Assistant

    def update(self):
        """Retrieve latest value."""
        # try:
        #     state = self._monoprice.zone_status(self._zone_id)
        # except SerialException:
        #     self._update_success = False
        #     _LOGGER.warning("Could not update zone %d", self._zone_id)
        #     return

        #if not state:
        #state = {'keypad':false, 'pa': True, 'do_not_disturb':false}
        self._update_success = True

        if(self._sensor_type == "Mute"):
            self._attr_native_value = '{}'.format('Off')
        elif(self._sensor_type == "3D"):
            self._attr_native_value = '{}'.format('Off')
        elif(self._sensor_type == "Tone"):
            self._attr_native_value = '{}'.format('Off')

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        if(self._zone_id == 10 or self._zone_id == 20 or self._zone_id == 30):
            return False
        return self._zone_id < 20 or self._update_success
