"""The sia integration."""
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .hub import SIAHub


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the sia component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up sia from a config entry."""
    hub = SIAHub(hass, entry.data, entry.entry_id, entry.title)
    await hub.async_setup_hub()
    hass.data[DOMAIN][entry.entry_id] = hub
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )
    hub.sia_client.start(reuse_port=True)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )

    if unload_ok:
        await hass.data[DOMAIN][entry.entry_id].sia_client.stop()
        hass.data[DOMAIN][entry.entry_id].shutdown_remove_listener()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
