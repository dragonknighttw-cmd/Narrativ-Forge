from redis import Redis

from ..core.config import settings


def create_redis_client(redis_url: str | None = None) -> Redis:
    configured_url = settings.redis_url if redis_url is None else redis_url
    if not configured_url:
        raise RuntimeError("REDIS_URL must be configured before using Redis")
    return Redis.from_url(configured_url, protocol=2)
