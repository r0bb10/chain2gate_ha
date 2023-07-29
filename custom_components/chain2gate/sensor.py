"""Platform for sensor integration of C2G."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
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
        async_add_entities([sensor], update_before_add=True)


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
        return self._c2g_sensor._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self.gate.id + "_" + self.name

    @property
    def available(self) -> bool:
        return self._available

    @property
    def device_info(self) -> DeviceInfo:
        """Return a device description for device registry."""
        return DeviceInfo(
            configuration_url="http://" + self.gate.ip,
            manufacturer="MAC s.r.l",
            model="Chain2Gate",
            name=self.gate.id,
            identifiers={(DOMAIN, self.gate.id)}
        )

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = 23