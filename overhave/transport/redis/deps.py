import logging

from redis import Redis
from redis.sentinel import Sentinel

from overhave.transport.redis.settings import OverhaveRedisSentinelSettings, OverhaveRedisSettings

logger = logging.getLogger(__name__)


def make_sentinel_master(settings: OverhaveRedisSentinelSettings) -> Redis:  # type: ignore
    logger.info("Connecting to redis through sentinel %s", settings.urls)
    url_tuples = [(url.host, url.port) for url in settings.urls]
    sentinel = Sentinel(url_tuples, socket_timeout=settings.socket_timeout.total_seconds(), retry_on_timeout=True)
    return sentinel.master_for(settings.master_set, password=settings.redis_password, db=settings.redis_db)


def make_regular_redis(redis_settings: OverhaveRedisSettings) -> Redis:  # type: ignore
    return Redis.from_url(
        str(redis_settings.redis_url),
        db=redis_settings.redis_db,
        socket_timeout=redis_settings.socket_timeout.total_seconds(),
    )


def make_redis(redis_settings: OverhaveRedisSettings, sentinel_settings: OverhaveRedisSentinelSettings) -> Redis:  # type: ignore  # noqa: E501
    if sentinel_settings.enabled:
        return make_sentinel_master(sentinel_settings)

    return make_regular_redis(redis_settings)
