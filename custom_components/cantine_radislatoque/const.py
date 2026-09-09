"""Constants for the Cantine integration."""
from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "cantine_radislatoque"
CONF_RESTAURANT_ID = "restaurant_id"
CONF_NAME = "name"

DEFAULT_RESTAURANT_ID = "1097"
DEFAULT_NAME = "cantine_radislatoque"

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON, Platform.SELECT]

BASE_URL = "https://www.radislatoque.fr/restaurants"

UPDATE_HOUR = 6
UPDATE_MINUTE = 10
UPDATE_SECOND = 0

STORAGE_VERSION = 1
STORAGE_KEY_PREFIX = "cantine_radislatoque"

ATTR_PLANNING = "planning"
ATTR_LAST_UPDATE = "last_update"
ATTR_LAST_ERROR = "last_error"
ATTR_URL = "url"
ATTR_RESTAURANT_ID = "restaurant_id"
