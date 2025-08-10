# app/core/clients/weather.py
from app.core.clients import cache_result
from app.core.config import settings
from app.core.circuit_breaker import with_circuit_breaker
import aiohttp
import asyncio
from typing import Optional
from app.models.schemas import BaseResponse, WeatherResponse

async def get_weather(city: str, latitude: Optional[float] = None, longitude: Optional[float] = None) -> BaseResponse:
    async def _get_weather():
        if latitude is None or longitude is None:
            return BaseResponse(status="down", message="Latitude and longitude must be provided", error="Missing coordinates")
        
        async with aiohttp.ClientSession() as session:
            url = f"{settings.EXTERNAL_APIS['weather']}/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,weathercode&forecast_days=1"
            try:
                async with session.get(url) as response:
                    await asyncio.sleep(1)  # Задержка
                    print(f"Weather API response status: {response.status}")
                    if response.status != 200:
                        return BaseResponse(status="down", message=f"API error: {response.status}", error=f"API error: {response.status}")
                    data = await response.json()
                    hourly = data.get("hourly", {})
                    temperature = hourly.get("temperature_2m", [None])[0]
                    weathercode = hourly.get("weathercode", [None])[0]
                    
                    conditions = {
                        0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                        45: "Fog", 48: "Depositing rime fog", 51: "Drizzle", 53: "Moderate drizzle",
                        55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers"
                    }.get(weathercode, "Unknown")

                    weather_data = WeatherResponse(
                        temperature=float(temperature) if temperature is not None else None,
                        condition=conditions,
                        city=city
                    )
                    return BaseResponse(status="up", data=weather_data)

            except aiohttp.ClientConnectionError:
                return BaseResponse(status="down", message="Connection error", error="Connection error")
            except aiohttp.ClientResponseError as exc:
                return BaseResponse(status="down", message=f"API error: {exc.status}", error=f"API error: {exc.status}")
            except Exception as e:
                return BaseResponse(status="down", message=f"Unexpected error: {str(e)}", error=f"Unexpected error: {str(e)}")

    return await cache_result(
        lambda: with_circuit_breaker("weather", _get_weather),
        f"weather:{city}:{latitude}:{longitude}" if latitude and longitude else f"weather:{city}"
    )
