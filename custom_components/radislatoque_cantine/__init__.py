"""Cantine integration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_change

from .api import CantineApi
from .const import (
    CONF_RESTAURANT_ID,
    PLATFORMS,
    UPDATE_HOUR,
    UPDATE_MINUTE,
    UPDATE_SECOND,
)
from .coordinator import CantineCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class CantineRuntimeData:
    """Runtime objects for a config entry."""
    coordinator: CantineCoordinator


type CantineConfigEntry = ConfigEntry[CantineRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: CantineConfigEntry) -> bool:
    """Set up Cantine from a config entry."""
    api = CantineApi(entry.data[CONF_RESTAURANT_ID])
    coordinator = CantineCoordinator(hass, entry, api)

    await coordinator.async_load_cache()

    if coordinator.should_refresh_on_start(UPDATE_HOUR):
        await coordinator.async_refresh()

    entry.runtime_data = CantineRuntimeData(coordinator=coordinator)

    async def _scheduled_refresh(now: datetime) -> None:
        """Refresh every day at 06:00 local Home Assistant time."""
        _LOGGER.debug("Actualisation planifiée Cantine")
        await coordinator.async_request_refresh()

    remove_listener = async_track_time_change(
        hass,
        _scheduled_refresh,
        hour=UPDATE_HOUR,
        minute=UPDATE_MINUTE,
        second=UPDATE_SECOND,
    )
    entry.async_on_unload(remove_listener)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: CantineConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
