from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, SessionExpiredError
from telethon.sessions import StringSession
from config import Config
from utils import handle_message, text_contains_test
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.client = None
        self._running = False

    async def start_login(self, phone):
        if not self.client:
            self.client = TelegramClient(StringSession(), Config.API_ID, Config.API_HASH)
            await self.client.connect()
            await self.client.send_code_request(phone)

    def is_running(self):
        return self._running

    async def verify_code(self, code):
        if not self.client:
            raise Exception("Must call start_login first")
        try:
            logger.info("Attempting to sign in with code...")
            await self.client.sign_in(code=code)
        except SessionPasswordNeededError:
            logger.info("2FA password required, attempting to sign in with password...")
            await self.client.sign_in(password=Config.PASSWORD_2FA)

        session_str = self.client.session.save()
        with open('sessions/session.txt', 'w') as f:
            f.write(session_str)

        self._running = True

        @self.client.on(events.NewMessage(chats=Config.SOURCE_GROUP_ID))
        async def forward_message(event):
            logger.info("New message received, processing...")
            await handle_message(self.client, event, text_contains_test)

        logger.info("Bot started successfully, running until disconnected...")
        await self.client.run_until_disconnected()

    async def start_existing_session(self):
        try:
            with open('sessions/session.txt', 'r') as f:
                session_str = f.read().strip()
                logger.info("Session file found, attempting to use existing session...")
                self.client = TelegramClient(StringSession(session_str), Config.API_ID, Config.API_HASH)
                await self.client.connect()

                if not await self.client.is_user_authorized():
                    logger.error("Existing session is not authorized. Please log in again.")
                    return False

                self._running = True

                @self.client.on(events.NewMessage(chats=Config.SOURCE_GROUP_ID))
                async def forward_message(event):
                    logger.info("New message received, processing...")
                    await handle_message(self.client, event, text_contains_test)

                logger.info("Bot started successfully with existing session, running until disconnected...")
                await self.client.run_until_disconnected()
                return True

        except FileNotFoundError:
            logger.error("No session file found.")
            return False
        except SessionExpiredError:
            logger.error("Session expired. Please log in again.")
            return False
        except Exception as e:
            logger.error(f"Error starting with existing session: {e}")
            return False