import os
from pathlib import Path

from fastapi import FastAPI

from somzhong_bot.application.conversation import InMemoryConversationStore, RecommendationConversation
from somzhong_bot.application.recommendations import RecommendationService
from somzhong_bot.application.ports import LineGateway
from somzhong_bot.domain.ports import VenueCatalog
from somzhong_bot.infrastructure.csv_catalog import CsvVenueCatalog
from somzhong_bot.infrastructure.line_sdk_gateway import LineSdkGateway
from somzhong_bot.presentation.webhook import WebhookService, router


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def create_app(
    *,
    catalog: VenueCatalog | None = None,
    gateway: LineGateway | None = None,
    conversation_store: InMemoryConversationStore | None = None,
) -> FastAPI:
    app = FastAPI(title="Somzhong Bot", version="0.1.0")
    venue_catalog = catalog or CsvVenueCatalog(PROJECT_ROOT / "data" / "venues.csv")
    recommendation_service = RecommendationService(venue_catalog)
    store = conversation_store or InMemoryConversationStore()
    conversation = RecommendationConversation(recommendation_service, store)

    if gateway is None:
        channel_secret = os.getenv("LINE_CHANNEL_SECRET", "")
        access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
        if channel_secret and access_token:
            gateway = LineSdkGateway(channel_secret, access_token)

    if gateway is not None:
        app.state.webhook_service = WebhookService(gateway, conversation)
    app.include_router(router)
    return app


app = create_app()
