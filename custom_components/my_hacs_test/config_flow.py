from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import TextSelector
from .const import DOMAIN

import voluptuous as vol

class CoServConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            user_id = user_input["user_id"]

            # Check if entry with this user_id already exists
            await self.async_set_unique_id(user_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"CoServ ({user_id})",
                data={
                    "user_id": user_input["user_id"],
                    "password": user_input["password"],
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("user_id"): str,
                vol.Required("password"): str
            }),
            errors=errors
        )