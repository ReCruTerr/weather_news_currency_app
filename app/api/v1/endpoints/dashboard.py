from fastapi import APIRouter, Request
from app.core.clients.weather import get_weather
from app.core.clients.news import get_news
from app.core.clients.geocoding import get_coordinates
from app.core.clients.currency import get_currency_rates
from app.models.schemas import DashboardResponse, WeatherResponse, NewsResponse, CurrencyResponse, BaseResponse
from typing import Dict, Any, Optional
from fastapi import Depends
from slowapi import Limiter
from app.core.metrics import REQUEST_COUNTER, REQUEST_LATENCY
import time

router = APIRouter()

# Получаем limiter из контекста запроса
def get_limiter(request: Request) -> Limiter:
    return request.app.state.limiter

@router.get("/city/{city}/dashboard", response_model=DashboardResponse, summary="Получить сводку по городу", description="Агрегирует данные о погоде, новостях, валютах и геокодировании для указанного города.", dependencies=[Depends(get_limiter)])
async def get_city_dashboard(city: str):
    start_time = time.time()
    REQUEST_COUNTER.inc()
    
    try:
        geo_data = await get_coordinates(city)
        print(f"Geo data for {city}: {geo_data}")
    except Exception as e:
        print(f"Error getting coordinates for {city}: {e}")
        latitude = 55.7558  # Москва как fallback
        longitude = 37.6173
    else:
        if "error" in geo_data or "latitude" not in geo_data or "longitude" not in geo_data:
            print(f"Using fallback coordinates for {city}")
            latitude = 55.7558
            longitude = 37.6173
        else:
            latitude = geo_data["latitude"]
            longitude = geo_data["longitude"]
    
    try:
        weather_data: BaseResponse = await get_weather(city, latitude, longitude)
        print(f"Type of weather_data: {type(weather_data)}, Value: {weather_data}")
    except Exception as e:
        print(f"Error getting weather for {city}: {e}")
        weather_data = BaseResponse(status="down", data=None, error=str(e))
        
    weather_data: BaseResponse = await get_weather(city, latitude, longitude)
    print(f"Type of weather_data: {type(weather_data)}, Value: {weather_data}")

    news_data: BaseResponse = await get_news(city)
    print(f"Type of news_data: {type(news_data)}, Value: {news_data}")  # Отладка

    currency_data: BaseResponse = await get_currency_rates()
    
    response_data: Dict[str, Any] = {"city": city}
    
    # Обработка погоды
    if isinstance(weather_data, dict) and weather_data.get("error"):
        response_data["error"] = weather_data["error"]
    elif hasattr(weather_data, "error") and weather_data.error:
        response_data["error"] = weather_data.error
    else:
        if (hasattr(weather_data, "status") and weather_data.status == "up" and hasattr(weather_data, "data") and weather_data.data):
            response_data["weather"] = weather_data.data
        else:
            response_data["weather"] = None
    
    # Обработка новостей
    if isinstance(news_data, dict) and news_data.get("error") and "error" not in response_data:
        response_data["error"] = news_data["error"]
    elif hasattr(news_data, "error") and news_data.error and "error" not in response_data:
        response_data["error"] = news_data.error
    else:
        if hasattr(news_data, "status") and news_data.status == "up" and hasattr(news_data, "data") and news_data.data is not None:
            response_data["news"] = news_data.data  # Извлекаем NewsResponse
            print(f"Extracted news data: {news_data.data}")
        else:
            response_data["news"] = None
            print(f"News data not extracted, status: {getattr(news_data, 'status', 'N/A')}, data: {getattr(news_data, 'data', 'N/A')}")
    
    # Обработка валют
    if isinstance(currency_data, dict) and currency_data.get("error") and "error" not in response_data:
        response_data["error"] = currency_data["error"]
    elif hasattr(currency_data, "error") and currency_data.error and "error" not in response_data:
        response_data["error"] = currency_data.error
    else:
        if (hasattr(currency_data, "status") and currency_data.status == "up" and hasattr(currency_data, "data") and currency_data.data):
            response_data["currency"] = currency_data.data
        else:
            response_data["currency"] = None  # Устанавливаем None, если данных нет
    
    latency = time.time() - start_time
    REQUEST_LATENCY.observe(latency)  # Записываем задержку
    
    return DashboardResponse(**response_data)