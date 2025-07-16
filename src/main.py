from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import sys
from config import Config
from src.app import bot_manager
import logging

logger = logging.getLogger(__name__)

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

    # By default, app working immediately after start. But additionally user can enable/disable it from admin panel.
    await bot_manager.toggle_monitoring()

    async with client:
        logger.info("Bot started successfully!")
        await client.run_until_disconnected()

async def get_string_session():
    async with TelegramClient(StringSession(), Config.API_ID, Config.API_HASH) as client:
        await client.start(phone=Config.PHONE_NUMBER)
        return client.session.save()

if __name__ == '__main__':
    asyncio.run(main())
