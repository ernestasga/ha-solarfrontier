"""Coordinators for data fetching."""
from datetime import timedelta
import logging

import aiohttp
from python_solarfrontier.api import SolarFrontierAPI

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class SolarFrontierBaseCoordinator(DataUpdateCoordinator):
    """Base coordinator for fetching data from Solar Frontier inverter."""

    def __init__(self, hass: HomeAssistant, api: SolarFrontierAPI, update_interval: timedelta) -> None:
        """Initialize the base coordinator."""
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name="solar_frontier",
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch data from Solar Frontier inverter."""
        raise NotImplementedError("Must implement _async_update_data in subclasses")


class SystemInfoCoordinator(SolarFrontierBaseCoordinator):
    """Coordinator for fetching system information from Solar Frontier inverter."""

    async def _async_update_data(self):
        """Fetch system information from Solar Frontier inverter."""
        try:
            return await self.api.get_system_info()
        except aiohttp.ClientError as e:
            raise UpdateFailed(f"Error fetching system info: {e}") from e


class PowerYieldCoordinator(SolarFrontierBaseCoordinator):
    """Coordinator for fetching power yield data from Solar Frontier inverter."""

    async def _async_update_data(self):
        """Fetch power yield data from Solar Frontier inverter."""
        try:
            return {
                "day": await self.api.get_yield_day(),
                "month": await self.api.get_yield_month(),
                "year": await self.api.get_yield_year(),
                "total": await self.api.get_yield_total(),
            }
        except aiohttp.ClientError as e:
            raise UpdateFailed(f"Error fetching power yield data: {e}") from e

class MeasurementsCoordinator(SolarFrontierBaseCoordinator):
    """Coordinator for fetching measurement data from Solar Frontier inverter."""

    async def _async_update_data(self):
        """Fetch measurement data from Solar Frontier inverter."""
        try:
            return await self.api.get_measurements()
        except aiohttp.ClientError as e:
            raise UpdateFailed(f"Error fetching measurements: {e}") from e
