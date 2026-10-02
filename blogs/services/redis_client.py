import os
import redis

REDIS_URL = os.environ.get("REDIS_URL")

def get_redis():
    if not REDIS_URL:
        return None

    return redis.Redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=0.2,
        socket_timeout=0.2,
    )