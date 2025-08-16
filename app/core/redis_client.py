import json
import redis

# Initialize the client variable as None as it will be created on first use
redis_client = None


def get_redis_client():
    """
    Initializes and returns the Redis client instance.
    This function will only connect to Redis on its first call.
    """
    global redis_client
    if redis_client is None:
        # Move imports and connection logic inside this function
        from .config import REDIS_HOST, REDIS_PORT

        pool = redis.ConnectionPool(
            host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
        )
        redis_client = redis.Redis(connection_pool=pool)
    return redis_client


def set_cache(key: str, value: dict, ttl: int = 3600):
    """Serializes and stores data in Redis with a TTL."""
    client = get_redis_client()  # Get the client instance
    client.set(key, json.dumps(value, default=str), ex=ttl)


def get_cache(key: str) -> dict | None:
    """Retrieves and deserializes data from Redis."""
    client = get_redis_client()  # Get the client instance
    cached_value = client.get(key)
    if cached_value:
        return json.loads(cached_value)
    return None


def delete_cache(key: str):
    """Deletes a key from Redis."""
    client = get_redis_client()  # Get the client instance
    client.delete(key)


# Add the mget/mset functions with the same pattern
def mget_cache(keys: list[str]) -> list:
    if not keys:
        return []
    client = get_redis_client()
    cached_values = client.mget(keys)
    return [json.loads(val) if val else None for val in cached_values]


def mset_cache(data: dict):
    client = get_redis_client()
    pipeline = client.pipeline()
    for key, value in data.items():
        pipeline.set(key, json.dumps(value, default=str), ex=3600)
    pipeline.execute()
