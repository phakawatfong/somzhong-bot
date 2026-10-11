import re
from collections.abc import Sequence

from somzhong_bot.domain.models import Venue
from somzhong_bot.domain.ports import VenueCatalog

BUDGET_ALIASES = {
    "low": {"low", "cheap", "affordable", "budget"},
    "medium": {"medium", "moderate", "mid-range", "midrange"},
    "high": {"high", "expensive", "premium"},
}
STOP_WORDS = {
    "a", "an", "and", "any", "beer", "best", "can", "for", "find", "good",
    "i", "in", "is", "me", "near", "of", "on", "place", "recommend", "should",
    "somewhere", "the", "there", "to", "tonight", "venue", "want", "where", "with",
}


def _words(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.casefold()))


def _query_budget(text: str) -> str | None:
    words = _words(text)
    for level, aliases in BUDGET_ALIASES.items():
        if words.intersection(aliases):
            return level
    return None


def _find_area(text: str, venues: Sequence[Venue]) -> str | None:
    folded = text.casefold()
    areas = sorted({venue.area for venue in venues}, key=len, reverse=True)
    for area in areas:
        if re.search(rf"(?<![a-z0-9]){re.escape(area.casefold())}(?![a-z0-9])", folded):
            return area
    return None


def _vibe_terms(text: str, area: str | None, budget: str | None) -> set[str]:
    terms = _words(text) - STOP_WORDS
    if area:
        terms -= _words(area)
    if budget:
        terms -= _words(budget)
        for aliases in BUDGET_ALIASES.values():
            terms -= aliases
    return terms


class RecommendationService:
    def __init__(self, catalog: VenueCatalog) -> None:
        self._catalog = catalog

    def areas(self) -> list[str]:
        return sorted({venue.area for venue in self._catalog.all_venues()})

    def recommend(self, text: str) -> tuple[str | None, list[Venue]]:
        venues = list(self._catalog.all_venues())
        if not venues:
            return None, []
        area = _find_area(text, venues)
        if area is None:
            return None, []

        budget = _query_budget(text)
        vibe_terms = _vibe_terms(text, area, budget)
        candidates = [v for v in venues if v.area.casefold() == area.casefold()]
        if budget:
            candidates = [v for v in candidates if v.budget.casefold() == budget]

        # Only apply descriptive vibe matching for words actually present in the catalog.
        catalog_terms = set().union(*(_words(f"{v.vibe} {v.why_go} {v.name}") for v in candidates)) if candidates else set()
        requested_vibe = vibe_terms & catalog_terms
        if requested_vibe:
            candidates = [
                v for v in candidates
                if requested_vibe & _words(f"{v.vibe} {v.why_go} {v.name}")
            ]
        return area, candidates[:3]
