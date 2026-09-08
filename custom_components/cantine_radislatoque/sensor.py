"""Sensor platform for Cantine."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CantineConfigEntry
from .const import ATTR_LAST_ERROR, ATTR_LAST_UPDATE, ATTR_PLANNING, ATTR_RESTAURANT_ID, ATTR_URL
from .coordinator import CantineCoordinator


async def async_setup_entry(hass, entry: CantineConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the menu sensor."""
    async_add_entities([CantineMenuSensor(entry.runtime_data.coordinator)])


class CantineMenuSensor(CoordinatorEntity[CantineCoordinator], SensorEntity):
    """Menu sensor exposing the current week as an attribute."""

    _attr_has_entity_name = True
    _attr_name = "Menu cantine Radis la Toque"
    _attr_icon = "mdi:silverware-fork-knife"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: CantineCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_menu"

    @property
    def available(self) -> bool:
        """Keep cached data visible after a transient failure."""
        return bool(self.coordinator.data)

    @property
    def native_value(self) -> datetime | None:
        """Use the last successful refresh as sensor state."""
        if not self.coordinator.data:
            return None
        value = self.coordinator.data.get("last_update")
        if not isinstance(value, str):
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return menu and refresh metadata."""
        data = self.coordinator.data or {}
        return {
            ATTR_PLANNING: data.get("planning", {}),
            ATTR_LAST_UPDATE: data.get("last_update"),
            ATTR_LAST_ERROR: self.coordinator.last_error,
            ATTR_URL: data.get("url"),
            ATTR_RESTAURANT_ID: data.get("restaurant_id"),
        }
