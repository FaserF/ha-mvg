"""The mvg component."""
import asyncio
import logging
from datetime import timedelta

from homeassistant import config_entries, core
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
import async_timeout

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up MVG integration from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    hass_data = dict(entry.data)

    unsub_options_update_listener = entry.add_update_listener(options_update_listener)
    hass_data["unsub_options_update_listener"] = unsub_options_update_listener
    hass.data[DOMAIN][entry.entry_id] = hass_data

    # Verwende async_forward_entry_setups anstelle von async_forward_entry_setup für zukünftige Erweiterungen
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    async def async_update_data():
        """Fetch data from MVG API."""
        config = hass.data[DOMAIN][entry.entry_id]
        update_interval = SCAN_INTERVAL  # Standard-Scanintervall
        async with async_timeout.timeout(update_interval * 60 - 1):
            # Hier sollte data.update() asynchron sein
            await hass.async_add_executor_job(data.update)

            if not data.departures:
                raise UpdateFailed(f"Error fetching {entry.entry_id} MVG data")

            return data.departures

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{entry.entry_id} MVG departures",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    hass_data["coordinator"] = coordinator
    hass.data[DOMAIN][entry.entry_id] = hass_data

    return True

async def options_update_listener(
    hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry
):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)

async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a MVG config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN][entry.entry_id]["unsub_options_update_listener"]()

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
