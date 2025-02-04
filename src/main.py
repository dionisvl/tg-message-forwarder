from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
import sys
from config import Config
from utils import handle_message, text_contains_test
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_string_session():
    async with TelegramClient(StringSession(), Config.API_ID, Config.API_HASH) as client:
        await client.start(phone=Config.PHONE_NUMBER)
        return client.session.save()

async def main():
    try:
        with open('sessions/session.txt', 'r') as f:
            session_str = f.read().strip()
            logger.info("Session file found, attempting to use existing session...")
    except FileNotFoundError:
        if not sys.stdin.isatty():
            logger.error("No session found and running in non-interactive mode")
            sys.exit(1)

        logger.info("No session file found, creating new session...")
        session_str = await get_string_session()
        with open('sessions/session.txt', 'w') as f:
            f.write(session_str)

    client = TelegramClient(StringSession(session_str), Config.API_ID, Config.API_HASH)

    @client.on(events.NewMessage(chats=Config.SOURCE_GROUP_ID))
    async def forward_message(event):
        logger.info("New message received, processing...")
        await handle_message(client, event, text_contains_test)

    async with client:
        logger.info("Bot started successfully!")
        await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
