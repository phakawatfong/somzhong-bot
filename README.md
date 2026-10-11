# Somzhong Bot

A small FastAPI LINE bot that recommends beer venues from a curated CSV catalog. The app follows Clean Architecture: recommendation rules live in the application layer, while FastAPI, LINE, and CSV are adapters.

## Requirements

- Python 3.11+
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
