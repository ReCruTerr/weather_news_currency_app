# app/core/clients/currency.py
from app.core.clients import cache_result
from app.core.config import settings
import aiohttp
from app.models.schemas import BaseResponse, CurrencyResponse
from app.core.circuit_breaker import with_circuit_breaker

async def get_currency_rates(base_currency: str = "USD") -> BaseResponse:
    async def _get_currency_rates():
        async with aiohttp.ClientSession() as session:
            url = settings.EXTERNAL_APIS['currency'].replace("YOUR_API_KEY", settings.CURRENCY_API_KEY).replace("USD", base_currency)
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        return BaseResponse(status="down", message=f"API error: {response.status}", error=f"API error: {response.status}")
                    data = await response.json()
                    if data.get("result") != "success":
                        return BaseResponse(status="down", message=data.get("error-type", "Unknown error"), error=data.get("error-type", "Unknown error"))
                    rates = data.get("conversion_rates", {})
                    currency_data = CurrencyResponse(
                        usd_to_rub=rates.get("RUB", 0.0),
                        eur_to_rub=rates.get("EUR", 0.0) if rates.get("EUR") else None,
                        updated_at=data.get("time_last_update_utc")
                    )
                    return BaseResponse(status="up", data=currency_data)
            except aiohttp.ClientConnectionError:
                return BaseResponse(status="down", message="Connection error", error="Connection error")
            except aiohttp.ClientResponseError as exc:
                return BaseResponse(status="down", message=f"API error: {exc.status}", error=f"API error: {exc.status}")
            except Exception as e:
                return BaseResponse(status="down", message=f"Unexpected error: {str(e)}", error=f"Unexpected error: {str(e)}")

    return await cache_result(
        lambda: with_circuit_breaker("currency", _get_currency_rates),
        f"currency:{base_currency}"
    )