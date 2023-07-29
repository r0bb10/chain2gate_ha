"""The Chain2Gate integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_HOST
from homeassistant.core import HomeAssistant

from .const import DOMAIN

from .c2g import Chain2Gate

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Chain2Gate from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    gate = Chain2Gate(entry.data[CONF_HOST])
    await hass.async_add_executor_job(gate.connect)
    hass.data[DOMAIN][entry.entry_id] = gate


    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
