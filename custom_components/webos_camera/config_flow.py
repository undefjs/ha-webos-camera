"""Config flow for LG WebOS Camera integration."""
from __future__ import annotations

import logging
from typing import Any

import asyncssh
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, DEFAULT_PORT, DEFAULT_USERNAME, DEFAULT_INTERVAL, CONF_KEY_FILE

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
        vol.Optional(CONF_KEY_FILE): str,
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_INTERVAL): int,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    # Validate that either password or key_file is provided
    if not data.get(CONF_PASSWORD) and not data.get(CONF_KEY_FILE):
        raise ValueError("Either password or key_file must be provided")
    
    try:
        connect_params = {
            "host": data[CONF_HOST],
            "username": data[CONF_USERNAME],
            "known_hosts": None,
            "port": DEFAULT_PORT,
            "connect_timeout": 5
        }
        
        # Use SSH key if provided, otherwise use password
        if data.get(CONF_KEY_FILE):
            connect_params["client_keys"] = [data[CONF_KEY_FILE]]
        else:
            connect_params["password"] = data[CONF_PASSWORD]
        
        async with asyncssh.connect(**connect_params) as conn:
            # Try a simple command to verify
            await conn.run("echo hello", check=True)
    except (OSError, asyncssh.Error) as err:
        _LOGGER.error("Connection failed: %s", err)
        raise CannotConnect from err

    return {"title": f"WebOS Camera ({data[CONF_HOST]})"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LG WebOS Camera."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
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


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
