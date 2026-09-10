"""Select platform for Cantine."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CantineConfigEntry
from .coordinator import CantineCoordinator


JOURS = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
]


async def async_setup_entry(hass, entry: CantineConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the menu day selector."""
    async_add_entities([CantineDaySelect(entry.runtime_data.coordinator)])


class CantineDaySelect(CoordinatorEntity[CantineCoordinator], SelectEntity):
    """Select the day to display."""

    _attr_has_entity_name = True
    _attr_name = "Jour du menu"
    _attr_icon = "mdi:calendar-week"
    _attr_options = JOURS

    def __init__(self, coordinator: CantineCoordinator) -> None:
        """Initialize the select."""
        super().__init__(coordinator)

        self._attr_unique_id = f"{coordinator.entry.entry_id}_menu_day"

        # Sélectionne automatiquement le jour actuel
        self._attr_current_option = self._get_current_day()

    @staticmethod
    def _get_current_day() -> str:
        """Return the current day."""
        from homeassistant.util import dt as dt_util

        weekday = dt_util.now().weekday()

        # Samedi et dimanche -> vendredi
        if weekday > 4:
            weekday = 4

        return JOURS[weekday]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the selected day after a coordinator refresh."""
        self._attr_current_option = self._get_current_day()
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Select a menu day."""
        if option not in JOURS:
            return

        self._attr_current_option = option
        self.async_write_ha_state()
