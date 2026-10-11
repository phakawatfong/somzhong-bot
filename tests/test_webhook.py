from fastapi.testclient import TestClient

from somzhong_bot.main import create_app


class _Gateway:
    def parse_text_events(self, body: str, signature: str) -> list[tuple[str, str, str]]:
        if signature != "valid":
            from somzhong_bot.infrastructure.line_sdk_gateway import InvalidWebhookSignature
            raise InvalidWebhookSignature
        if body == "empty":
            return []
        return [("reply-token", "user-1", "Ari")]

    def reply_text(self, reply_token: str, text: str) -> None:
        self.reply = (reply_token, text)


def test_health_and_webhook_dependency_injection() -> None:
    gateway = _Gateway()
    client = TestClient(create_app(gateway=gateway))
    assert client.get("/health").json() == {"status": "ok"}
    response = client.post("/callback", headers={"x-line-signature": "valid"}, content="{}")
    assert response.status_code == 200
    assert gateway.reply[0] == "reply-token"
    assert "THE PICKLES ARI" in gateway.reply[1]


def test_invalid_signature_is_rejected() -> None:
    client = TestClient(create_app(gateway=_Gateway()))
    response = client.post("/callback", headers={"x-line-signature": "bad"}, content="{}")
    assert response.status_code == 400


def test_callback_is_unavailable_without_line_configuration(monkeypatch) -> None:
    monkeypatch.delenv("LINE_CHANNEL_SECRET", raising=False)
    monkeypatch.delenv("LINE_CHANNEL_ACCESS_TOKEN", raising=False)
    client = TestClient(create_app())
    response = client.post("/callback", headers={"x-line-signature": "x"}, content="{}")
    assert response.status_code == 503


def test_unhandled_events_do_not_trigger_replies() -> None:
    gateway = _Gateway()
    client = TestClient(create_app(gateway=gateway))
    response = client.post("/callback", headers={"x-line-signature": "valid"}, content="empty")
    assert response.status_code == 200
    assert not hasattr(gateway, "reply")
