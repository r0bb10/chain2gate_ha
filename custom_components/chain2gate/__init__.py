"""The Chain2Gate integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_HOST
from homeassistant.core import HomeAssistant


from .const import DOMAIN
from .c2g import Chain2Gate

PLATFORMS: list[Platform] = [Platform.SENSOR]

import asyncio

DISCOVERY_INTERVAL = 60  # seconds

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Chain2Gate from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    async def do_connect():
        gate = Chain2Gate(hass, entry.data[CONF_HOST])
        if not await gate.check_connection(False):
            return False
        await gate.connect()
        hass.data[DOMAIN][entry.entry_id] = gate
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        return True

    async def delayed_connect(_event=None):
        await do_connect()

    # Wait for Home Assistant to be fully started before connecting
    hass.bus.async_listen_once("homeassistant_started", delayed_connect)

    # Periodic re-scan/reconnect logic
    async def periodic_discovery():
        while True:
            await asyncio.sleep(DISCOVERY_INTERVAL)
            await do_connect()

    hass.async_create_task(periodic_discovery())

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
