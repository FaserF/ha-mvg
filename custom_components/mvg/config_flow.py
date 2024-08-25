import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (  # pylint: disable=unused-import
    CONF_NEXT_DEPARTURE,
    CONF_STATION,
    CONF_DESTINATIONS,
    CONF_LINES,
    CONF_PRODUCTS ,
    CONF_TIMEOFFSET,
    CONF_NUMBER,
    CONF_PRODUCTS,
)

DOMAIN = "mvg"

_LOGGER = logging.getLogger(__name__)

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        def __get_option(key: str, default: Any) -> Any:
            return self.config_entry.options.get(
                key, self.config_entry.data.get(key, default)
            )

        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_STATION): str,
                    vol.Optional(CONF_DESTINATIONS, default=""): str,
                    vol.Optional(CONF_LINES, default=""): str,
                    vol.Optional(CONF_PRODUCTS, default="U-Bahn,Tram,Bus,ExpressBus,S-Bahn,Nachteule"): cv.multi_select(CONF_PRODUCTS),
                    vol.Optional(CONF_TIMEOFFSET, default=0): int,
                    vol.Optional(CONF_NUMBER, default=5): int,
                }
            ),
        )

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow"""

    VERSION = 2
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_START] + " to " + user_input[CONF_DESTINATION])
            self._abort_if_unique_id_configured()
            _LOGGER.debug("Initialized new mvg sensor with id: {unique_id}")
            return self.async_create_entry(title=user_input[CONF_START] + " - " + user_input[CONF_DESTINATION], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_STATION): str,
                vol.Optional(CONF_DESTINATIONS, default=""): str,
                vol.Optional(CONF_LINES, default=""): str,
                vol.Optional(CONF_PRODUCTS, default="U-Bahn,Tram,Bus,ExpressBus,S-Bahn,Nachteule"): cv.multi_select(CONF_PRODUCTS),
                vol.Optional(CONF_TIMEOFFSET, default=0): int,
                vol.Optional(CONF_NUMBER, default=5): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)
