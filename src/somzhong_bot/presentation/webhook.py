from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.concurrency import run_in_threadpool

from somzhong_bot.application.conversation import RecommendationConversation
from somzhong_bot.application.ports import LineGateway
from somzhong_bot.infrastructure.line_sdk_gateway import InvalidWebhookSignature

router = APIRouter()


class WebhookService:
    def __init__(self, gateway: LineGateway, conversation: RecommendationConversation) -> None:
        self._gateway = gateway
        self._conversation = conversation

    def handle(self, body: str, signature: str) -> None:
        events = self._gateway.parse_text_events(body, signature)
        for reply_token, user_id, text in events:
            reply = self._conversation.handle(user_id, text)
            self._gateway.reply_text(reply_token, reply)


def get_webhook_service(request: Request) -> WebhookService:
    service = getattr(request.app.state, "webhook_service", None)
    if service is None:
        raise HTTPException(status_code=503, detail="LINE webhook is not configured")
    return service


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/callback")
async def callback(
    request: Request,
    service: WebhookService = Depends(get_webhook_service),
) -> dict[str, str]:
    body = (await request.body()).decode("utf-8")
    signature = request.headers.get("x-line-signature", "")
    try:
        await run_in_threadpool(service.handle, body, signature)
    except InvalidWebhookSignature:
        raise HTTPException(status_code=400, detail="Invalid LINE webhook signature") from None
    return {"status": "ok"}
