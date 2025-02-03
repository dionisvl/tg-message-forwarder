import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER')
    SOURCE_GROUP_ID = int(os.getenv('SOURCE_GROUP_ID'))
    TARGET_USER_ID = int(os.getenv('TARGET_USER_ID'))
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))