import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER')
    PASSWORD_2FA = os.getenv('2FA_PASSWORD')
    SOURCE_GROUP_ID = int(os.getenv('SOURCE_GROUP_ID'))
    TARGET_USER_ID = int(os.getenv('TARGET_USER_ID'))
    TARGET_USER_NICKNAME = os.getenv('TARGET_USER_NICKNAME')
    ORDER_AMOUNT_THRESHOLD = int(os.getenv('ORDER_AMOUNT_THRESHOLD', 10000))
    # check interval in seconds (default is 300 seconds = 5 minutes)
    CONNECTION_CHECK_INTERVAL = int(os.getenv('CONNECTION_CHECK_INTERVAL', 300))
    
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT_INTERNAL', 5432))
    DB_NAME = os.getenv('DB_NAME', 'tgbot')
    DB_USER = os.getenv('DB_USER', 'tgbot_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'tgbot_secure_2024')
    
    @classmethod
    async def get_excluded_keywords(cls):
        """Get excluded keywords from database"""
        try:
            from database import db_manager
            return await db_manager.get_all_keywords()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting excluded keywords: {e}")
            return []
