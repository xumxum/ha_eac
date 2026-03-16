"""Adds config flow for eac."""
import logging

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    #CONF_SCAN_INTERVAL,
)


from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


class EACConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for EAC."""

    VERSION = 1

 
    async def async_step_user( self, user_input: dict | None = None ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_USERNAME], data=user_input)
        if user_input is None:
            user_input = {}

        data_schema=vol.Schema({
                vol.Required(CONF_USERNAME, default=user_input.get(CONF_USERNAME, vol.UNDEFINED)): str,
                vol.Required(CONF_PASSWORD, default=user_input.get(CONF_PASSWORD, vol.UNDEFINED)): str,
            })

        return self.async_show_form(
            step_id='user',
            data_schema=data_schema,
            errors=_errors
            )
    

    async def _validate_user_input(self, api_key: str, latitude: str, longitude: str):
        """Validate user input."""
        return True