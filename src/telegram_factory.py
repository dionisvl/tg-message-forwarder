from telethon import TelegramClient
from telethon.sessions import StringSession
from config import Config

class TelegramClientFactory:
    @staticmethod
    async def create_client(session_str=None):
        session = StringSession(session_str) if session_str else StringSession()
        client = TelegramClient(session, Config.API_ID, Config.API_HASH)
        await client.connect()
        return client
    
    @staticmethod
    async def check_authorization(client):
        try:
            return await client.get_me() is not None
        except:
            return False
    
    @staticmethod
    async def get_user_info(client):
        try:
            me = await client.get_me()
            return {'first_name': me.first_name} if me else None
        except:
            return None
    
    @staticmethod
    async def diagnose_session_error(client):
        try:
            me = await client.get_me()
            return "Unable to get user info" if me is None else f"Security reset for {me.phone}"
        except Exception as e:
            error_str = str(e)
            if "UserDeactivated" in error_str:
                return "Account deactivated"
            elif "AuthKeyUnregistered" in error_str:
                return "Logged out from another device"
            elif "SessionExpired" in error_str:
                return "Session expired"
            elif "SessionRevoked" in error_str:
                return "Password changed"
            return f"Unknown error: {type(e).__name__}"