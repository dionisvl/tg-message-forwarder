from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, SessionExpiredError
from telethon.sessions import StringSession
from config import Config
from utils import handle_message, text_contains_test
import logging
import asyncio

logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.client = None
        self._running = False
        self._monitoring = False
        self.phone = None
        self.phone_code_hash = None
        self._handler = None
        self._connection_monitor_task = None
        self._session_lost = False
        self._auth_failure_count = 0
        self._max_auth_failures = Config.MAX_AUTH_FAILURES
        self._retry_delay = Config.AUTH_RETRY_DELAY

    def is_running(self):
        return self._running and self.client is not None and self.client.is_connected()

    def is_monitoring(self):
        return self._monitoring
    
    def is_session_lost(self):
        return self._session_lost

    async def _diagnose_session_error(self):
        """Diagnose session authorization error and log details"""
        try:
            me = await self.client.get_me()
            if me is None:
                logger.error("Session error: Unable to get user info - session may be expired or revoked")
            else:
                logger.error(f"Session error: Got user info but not authorized - possible security reset for user {me.phone}")
        except Exception as auth_error:
            logger.error(f"Session error details: {type(auth_error).__name__}: {auth_error}")
            
            error_str = str(auth_error)
            if "UserDeactivated" in error_str:
                logger.error("Session error reason: Account was deactivated")
            elif "AuthKeyUnregistered" in error_str:
                logger.error("Session error reason: Authorization key was unregistered (logged out from another device)")
            elif "SessionExpired" in error_str:
                logger.error("Session error reason: Session has expired")
            elif "SessionRevoked" in error_str:
                logger.error("Session error reason: Session was revoked (password changed or security reset)")
            else:
                logger.error("Session error reason: Unknown authorization error")

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
        self._session_lost = False
        # Start the unified connection monitor task
        self._connection_monitor_task = asyncio.create_task(self._monitor_and_keep_connection())
        logger.info("Bot started successfully with new login")

    async def _monitor_and_keep_connection(self):
        logger.info(f"Starting connection monitor (detailed check interval: {Config.CONNECTION_CHECK_INTERVAL} seconds)")
        last_health_log = 0
        while True:
            if not self.client.is_connected():
                logger.warning("Client disconnected; attempting to reconnect...")
                try:
                    await self.client.connect()
                    logger.info("Reconnection successful")
                except Exception as e:
                    logger.error(f"Error during reconnection attempt: {e}")

            # Detailed connection health check every CONNECTION_CHECK_INTERVAL seconds
            current_time = asyncio.get_running_loop().time()
            if current_time - last_health_log >= Config.CONNECTION_CHECK_INTERVAL:
                # Check authorization with retry mechanism
                auth_result = await self._check_authorization_with_retry()
                if not auth_result:
                    logger.error(f"Authorization failed after {self._max_auth_failures} attempts")
                    self._session_lost = True
                    self._running = False
                    self._monitoring = False
                    # Stop monitoring handler if it exists
                    if self._handler:
                        self.client.remove_event_handler(self._handler)
                        self._handler = None
                    logger.error("Session lost - bot stopped, please re-authenticate")
                    break
                
                try:
                    me = await self.client.get_me()
                    if me is not None:
                        logger.info(f"1 - Logged as {me.first_name}")
                    else:
                        logger.error("1 - User info is None - authorization issue")
                except Exception as e:
                    logger.error(f"Health check error: {e}")

                # Check for group existence and membership 
                try:
                    group = await self.client.get_entity(Config.SOURCE_GROUP_ID)
                    # If group exists, attempt to retrieve its title
                    group_title = getattr(group, 'title', 'Unknown Group')
                    logger.info(f"2 - Membership in: '{group_title}'")
                except Exception as e:
                    logger.error(f"Group check error: {e}")

                logger.info(f"3 - Is running: '{self._running}'")
                logger.info(f"4 - Monitoring: '{self._monitoring}'")

                last_health_log = current_time

            await asyncio.sleep(1)

    async def _check_authorization_with_retry(self):
        """Check authorization with retry mechanism using real API call instead of is_user_authorized()"""
        for attempt in range(self._max_auth_failures):
            try:
                # Use get_me() instead of is_user_authorized() for reliable check
                me = await self.client.get_me()
                if me is not None:
                    # Reset failure count on success
                    self._auth_failure_count = 0
                    logger.debug(f"Authorization check successful - user: {me.first_name}")
                    return True
                else:
                    logger.warning(f"Authorization check failed - get_me() returned None (attempt {attempt + 1}/{self._max_auth_failures})")
                
            except Exception as e:
                logger.warning(f"Authorization check failed with error (attempt {attempt + 1}/{self._max_auth_failures}): {e}")
                
                # Check if it's a recoverable error
                error_str = str(e)
                if any(recoverable in error_str for recoverable in [
                    "AuthKeyUnregistered", "SessionExpired", "SessionRevoked", 
                    "ConnectionError", "TimeoutError", "NetworkError"
                ]):
                    # If not the last attempt, try to recover
                    if attempt < self._max_auth_failures - 1:
                        logger.info("Attempting session recovery for recoverable error...")
                        if await self._attempt_session_recovery():
                            logger.info("Session recovery successful")
                            self._auth_failure_count = 0
                            return True
                        
                        logger.warning(f"Session recovery failed, waiting {self._retry_delay} seconds before retry...")
                        await asyncio.sleep(self._retry_delay)
                else:
                    logger.error(f"Non-recoverable authorization error: {e}")
                    break
        
        self._auth_failure_count = self._max_auth_failures
        return False
    
    async def _attempt_session_recovery(self):
        """Attempt to recover session by reconnecting with existing session file"""
        try:
            logger.info("Attempting to recover session from file...")
            
            # Read existing session
            with open('sessions/session.txt', 'r') as f:
                session_str = f.read().strip()
            
            if not session_str:
                logger.error("Session file is empty")
                return False
            
            # Disconnect current client
            if self.client and self.client.is_connected():
                await self.client.disconnect()
            
            # Create new client with saved session
            self.client = TelegramClient(StringSession(session_str), Config.API_ID, Config.API_HASH)
            await self.client.connect()
            
            # Test session with real API call instead of is_user_authorized()
            try:
                me = await self.client.get_me()
                if me is not None:
                    logger.info(f"Session recovery successful - authenticated as {me.first_name}")
                    return True
                else:
                    logger.error("Session recovery failed - get_me() returned None")
                    return False
            except Exception as auth_error:
                logger.error(f"Session recovery failed - API call error: {auth_error}")
                await self._diagnose_session_error()
                return False
                
        except FileNotFoundError:
            logger.error("Session file not found during recovery attempt")
            return False
        except Exception as e:
            logger.error(f"Error during session recovery: {e}")
            return False


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

                # Test session with real API call instead of is_user_authorized()
                try:
                    me = await self.client.get_me()
                    if me is None:
                        logger.error("Existing session is not authorized - get_me() returned None")
                        await self._diagnose_session_error()
                        self._session_lost = True
                        return False
                    else:
                        logger.info(f"Session validated successfully - authenticated as {me.first_name}")
                except Exception as auth_error:
                    logger.error(f"Existing session is not authorized - API error: {auth_error}")
                    await self._diagnose_session_error()
                    self._session_lost = True
                    return False

                self._running = True
                self._session_lost = False
                # Start the unified connection monitor task
                self._connection_monitor_task = asyncio.create_task(self._monitor_and_keep_connection())
                logger.info("Telethon started successfully with existing session")

                is_monitoring = await self.toggle_monitoring()
                if is_monitoring:
                    logger.info("Telethon group monitoring started")
                else:
                    logger.error("Error starting Telethon group monitoring")
                    raise Exception("Error starting Telethon group monitoring")

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
