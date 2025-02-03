import redis
from config import Config

redis_client = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    decode_responses=True
)

def is_message_processed(message_id: int) -> bool:
    """Check if message was already processed"""
    return bool(redis_client.get(f"msg:{message_id}"))

def mark_message_processed(message_id: int) -> None:
    """Mark message as processed"""
    redis_client.setex(f"msg:{message_id}", 86400, "1")  # TTL: 24 hours