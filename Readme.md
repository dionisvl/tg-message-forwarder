# Telegram Message Forwarder

Async Telegram message forwarding service with a small web admin panel and PostgreSQL-backed runtime configuration.

The project is built for private group monitoring workflows: it connects through a Telegram user session, filters messages by configured rules, and forwards matching messages to a target user. Runtime settings such as excluded keywords are managed through HTTP endpoints and persisted in PostgreSQL.

## Stack

- Python 3.12
- Telethon
- Quart
- PostgreSQL 17
- Docker Compose

## Features

- Telegram group monitoring through a user account session
- Forwarding to a configured target user
- Excluded keyword management stored in PostgreSQL
- Web admin panel for operational configuration
- Docker Compose setup for the app and database
- Persistent Telegram sessions mounted from `./sessions`
- Basic restart helper for simple VPS deployments

## Project Layout

```text
.
├── src/                  # application code
├── templates/            # admin UI templates
├── migrations/           # database migrations
├── compose.yml           # app + PostgreSQL services
├── Dockerfile            # Python application image
├── Makefile              # local operational commands
├── restart.sh            # simple restart helper
├── test.py
└── test_excluded_keywords.py
```

## Quick Start

```bash
git clone https://github.com/dionisvl/tg-message-forwarder.git
cd tg-message-forwarder

cp .env.example .env
# Fill in Telegram credentials, target user, source group, and admin settings.

make up
```

The admin panel is exposed on:

```text
http://127.0.0.1:5001
```

Common commands:

```bash
make up       # start services
make down     # stop services
make build    # rebuild and start
make sh       # shell inside the web container
```

## Configuration

Core environment variables:

| Variable | Purpose |
|---|---|
| `API_ID` / `API_HASH` | Telegram API credentials from `my.telegram.org` |
| `PHONE_NUMBER` | Telegram account phone number used for the user session |
| `2FA_PASSWORD` | Telegram two-factor password, if enabled |
| `SOURCE_GROUP_ID` | Telegram group/channel id to monitor |
| `TARGET_USER_ID` | Telegram user id that receives forwarded messages |
| `TARGET_USER_NICKNAME` | Optional target nickname used by the app UI/rules |
| `ORDER_AMOUNT_THRESHOLD` | Numeric threshold used by message matching logic |
| `EXCLUDED_NAMES` | Comma-separated names excluded from matching |
| `CONNECTION_CHECK_INTERVAL` | Connection check interval in seconds |
| `MAX_AUTH_FAILURES` | Max authorization attempts before stopping retries |
| `AUTH_RETRY_DELAY` | Delay between authorization retries, in seconds |
| `ADMIN_PASSWORD` / `ADMIN_SECRET` | Admin panel credentials/secrets |
| `BOT_TOKEN` | Bot token used only by helper/testing flows |
| `DB_*` | PostgreSQL connection settings |

Use `.env.example` as the source of truth for supported variables.

## Getting Telegram IDs

Telegram API credentials:

1. Open `https://my.telegram.org`.
2. Log in with the Telegram account that will own the session.
3. Open API development tools.
4. Create an application and copy `API_ID` and `API_HASH`.

Source group id:

1. Open `https://web.telegram.org`.
2. Open the target group.
3. Check the URL segment after `#`; group ids are usually negative numbers.

Target user id:

1. Send a message to `@userinfobot`.
2. Copy the numeric id from the response.

Bot token for helper/test flows:

1. Open `@BotFather`.
2. Create a bot with `/newbot`.
3. Copy the token into `BOT_TOKEN` if the helper flow needs it.

## API

Excluded keywords:

```http
GET /api/excluded_keywords
```

```json
{
  "keywords": ["keyword1", "keyword2"]
}
```

```http
POST /api/excluded_keywords
Content-Type: application/json

{
  "keyword": "new_keyword"
}
```

```http
DELETE /api/excluded_keywords/{keyword}
```

## Operations

For a simple VPS deployment, the repository includes `restart.sh`. If you use cron, keep logs outside the container lifecycle:

```bash
chmod +x /home/tgbot/restart.sh
crontab -e
```

```cron
0 3 * * * /home/tgbot/restart.sh >> /home/tgbot/logs/restart.log 2>&1
```

The Compose file publishes PostgreSQL on `DB_PORT_EXTERNAL`. For production-like deployments, restrict that port at the firewall level or remove the host port mapping if external database access is not required.

## Local Python Environment

Docker Compose is the default path. For direct local development:

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Security Notes

- Do not commit `.env`, Telegram session files, or runtime logs.
- Treat Telegram user sessions like credentials.
- Set a strong `ADMIN_PASSWORD` and `ADMIN_SECRET` before exposing the admin panel.
- Avoid exposing PostgreSQL publicly unless there is a specific operational reason.

