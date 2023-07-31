"""Platform for sensor integration of C2G."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities,
    discovery_info=None):
    """ Setup sensor platform """

    gate = hass.data[DOMAIN][config_entry.entry_id]

    sensors = gate.get_sensors()

    for sensor in sensors:
        async_add_entities([C2GHASensor(gate, sensor)], update_before_add=True)


class C2GHASensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, gate, c2g_sensor):
        super().__init__()
        self.gate = gate
        self._c2g_sensor = c2g_sensor
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._c2g_sensor.name
    
    @property
    def state(self):
        """Return the state of the device."""
        return self._state
    
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._c2g_sensor.unit_of_measurement
    
    @property
    def device_class(self):
        return self._c2g_sensor.device_class

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self.gate.id + "_" + self.name

    @property
    def available(self) -> bool:
        return self._available
    
    @property
    def should_poll(self):
        """Return that polling is not necessary."""
        return False

    @property
    def device_info(self) -> DeviceInfo:
        """Return a device description for device registry."""
        return DeviceInfo(
            configuration_url="http://" + self.gate.ip,
            manufacturer="MAC s.r.l",
            model="Chain2Gate",
            name=self.gate.id,
            identifiers={(DOMAIN, self.gate.id)},
            sw_version=self.gate.prog_id,
        )
    
    async def async_added_to_hass(self):
        """Register callback to update hass after device was changed."""
        async def after_update_callback():
            """Call after device was updated."""
            await self.async_update_ha_state(True)
        print("set callback")
        self._c2g_sensor.set_callback(after_update_callback)
        print("callback set")

    async def async_update(self):
        """Retrieve latest state."""
        self._state = self._c2g_sensor.value