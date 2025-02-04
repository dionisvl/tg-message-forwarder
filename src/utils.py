import redis
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

from config import Config
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_redis_client():
    try:
        logger.info("Attempting to connect to Redis...")
        client = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            decode_responses=True,
            socket_timeout=5,
            retry_on_timeout=True
        )
        logger.info("Redis connection established successfully.")
        return client
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
        return None

redis_client = get_redis_client()

def is_message_processed(message_id: int) -> bool:
    """Check if message was already processed"""
    logger.info(f"Checking if message {message_id} was processed...")
    return bool(redis_client.get(f"msg:{message_id}"))

def mark_message_processed(message_id: int) -> None:
    """Mark message as processed"""
    logger.info(f"Marking message {message_id} as processed...")
    redis_client.setex(f"msg:{message_id}", 86400, "1")  # TTL: 24 hours

async def handle_message(client, event, condition_func):
    logger.info("Checking conditions")
    if condition_func(event.message):
        try:
            logger.info("Message forwarding started!")
            target_entity = await client.get_input_entity(Config.TARGET_USER_NICKNAME)
            await client.forward_messages(target_entity, event.message)
            logger.info("Message forwarded successfully!")

            # Adding a like reaction to the message
            # await client(SendReactionRequest(
            #     peer=event.message.peer_id,
            #     msg_id=event.message.id,
            #     reaction=[ReactionEmoji(emoticon='👍')]
            # ))

            if event.message.buttons:
                await event.message.click(text="Забрать заказ")
                logger.info("Button pressed successfully!")

        except Exception as e:
            logger.info(f"Error forwarding: {str(e)}")
    logger.info("Message processed.")

def text_contains_test(message):
    logger.info("Checking message " + message.text)
    match = re.search(r"Сумма заказа:\s*(\d+)", message.text)
    if match:
        order_amount = int(match.group(1))
        return order_amount > Config.ORDER_AMOUNT_THRESHOLD
    return False
