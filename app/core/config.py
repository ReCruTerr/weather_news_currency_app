# app/core/config.py
import os
from typing import Dict

class Settings:
    EXTERNAL_APIS: Dict[str, str] = {
        "weather": "https://api.open-meteo.com/v1",
        "news": "https://newsapi.org/v2",
        "geocoding": "https://nominatim.openstreetmap.org/search",
        "currency": "https://v6.exchangerate-api.com/v6/0b8505ac70122d0a76f5831c/latest/USD",
        "traffic": "https://api.traffic.example.com/v1",
    }
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "6760710056e45cadca80c5c234e33efd")
    CURRENCY_API_KEY: str = os.getenv("CURRENCY_API_KEY", "0b8505ac70122d0a76f5831c")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", 300))
    RATE_LIMIT: int = int(os.getenv("RATE_LIMIT", 100))  # Максимальное количество запросов в минуту
    RATE_LIMIT_TTL: int = int(os.getenv("RATE_LIMIT_TTL", 60))  # Время жизни лимита в секундах

settings = Settings()