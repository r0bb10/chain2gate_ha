"""Config flow for Chain2Gate integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

from .c2g import Chain2Gate

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    # gate = await hass.async_add_executor_job(Chain2Gate, hass, data["host"])

    gate = Chain2Gate(hass, data["host"])

    if await gate.check_connection(False):

        if DOMAIN in hass.data:
            for g in hass.data[DOMAIN].values():
                if gate.id == g.id:
                    raise AlreadyConfigured()

        return {"title": gate.id}
    else:
        raise CannotConnect()


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Chain2Gate."""

    VERSION = 1

    async def async_step_zeroconf(self, discovery_info):
        """Handle zeroconf discovery."""
        _LOGGER.info("ZEROCONF: async_step_zeroconf triggered!")
        # Extract info from discovery_info
        ip = getattr(discovery_info, "ip_address", None)
        if not ip and hasattr(discovery_info, "ip_addresses") and discovery_info.ip_addresses:
            ip = discovery_info.ip_addresses[0]
        ip_str = str(ip) if ip is not None else None
        name = getattr(discovery_info, "name", None)
        hostname = None
        if name:
            import re
            match = re.search(r"c2g-[A-F0-9]+", name)
            if match:
                hostname = match.group(0)
        display_name = hostname or name or ip_str
        if not hostname:
            _LOGGER.warning("ZEROCONF: aborting, could not extract hostname")
            return self.async_abort(reason="unknown")
        # Set unique_id and abort if already configured
        await self.async_set_unique_id(hostname)
        self._abort_if_unique_id_configured()
        # Store all info for confirmation step
        self.discovery_info = {
            "title": display_name,
            CONF_HOST: ip_str,
            "hostname": hostname,
            "name": name,
        }
        self.context["title_placeholders"] = {"name": display_name}
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(self, user_input=None):
        """Show confirmation form to add discovered device."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title=self.discovery_info["title"],
                data={CONF_HOST: self.discovery_info[CONF_HOST]}
            )
        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={
                "name": self.discovery_info["title"],
                "ip": self.discovery_info[CONF_HOST],
            },
            errors=errors,
        )

    async def async_step_confirm(self, user_input=None):
        """Show confirmation form to add discovered device."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title=self.discovery_info["title"],
                data={CONF_HOST: self.discovery_info[CONF_HOST]}
            )
        # Show device info in the confirmation dialog using translations
        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "name": self.discovery_info["title"],
                "ip": self.discovery_info[CONF_HOST],
            },
            errors=errors,
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except AlreadyConfigured:
                errors["base"] = "already_configured"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

class AlreadyConfigured(HomeAssistantError):
    """Error to indicate host is already configured."""

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
