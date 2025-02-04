import redis
from config import Config

def get_redis_client():
    try:
        return redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            decode_responses=True,
            socket_timeout=5,
            retry_on_timeout=True
        )
    except redis.ConnectionError as e:
        print(f"Redis connection error: {e}")
        return None

redis_client = get_redis_client()

def is_message_processed(message_id: int) -> bool:
    """Check if message was already processed"""
    return bool(redis_client.get(f"msg:{message_id}"))

def mark_message_processed(message_id: int) -> None:
    """Mark message as processed"""
    redis_client.setex(f"msg:{message_id}", 86400, "1")  # TTL: 24 hours

async def handle_message(client, event, condition_func):
    if is_message_processed(event.message.id):
        return

    if condition_func(event.message):
        try:
            await client.forward_messages(Config.TARGET_USER_ID, event.message)
            mark_message_processed(event.message.id)
        except Exception as e:
            print(f"Error forwarding: {str(e)}")

def text_contains_test(message):
    return message.text and "тест" in message.text.lower()