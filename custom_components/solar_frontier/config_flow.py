"""Config flow for Solar Frontier integration."""
from __future__ import annotations

import logging
from typing import Any

from python_solarfrontier.api import SolarFrontierAPI
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str})


class SolarFrontierConnectionChecker:
    """Check connection to inverter on LAN."""

    model_name = None
    nominal_power = None

    def __init__(self, host: str) -> None:
        """Initialize."""
        if not host.startswith(('http://', 'https://')):
            host = f"http://{host}"
        self.host = host

    async def connect(self) -> bool:
        """Test if we can connect with the host."""
        api = SolarFrontierAPI(self.host)
        connection = await api.test_connection()
        api.close()
        if not connection:
            return False
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    checker = SolarFrontierConnectionChecker(data[CONF_HOST])
    if not await checker.connect():
        raise CannotConnect

    # Return info that you want to store in the config entry.
    return {
        "title": f"Solar Frontier inverter at {data[CONF_HOST]}",

        "model_name": checker.model_name,
        "nominal_power": checker.nominal_power
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solar Frontier."""

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
