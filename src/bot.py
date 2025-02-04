from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, SessionExpiredError
from telethon.sessions import StringSession
from config import Config
from utils import handle_message, text_contains_test
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.client = None
        self._running = False
        self._monitoring = False
        self.phone = None
        self.phone_code_hash = None
        self._handler = None
        self._client_task = None

    def is_running(self):
        return self._running and self.client is not None and self.client.is_connected()

    def is_monitoring(self):
        return self._monitoring

    async def toggle_monitoring(self):
        if not self.is_running():
            raise Exception("Bot must be running to toggle monitoring")

        self._monitoring = not self._monitoring

        if self._monitoring:
            @self.client.on(events.NewMessage(chats=Config.SOURCE_GROUP_ID))
            async def forward_message(event):
                logger.info("New message received, processing...")
                await handle_message(self.client, event, text_contains_test)
            self._handler = forward_message
            logger.info("Monitoring started")
        else:
            if self._handler:
                self.client.remove_event_handler(self._handler)
                self._handler = None
            logger.info("Monitoring stopped")

        return self._monitoring

    async def start_login(self, phone):
        if self.client:
            await self.client.disconnect()
            self.client = None

        self.client = TelegramClient(StringSession(), Config.API_ID, Config.API_HASH)
        await self.client.connect()
        self.phone = phone
        code_request = await self.client.send_code_request(phone)
        self.phone_code_hash = code_request.phone_code_hash
        logger.info("Login initiated")

    async def verify_code(self, code):
        if not self.client:
            raise Exception("Must call start_login first")

        try:
            logger.info("Attempting to sign in with code...")
            await self.client.sign_in(
                phone=self.phone,
                code=code,
                phone_code_hash=self.phone_code_hash
            )
        except SessionPasswordNeededError:
            logger.info("2FA password required, attempting to sign in with password...")
            await self.client.sign_in(password=Config.PASSWORD_2FA)

        session_str = self.client.session.save()
        with open('sessions/session.txt', 'w') as f:
            f.write(session_str)

        self._running = True
        self._client_task = asyncio.create_task(self._keep_client_running())
        logger.info("Bot started successfully")

    async def _keep_client_running(self):
        """Keep the client running in background"""
        try:
            logger.info("Starting client background task")
            while True:
                if not self.client.is_connected():
                    await self.client.connect()
                await asyncio.sleep(1)  # Check connection every second
        except Exception as e:
            logger.error(f"Client task error: {e}")
            self._running = False
            self._monitoring = False

    async def start_existing_session(self):
        """Start bot with existing session if available"""
        try:
            with open('sessions/session.txt', 'r') as f:
                session_str = f.read().strip()
                logger.info("Session file found, attempting to use existing session...")

                if self.client:
                    await self.client.disconnect()

                self.client = TelegramClient(StringSession(session_str), Config.API_ID, Config.API_HASH)
                await self.client.connect()

                if not await self.client.is_user_authorized():
                    logger.error("Existing session is not authorized")
                    return False

                self._running = True
                self._client_task = asyncio.create_task(self._keep_client_running())
                logger.info("Bot started successfully with existing session")
                return True

        except FileNotFoundError:
            logger.error("No session file found")
            return False
        except SessionExpiredError:
            logger.error("Session expired")
            return False
        except Exception as e:
            logger.error(f"Error starting with existing session: {e}")
            return False