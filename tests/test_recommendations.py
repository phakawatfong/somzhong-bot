from pathlib import Path

from somzhong_bot.application.conversation import InMemoryConversationStore, RecommendationConversation
from somzhong_bot.application.recommendations import RecommendationService
from somzhong_bot.domain.models import Venue
from somzhong_bot.infrastructure.csv_catalog import CsvVenueCatalog

DATA = Path(__file__).parents[1] / "data" / "venues.csv"


def test_seed_catalog_loads_two_venues_and_map_links() -> None:
    venues = CsvVenueCatalog(DATA).all_venues()
    assert [venue.area for venue in venues] == ["saphan khwai", "ari"]
    assert all(venue.budget == "medium" for venue in venues)
    assert all(venue.map_url.startswith("https://") for venue in venues)


def test_asks_for_area_then_uses_follow_up() -> None:
    service = RecommendationService(CsvVenueCatalog(DATA))
    conversation = RecommendationConversation(service, InMemoryConversationStore())
    assert "Which Bangkok area" in conversation.handle("user-1", "Where should I drink beer tonight?")
    reply = conversation.handle("user-1", "Ari")
    assert "THE PICKLES ARI" in reply
    assert "Map: https://maps.app.goo.gl/" in reply


def test_budget_filter_can_return_no_matches() -> None:
    service = RecommendationService(CsvVenueCatalog(DATA))
    area, venues = service.recommend("high budget in Ari")
    assert area == "ari"
    assert venues == []


def test_descriptive_vibe_matches_catalog_copy() -> None:
    service = RecommendationService(CsvVenueCatalog(DATA))
    area, venues = service.recommend("casual Ari")
    assert area == "ari"
    assert [venue.name for venue in venues] == ["THE PICKLES ARI"]


def test_conversation_state_is_per_user() -> None:
    catalog = _StaticCatalog([Venue("A", "ari", "medium", "casual", "cozy")])
    conversation = RecommendationConversation(RecommendationService(catalog), InMemoryConversationStore())
    conversation.handle("u1", "beer tonight")
    conversation.handle("u2", "beer tonight")
    assert "A" in conversation.handle("u1", "Ari")
    assert "Which Bangkok area" in conversation.handle("u2", "still deciding")


class _StaticCatalog:
    def __init__(self, venues: list[Venue]) -> None:
        self._venues = venues

    def all_venues(self) -> list[Venue]:
        return self._venues


def test_results_are_limited_to_three() -> None:
    venues = [Venue(f"Venue {i}", "ari", "medium", "casual", "cozy") for i in range(5)]
    area, matches = RecommendationService(_StaticCatalog(venues)).recommend("Ari")
    assert area == "ari"
    assert len(matches) == 3
