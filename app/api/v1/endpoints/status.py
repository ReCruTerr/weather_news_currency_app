# app/api/v1/endpoints/status.py
from fastapi import APIRouter, Request, HTTPException
from app.core.clients.weather import get_weather
from app.core.clients.news import get_news
from app.core.clients.currency import get_currency_rates
from app.core.clients.geocoding import get_coordinates
from app.core.config import settings
from app.models.schemas import BaseResponse, ServiceStatus, StatusResponse
from fastapi import Depends
from slowapi import Limiter
from prometheus_client import Gauge
import asyncio

router = APIRouter()

# Получаем limiter из контекста запроса
def get_limiter(request: Request) -> Limiter:
    return request.app.state.limiter

# Получаем API_STATUS из контекста запроса
def get_api_status(request: Request) -> Gauge:
    return request.app.state.API_STATUS

@router.get("/status", response_model=StatusResponse, summary="Проверка состояния сервисов", description="Возвращает статус всех внешних API (weather, news, currency, geocoding) и внутреннего сервиса.", dependencies=[Depends(get_limiter)])
async def get_status(request: Request, city: str = "Moscow", api_status: Gauge = Depends(get_api_status)):
    # Получаем координаты для города
    geo_data = await get_coordinates(city)
    if "error" in geo_data or "latitude" not in geo_data or "longitude" not in geo_data:
        latitude, longitude = 55.7558, 37.6173  # Fallback для Москвы
    else:
        latitude = geo_data["latitude"]
        longitude = geo_data["longitude"]

    tasks = {
        "weather": get_weather(city, latitude, longitude),
        "news": get_news(city),
        "currency": get_currency_rates(),
        "geocoding": get_coordinates(city)
    }
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    
    # Определяем статусы
    status = {
        "weather": ServiceStatus(status="down" if isinstance(results[0], Exception) or (isinstance(results[0], BaseResponse) and results[0].status == "down") else "up"),
        "news": ServiceStatus(status="down" if isinstance(results[1], Exception) or (isinstance(results[1], BaseResponse) and results[1].status == "down") else "up"),
        "geocoding": ServiceStatus(status="down" if isinstance(results[2], Exception) or (isinstance(results[2], BaseResponse) and results[2].status == "down") else "up"),
        "currency": ServiceStatus(status="down" if isinstance(results[3], Exception) or (isinstance(results[3], BaseResponse) and results[3].status == "down") else "up"),
        "gateway": ServiceStatus(status="up")  # Статус шлюза
    }
    
    # Обновляем метрики состояния API только для известных меток
    service_names = ["weather", "news", "geocoding", "currency", "gateway"]
    for name in service_names:
        api_status.labels(api_name=name).set(1 if status[name].status == "up" else 0)
    
    return StatusResponse(**status)