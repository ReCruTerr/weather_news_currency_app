# app/core/clients/__init__.py
import json
from typing import Callable, Any
import redis.asyncio as redis
from app.core.config import settings
from fastapi.encoders import jsonable_encoder
from app.models.schemas import BaseResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_redis_client():
    return await redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
        encoding="utf-8",
        decode_responses=True
    )

async def cache_result(func: Callable, key: str, ttl: int = settings.CACHE_TTL) -> Any:
    redis = await get_redis_client()
    cached = await redis.get(key)
    if cached:
        logger.info(f"Cache hit for key: {key}")
        try:
            result_dict = json.loads(cached)  # Десериализация в словарь
            logger.info(f"Deserialized cached data: {result_dict}")
            # Преобразуем обратно в BaseResponse, если структура соответствует
            if all(key in result_dict for key in ["status", "data", "error"]):
                result = BaseResponse.parse_obj(result_dict)
            else:
                result = result_dict
            await redis.close()
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode cached data for key {key}: {e}")
            await redis.close()
            # Выполняем функцию и продолжаем
            result = await func()
    else:
        logger.info(f"Cache miss for key: {key}, fetching fresh data")
        result = await func()  # Ждем выполнения функции
    
    # Кэшируем только если нет ошибки и результат сериализуем
    if result and isinstance(result, dict) and "error" not in result:  # Проверяем, что result — словарь
        logger.info(f"Caching result for key: {key} with TTL: {ttl}")
        serialized_result = jsonable_encoder(result)  # Преобразуем Pydantic в сериализуемый формат
        await redis.setex(key, ttl, json.dumps(serialized_result))  # Сериализация
    await redis.close()
    return result

__all__ = ["cache_result", "get_redis_client"]