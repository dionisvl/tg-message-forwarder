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

    EXCLUDED_NAMES = os.getenv('EXCLUDED_NAMES', '').split(',')