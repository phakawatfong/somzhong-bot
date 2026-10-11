from collections.abc import Sequence
from typing import Protocol

from somzhong_bot.domain.models import Venue


class VenueCatalog(Protocol):
    def all_venues(self) -> Sequence[Venue]: ...
