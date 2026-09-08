"""Config flow for Cantine."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector

from .api import CantineApi, CantineError
from .const import CONF_NAME, CONF_RESTAURANT_ID, DEFAULT_NAME, DEFAULT_RESTAURANT_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def _validate_restaurant(hass: HomeAssistant, restaurant_id: str) -> None:
    api = CantineApi(restaurant_id)
    await hass.async_add_executor_job(api.validate)


class CantineConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the Cantine config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle initial setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            restaurant_id = user_input[CONF_RESTAURANT_ID].strip()
            name = user_input[CONF_NAME].strip() or DEFAULT_NAME
            try:
                await _validate_restaurant(self.hass, restaurant_id)
            except CantineError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Erreur inattendue pendant la validation")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(restaurant_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name,
                    data={CONF_RESTAURANT_ID: restaurant_id, CONF_NAME: name},
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_RESTAURANT_ID, default=DEFAULT_RESTAURANT_ID): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Required(CONF_NAME, default=DEFAULT_NAME): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
