import csv
from pathlib import Path

from somzhong_bot.domain.models import Venue

REQUIRED_FIELDS = {"name", "area", "budget", "vibe", "why_go"}


class CsvVenueCatalog:
    def __init__(self, path: Path) -> None:
        self._path = path

    def all_venues(self) -> list[Venue]:
        with self._path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fields = set(reader.fieldnames or [])
            missing = REQUIRED_FIELDS - fields
            if missing:
                raise ValueError(f"Venue CSV is missing required columns: {', '.join(sorted(missing))}")
            venues: list[Venue] = []
            for line_number, row in enumerate(reader, start=2):
                values = {key: (row.get(key) or "").strip() for key in REQUIRED_FIELDS}
                if not all(values.values()):
                    raise ValueError(f"Venue CSV row {line_number} has an empty required value")
                budget = values["budget"].casefold()
                if budget not in {"low", "medium", "high"}:
                    raise ValueError(f"Venue CSV row {line_number} has unsupported budget: {values['budget']}")
                venues.append(Venue(
                    name=values["name"], area=values["area"], budget=budget,
                    vibe=values["vibe"], why_go=values["why_go"],
                    address=(row.get("address") or "").strip(),
                    map_url=(row.get("map_url") or "").strip(),
                ))
            return venues
