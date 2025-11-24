"""The LG WebOS Camera integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.CAMERA]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up LG WebOS Camera from a config entry."""
    
    hass.data.setdefault(DOMAIN, {})
    # We don't need to store anything specific here yet, 
    # the camera platform will handle the connection based on entry.data
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        pass
        # hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
