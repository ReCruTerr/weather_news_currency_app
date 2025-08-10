import aiohttp
from app.core.config import settings
from app.core.clients import cache_result  # Предполагаем, что эта функция уже определена
from app.core.circuit_breaker import with_circuit_breaker  # Новый импорт

async def get_coordinates(city: str) -> dict:
    async def _get_coordinates():
        async with aiohttp.ClientSession() as session:
            url = f"{settings.EXTERNAL_APIS['geocoding']}?q={city}&format=json&addressdetails=1&limit=1"
            headers = {"User-Agent": "api-gateway/1.0 renatren25@gmail.com"}
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        return {"city": city, "error": f"Geocoding API error: {response.status}"}
                    data = await response.json()
                    print(f"Nominatim response for {city}: {data}")
                    if data:
                        location = data[0]
                        return {
                            "city": city,
                            "latitude": float(location["lat"]),
                            "longitude": float(location["lon"])
                        }
                    return {"city": city, "error": "City not found"}
            except aiohttp.ClientConnectionError:
                return {"city": city, "error": "Connection error"}
            except (aiohttp.ClientResponseError, ValueError, KeyError) as e:
                return {"city": city, "error": f"Geocoding error: {str(e)}"}

    return await cache_result(
        lambda: with_circuit_breaker("geocoding", _get_coordinates),
        f"geocoding:{city}"
    )