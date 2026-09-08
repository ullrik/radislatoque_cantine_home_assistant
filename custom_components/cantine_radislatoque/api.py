"""Synchronous web client for Radis la Toque."""
from __future__ import annotations

from datetime import date, datetime
import logging
import re

import requests
from bs4 import BeautifulSoup

from .const import BASE_URL

_LOGGER = logging.getLogger(__name__)

WEEKDAYS = (
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
)

CATEGORIES = {
    "entrée": "entree",
    "plat principal": "plat",
    "légumes": "legumes",
    "fromage": "fromage",
    "dessert": "dessert",
}


class CantineError(Exception):
    """Base exception for the Cantine client."""


class CantineConnectionError(CantineError):
    """Raised when the web site cannot be reached or parsed."""


class CantineApi:
    """Client used by the Home Assistant integration."""

    def __init__(self, restaurant_id: str) -> None:
        self._restaurant_id = restaurant_id
        self._url = f"{BASE_URL}/{restaurant_id}"

    @staticmethod
    def _new_session() -> requests.Session:
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/151.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "fr-FR,fr;q=0.9",
            }
        )
        return session

    @staticmethod
    def _clean_text(cell) -> str:
        """Extract visible text from a menu cell."""
        return " ".join(cell.stripped_strings)

    @staticmethod
    def _parse_header_date(text: str, year: int) -> date | None:
        """Parse the DD/MM date contained in a weekday header."""
        match = re.search(r"\b(\d{1,2})/(\d{1,2})\b", text)
        if not match:
            return None
        try:
            return date(year, int(match.group(2)), int(match.group(1)))
        except ValueError:
            return None

    @staticmethod
    def _find_menu_table(soup: BeautifulSoup):
        """Find the table containing the menu categories."""
        for table in soup.find_all("table"):
            text = " ".join(table.stripped_strings).lower()
            if "entrée" in text and "plat principal" in text and "dessert" in text:
                return table
        return None

    def _get_page(self) -> str:
        """Download the restaurant page."""
        session = self._new_session()
        try:
            response = session.get(self._url, timeout=(10, 30))
            response.raise_for_status()
            return response.text
        except requests.RequestException as err:
            raise CantineConnectionError(
                f"Impossible de récupérer le menu : {err}"
            ) from err
        finally:
            session.close()

    def get_menu(self, today: date | None = None) -> dict:
        """Return the current menu in a HA-friendly planning structure."""
        today = today or date.today()
        html = self._get_page()
        soup = BeautifulSoup(html, "html.parser")
        table = self._find_menu_table(soup)

        if table is None:
            raise CantineConnectionError("Table du menu introuvable.")

        rows = table.find_all("tr")
        if not rows:
            raise CantineConnectionError("Aucune ligne trouvée dans le tableau.")

        # The first row containing at least three French weekdays is the
        # header row. Current Radis la Toque HTML has five day columns.
        header_cells = None
        for row in rows:
            cells = row.find_all(["th", "td"])
            day_count = 0
            for cell in cells:
                text = self._clean_text(cell).lower()
                if any(text.startswith(day) for day in WEEKDAYS):
                    day_count += 1
            if day_count >= 3:
                header_cells = cells
                break

        if header_cells is None:
            raise CantineConnectionError("Jours du menu introuvables.")

        columns: dict[int, tuple[str, date]] = {}
        for index, cell in enumerate(header_cells):
            text = self._clean_text(cell).lower()
            for weekday in WEEKDAYS:
                if text.startswith(weekday):
                    parsed = self._parse_header_date(text, today.year)
                    if parsed is None:
                        raise CantineConnectionError(
                            f"Date introuvable pour {weekday}."
                        )
                    columns[index] = (weekday, parsed)
                    break

        if not columns:
            raise CantineConnectionError("Colonnes des jours introuvables.")

        planning: dict[str, dict] = {}
        for _, (weekday, menu_date) in columns.items():
            planning[menu_date.strftime("%Y%m%d")] = {
                "date": menu_date.isoformat(),
                "jour": weekday,
                "repas_vegetarien": False,
                "entree": "",
                "plat": "",
                "plat_vegetarien": "",
                "legumes": "",
                "fromage": "",
                "dessert": "",
            }

        current_category: str | None = None
        for row in rows:
            cells = row.find_all(["th", "td"])
            if not cells:
                continue

            first_text = self._clean_text(cells[0]).lower()
            category = CATEGORIES.get(first_text)

            if category:
                current_category = category
                for index, (_, menu_date) in columns.items():
                    if index < len(cells):
                        key = menu_date.strftime("%Y%m%d")
                        planning[key][category] = self._clean_text(cells[index])
                continue

            # Radis la Toque uses the row immediately following "Plat principal"
            # for the vegetarian alternative.
            if current_category == "plat":
                row_text = " ".join(self._clean_text(cell) for cell in cells)
                if "végé" in row_text.lower():
                    for index, (_, menu_date) in columns.items():
                        if index < len(cells):
                            key = menu_date.strftime("%Y%m%d")
                            value = self._clean_text(cells[index])
                            planning[key]["plat_vegetarien"] = re.sub(
                                r"^végé\s*:\s*", "", value, flags=re.IGNORECASE
                            ).strip()
                            if planning[key]["plat_vegetarien"]:
                                planning[key]["repas_vegetarien"] = True

        if not planning:
            raise CantineConnectionError("Menu vide.")

        return {
            "planning": dict(sorted(planning.items())),
            "url": self._url,
            "restaurant_id": self._restaurant_id,
        }

    def validate(self) -> None:
        """Validate the configured restaurant by fetching its menu."""
        self.get_menu(date.today())
