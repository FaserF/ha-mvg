import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN

@config_entries.HANDLERS.register(DOMAIN)
class MVGConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input["station"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("station"): str,
                vol.Optional("destinations", default=""): str,
                vol.Optional("lines", default=""): str,
                vol.Optional("products", default="U-Bahn,Tram,Bus,ExpressBus,S-Bahn,Nachteule"): str,
                vol.Optional("timeoffset", default=0): int,
                vol.Optional("number", default=5): int,
            })
        )
