# app/core/circuit_breaker.py
from pybreaker import CircuitBreaker, CircuitRedisStorage
import redis  # Синхронный клиент для Circuit Breaker
import redis.asyncio as redis_async  # Асинхронный клиент для других операций
from app.core.config import settings
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Singleton синхронный клиент Redis для Circuit Breaker
_sync_redis_client = None

def get_sync_redis_client():
    global _sync_redis_client
    if _sync_redis_client is None:
        try:
            _sync_redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                encoding="utf-8",
            )
            logger.info("Sync Redis client initialized successfully for Circuit Breaker")
        except Exception as e:
            logger.error(f"Failed to connect to Redis for Circuit Breaker: {e}")
            raise
    return _sync_redis_client

# Singleton асинхронный клиент Redis для кэширования
_async_redis_client = None

async def get_async_redis_client():
    global _async_redis_client
    if _async_redis_client is None:
        try:
            _async_redis_client = await redis_async.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Async Redis client initialized successfully for caching")
        except Exception as e:
            logger.error(f"Failed to connect to Redis for caching: {e}")
            raise
    return _async_redis_client

async def is_client_closed(client):
    return await client.is_closed() if client else True

CIRCUIT_BREAKERS = {
    "weather": CircuitBreaker(fail_max=5, reset_timeout=30, state_storage=CircuitRedisStorage(state="closed", redis_object=get_sync_redis_client())),
    "news": CircuitBreaker(fail_max=5, reset_timeout=30, state_storage=CircuitRedisStorage(state="closed", redis_object=get_sync_redis_client())),
    "geocoding": CircuitBreaker(fail_max=5, reset_timeout=30, state_storage=CircuitRedisStorage(state="closed", redis_object=get_sync_redis_client())),
    "currency": CircuitBreaker(fail_max=5, reset_timeout=30, state_storage=CircuitRedisStorage(state="closed", redis_object=get_sync_redis_client()))
}

async def with_circuit_breaker(service_name: str, func, *args, **kwargs):
    breaker = CIRCUIT_BREAKERS[service_name]
    logger.info(f"Circuit Breaker for {service_name}: state={breaker.current_state}, failures={breaker.fail_counter}")

    
    loop = asyncio.get_running_loop()

    if asyncio.iscoroutinefunction(func):
        def sync_wrapper():
            try:
                return asyncio.run(func(*args, **kwargs))
            except Exception as e:
                raise e 
        return await loop.run_in_executor(None, lambda: breaker.call(sync_wrapper))
    else:
        return await loop.run_in_executor(None, lambda: breaker.call(func, *args, **kwargs))

# Асинхронное закрытие клиентов
async def close_redis():
    global _sync_redis_client, _async_redis_client
    if _sync_redis_client:
        _sync_redis_client.close()
        logger.info("Sync Redis client closed for Circuit Breaker")
    if _async_redis_client:
        if not await is_client_closed(_async_redis_client):
            await _async_redis_client.close()
            logger.info("Async Redis client closed for caching")