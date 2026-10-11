# Somzhong Bot

A small FastAPI LINE bot that recommends beer venues from a curated CSV catalog. The app follows Clean Architecture: recommendation rules live in the application layer, while FastAPI, LINE, and CSV are adapters.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

## Setup

```sh
uv sync
cp .env.example .env
```

Set `LINE_CHANNEL_SECRET` and `LINE_CHANNEL_ACCESS_TOKEN` in `.env`. Keep `.env` private.

## Run locally

```sh
uv run --env-file .env uvicorn somzhong_bot.main:app --reload --app-dir src
```

The webhook endpoint is `POST /callback`; health check is `GET /health`. To test with LINE, expose the local server through a public HTTPS tunnel and set that URL plus `/callback` as the webhook URL in LINE Developers Console.

## Venue catalog

Edit `data/venues.csv`. Required fields are `name`, `area`, `budget`, `vibe`, and `why_go`. `address` and `map_url` are optional. Budget values are relative labels (`low`, `medium`, `high`); vibe remains descriptive text. Recommendations are only based on this catalog; the bot does not verify current opening hours.

## Tests

```sh
uv run pytest
```


## Container deployment

The root `Dockerfile` builds one image for local Docker, ECS/Fargate, or AWS Lambda. It includes the AWS Lambda Web Adapter while keeping the same Uvicorn command for normal container hosting.

Build and run it locally:

```sh
docker build -t somzhong-bot:local .
docker run --rm -p 8000:8000 --env-file .env somzhong-bot:local
```

For ECS/Fargate, push this image to Amazon ECR and configure the service to send traffic to container port `8000`. For Lambda, use the same image from ECR as the function package and connect an API Gateway HTTP API route to the function. Configure `LINE_CHANNEL_SECRET` and `LINE_CHANNEL_ACCESS_TOKEN` in the AWS service settings or through AWS Secrets Manager; do not copy `.env` into the image.

The current conversation state is in process memory. It can be lost when a container restarts, and it is not shared across multiple ECS tasks or Lambda execution environments. Use a shared store such as DynamoDB before relying on multi-instance or durable conversations.
