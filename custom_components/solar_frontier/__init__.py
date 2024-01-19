"""The Solar Frontier integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from python_solarfrontier.api import SolarFrontierAPI

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import (
    MeasurementsCoordinator,
    PowerYieldCoordinator,
    SystemInfoCoordinator,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Solar Frontier from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    # Create an instance of your API class
    api = SolarFrontierAPI(entry.data[CONF_HOST])

    # Validate the API connection
    if not await api.test_connection():
        await api.close()  # Close the session if connection fails
        return False


    # Initialize coordinators
    system_info_coordinator = SystemInfoCoordinator(hass, api, timedelta(hours=6))
    power_yield_coordinator = PowerYieldCoordinator(hass, api, timedelta(minutes=30))
    measurements_coordinator = MeasurementsCoordinator(hass, api, timedelta(seconds=20))


    # Fetch initial data so we have data when entities subscribe
    await system_info_coordinator.async_refresh()
    await power_yield_coordinator.async_refresh()
    await measurements_coordinator.async_refresh()

    # Store the API and coordinator
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "system_info": system_info_coordinator,
        "power_yield": power_yield_coordinator,
        "measurements": measurements_coordinator
    }

    # Set up your platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
    # Close the API session
        api = hass.data[DOMAIN].pop(entry.entry_id, None)
        if api:
            await api.close()

    return unload_ok
