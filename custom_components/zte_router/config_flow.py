"""Config flow for ZTE Router integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .api import ZTERouterAPI
from .const import DEFAULT_HOST, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ZTERouterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ZTE Router."""
    
    VERSION = 1
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            host = user_input[CONF_HOST]
            password = user_input.get(CONF_PASSWORD)
            
            # Test the connection
            api = ZTERouterAPI(host, password)
            try:
                # Try to get router status to verify connection
                data = await api.async_update()
                
                if not data or not any(data.values()):
                    errors["base"] = "cannot_connect"
                else:
                    await api.close()
                    
                    # Create unique ID from host
                    await self.async_set_unique_id(host)
                    self._abort_if_unique_id_configured()
                    
                    return self.async_create_entry(
                        title=f"ZTE Router ({host})",
                        data={
                            CONF_HOST: host,
                            CONF_PASSWORD: password,
                        },
                    )
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error during setup: %s", err)
                errors["base"] = "cannot_connect"
            finally:
                await api.close()
        
        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=DEFAULT_HOST): cv.string,
                vol.Optional(CONF_PASSWORD): cv.string,
            }
        )
        
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "host": DEFAULT_HOST,
            },
        )


class ZTERouterOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for ZTE Router."""
    
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
    
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({}),
        )
