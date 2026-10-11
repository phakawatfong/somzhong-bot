from dataclasses import dataclass

from somzhong_bot.application.recommendations import RecommendationService
from somzhong_bot.domain.models import Venue


@dataclass(slots=True)
class PendingRequest:
    original_text: str


class InMemoryConversationStore:
    def __init__(self) -> None:
        self._pending: dict[str, PendingRequest] = {}

    def get(self, user_id: str) -> PendingRequest | None:
        return self._pending.get(user_id)

    def set(self, user_id: str, pending: PendingRequest) -> None:
        self._pending[user_id] = pending

    def clear(self, user_id: str) -> None:
        self._pending.pop(user_id, None)


class RecommendationConversation:
    def __init__(self, service: RecommendationService, store: InMemoryConversationStore) -> None:
        self._service = service
        self._store = store

    def handle(self, user_id: str, text: str) -> str:
        pending = self._store.get(user_id)
        combined = f"{pending.original_text} {text}" if pending else text
        area, venues = self._service.recommend(combined)

        if area is None:
            self._store.set(user_id, PendingRequest(original_text=combined))
            areas = ", ".join(self._service.areas())
            if areas:
                return f"Which Bangkok area should I look in? I currently have venues in {areas}."
            return "I don’t have any venues in my catalog yet."

        self._store.clear(user_id)
        if not venues:
            return f"I don’t have a match in {area} with those preferences. Try a nearby area or a broader budget."
        return "Here are a few options:\n\n" + "\n\n".join(self._format(v) for v in venues)

    @staticmethod
    def _format(venue: Venue) -> str:
        result = f"{venue.name} — {venue.area}\n{venue.why_go}"
        if venue.map_url:
            result += f"\nMap: {venue.map_url}"
        return result
