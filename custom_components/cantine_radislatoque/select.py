"""Select platform for the Cantine integration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util


JOURS = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
]


def _jour_actuel() -> str:
    """Return the current weekday, limited to the school week."""
    weekday = min(dt_util.now().weekday(), 4)
    return JOURS[weekday]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Cantine select."""
    async_add_entities(
        [
            CantineDaySelect(),
        ]
    )


class CantineDaySelect(SelectEntity):
    """Select the day to display."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:calendar-week"
    _attr_options = JOURS

    def __init__(self) -> None:
        """Initialize the select."""
        self._attr_unique_id = "jour_menu_cantine"
        self._attr_current_option = _jour_actuel()

    @property
    def name(self) -> str:
        """Return the entity name."""
        return "Jour du menu"

    async def async_select_option(self, option: str) -> None:
        """Select a menu day."""
        if option not in self._attr_options:
            return

        self._attr_current_option = option
        self.async_write_ha_state()
