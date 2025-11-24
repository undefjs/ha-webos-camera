"""Camera platform for LG WebOS Camera."""
from __future__ import annotations

import asyncio
import base64
import logging
from typing import Optional

import asyncssh
from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEFAULT_PORT, CONF_KEY_FILE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the WebOS Camera from a config entry."""
    host = entry.data[CONF_HOST]
    username = entry.data[CONF_USERNAME]
    password = entry.data.get(CONF_PASSWORD)
    key_file = entry.data.get(CONF_KEY_FILE)
    interval = entry.data[CONF_SCAN_INTERVAL]

    async_add_entities([WebOSCamera(host, username, password, key_file, interval, entry.title)])


class WebOSCamera(Camera):
    """Representation of a WebOS Camera."""

    _attr_supported_features = CameraEntityFeature.ON_OFF

    def __init__(self, host, username, password, key_file, interval, name):
        """Initialize the camera."""
        super().__init__()
        self._host = host
        self._username = username
        self._password = password
        self._key_file = key_file
        self._attr_name = name
        self._attr_unique_id = f"webos_camera_{host}"
        self._interval = interval
        self._conn = None
        self._is_on = True
        
        # Command to capture, base64 encode, and cleanup
        # We use a unique filename to avoid collisions if multiple instances run (though unlikely on same TV)
        self._cmd = (
            "luna-send -n 1 -f luna://com.webos.service.tv.capture/executeOneShot "
            "'{\"path\":\"/tmp/webos_cam.png\", \"method\":\"DISPLAY\", \"format\":\"PNG\", \"width\":960, \"height\":540}' "
            "&& base64 /tmp/webos_cam.png | grep -A100 '^iVBOR' | tr -d '\\n' "
            "&& rm /tmp/webos_cam.png"
        )

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""
        if not self._is_on:
            return None

        try:
            if self._conn is None:
                connect_params = {
                    "host": self._host,
                    "username": self._username,
                    "known_hosts": None,
                    "port": DEFAULT_PORT,
                    "connect_timeout": 5
                }
                
                # Use SSH key if provided, otherwise use password
                if self._key_file:
                    connect_params["client_keys"] = [self._key_file]
                else:
                    connect_params["password"] = self._password
                
                self._conn = await asyncssh.connect(**connect_params)

            # Run the command
            result = await self._conn.run(self._cmd, check=False)
            
            # Log command result for debugging
            _LOGGER.debug("Command stdout: %s", result.stdout)
            _LOGGER.debug("Command stderr: %s", result.stderr)
            _LOGGER.debug("Command exit status: %s", result.exit_status)
            
            if result.exit_status != 0:
                _LOGGER.error(
                    "Command failed with exit status %s. Stdout: %s, Stderr: %s",
                    result.exit_status,
                    result.stdout,
                    result.stderr
                )
                return None
            
            # Decode base64
            image_data = base64.b64decode(result.stdout.strip())
            return image_data

        except (OSError, asyncssh.Error, asyncio.TimeoutError) as err:
            _LOGGER.warning("Error getting camera image from %s: %s", self._host, err)
            # Force reconnection next time
            if self._conn:
                self._conn.close()
            self._conn = None
            return None
        except Exception as err:
             _LOGGER.exception("Unexpected error getting camera image: %s", err)
             return None

    @property
    def is_on(self) -> bool:
        """Return true if on."""
        return self._is_on

    def turn_off(self) -> None:
        """Turn off camera."""
        self._is_on = False

    def turn_on(self) -> None:
        """Turn on camera."""
        self._is_on = True
