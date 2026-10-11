from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Venue:
    name: str
    area: str
    budget: str
    vibe: str
    why_go: str
    address: str = ""
    map_url: str = ""


@dataclass(frozen=True, slots=True)
class RecommendationRequest:
    text: str
    area: str | None
    budget: str | None
    vibe_terms: tuple[str, ...]
