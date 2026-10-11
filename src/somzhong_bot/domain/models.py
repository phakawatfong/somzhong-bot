from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

BudgetLevel = Literal["low", "medium", "high"]


class Venue(BaseModel):
    """Validated venue record loaded from the local catalog."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    name: str = Field(min_length=1)
    area: str = Field(min_length=1)
    budget: BudgetLevel
    vibe: str = Field(min_length=1)
    why_go: str = Field(min_length=1)
    address: str | None = None
    map_url: HttpUrl | None = None

    @field_validator("budget", mode="before")
    @classmethod
    def normalize_budget(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().casefold()
        return value

    @field_validator("address", "map_url", mode="before")
    @classmethod
    def empty_optional_values_to_none(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip() or None
        return value


class RecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    text: str = Field(min_length=1)
    area: str | None = None
    budget: BudgetLevel | None = None
    vibe_terms: tuple[str, ...] = ()
