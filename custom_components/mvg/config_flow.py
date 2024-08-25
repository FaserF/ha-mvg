import logging
from typing import Any

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (  # pylint: disable=unused-import
    CONF_STATION,
    CONF_DESTINATIONS,
    CONF_LINES,
    CONF_PRODUCTS,
    CONF_TIMEOFFSET,
    CONF_NUMBER,
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
        _LOGGER.debug("Starting async_step_init with user_input: %s", user_input)

        def __get_option(key: str, default: Any) -> Any:
            return self.config_entry.options.get(
                key, self.config_entry.data.get(key, default)
            )

        if user_input is not None:
            _LOGGER.debug("User input received: %s", user_input)
            return self.async_create_entry(data=user_input)

        _LOGGER.debug("Showing init form")
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_STATION): str,
                    vol.Optional(CONF_DESTINATIONS, default=""): str,
                    vol.Optional(CONF_LINES, default=""): str,
                    vol.Optional(CONF_PRODUCTS, default=CONF_PRODUCTS): cv.multi_select(CONF_PRODUCTS),
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
        _LOGGER.debug("Starting async_step_user with user_input: %s", user_input)
        errors = {}

        if user_input is not None:
            try:
                unique_id = f"{user_input[CONF_STATION]}"
                _LOGGER.debug("Generated unique_id: %s", unique_id)
                await self.async_set_unique_id(unique_id)
                _LOGGER.debug("Set unique ID, checking if already configured")
                self._abort_if_unique_id_configured()
                _LOGGER.debug(f"Initialized new mvg sensor with id: {unique_id}")
                return self.async_create_entry(
                    title=f"{user_input[CONF_STATION]} - {user_input[CONF_DESTINATIONS]}",
                    data=user_input
                )
            except KeyError as e:
                _LOGGER.error("KeyError in async_step_user: %s", e, exc_info=True)
                errors["base"] = "key_error"
            except ValueError as e:
                _LOGGER.error("ValueError in async_step_user: %s", e, exc_info=True)
                errors["base"] = "value_error"
            except Exception as e:
                _LOGGER.error("Exception in async_step_user while handling user_input: %s", e, exc_info=True)
                errors["base"] = "unknown_error"

        _LOGGER.debug("Showing user form with data_schema")
        try:
            data_schema = vol.Schema(
                {
                    vol.Required(CONF_STATION): str,
                    vol.Optional(CONF_DESTINATIONS, default=""): str,
                    vol.Optional(CONF_LINES, default=""): str,
                    vol.Optional(CONF_PRODUCTS, default=CONF_PRODUCTS): cv.multi_select(CONF_PRODUCTS),
                    vol.Optional(CONF_TIMEOFFSET, default=0): int,
                    vol.Optional(CONF_NUMBER, default=5): int,
                }
            )
        except Exception as e:
            _LOGGER.error("Exception while creating data_schema: %s", e, exc_info=True)
            errors["base"] = "schema_error"

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
        _LOGGER.debug("Creating OptionsFlowHandler")
        return OptionsFlowHandler(config_entry)
