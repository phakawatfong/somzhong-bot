from typing import Protocol


class LineGateway(Protocol):
    def parse_text_events(self, body: str, signature: str) -> list[tuple[str, str, str]]: ...

    def reply_text(self, reply_token: str, text: str) -> None: ...
