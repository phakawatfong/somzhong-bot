import csv
from pathlib import Path

from pydantic import ValidationError

from somzhong_bot.domain.models import Venue


class CsvVenueCatalog:
    def __init__(self, path: Path) -> None:
        self._path = path

    def all_venues(self) -> list[Venue]:
        with self._path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            venues: list[Venue] = []
            for line_number, row in enumerate(reader, start=2):
                try:
                    venues.append(Venue.model_validate({
                        "name": row.get("name"),
                        "area": row.get("area"),
                        "budget": row.get("budget"),
                        "vibe": row.get("vibe"),
                        "why_go": row.get("why_go"),
                        "address": row.get("address"),
                        "map_url": row.get("map_url"),
                    }))
                except ValidationError as exc:
                    raise ValueError(f"Invalid venue data at CSV line {line_number}: {exc}") from exc
            return venues
