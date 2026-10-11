from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)


class InvalidWebhookSignature(Exception):
    pass


class LineSdkGateway:
    def __init__(self, channel_secret: str, channel_access_token: str) -> None:
        self._parser = WebhookParser(channel_secret)
        self._configuration = Configuration(access_token=channel_access_token)

    def parse_text_events(self, body: str, signature: str) -> list[tuple[str, str, str]]:
        try:
            events = self._parser.parse(body, signature)
        except InvalidSignatureError as exc:
            raise InvalidWebhookSignature from exc
        result: list[tuple[str, str]] = []
        for event in events:
            message = getattr(event, "message", None)
            source = getattr(event, "source", None)
            user_id = getattr(source, "user_id", None)
            reply_token = getattr(event, "reply_token", None)
            message_text = getattr(message, "text", None)
            if user_id and reply_token and isinstance(message_text, str):
                result.append((reply_token, user_id, message_text))
        return result

    def reply_text(self, reply_token: str, text: str) -> None:
        with ApiClient(self._configuration) as api_client:
            MessagingApi(api_client).reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=text)])
            )
