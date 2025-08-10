from app.core.clients import cache_result
from app.core.circuit_breaker import with_circuit_breaker
from app.core.config import settings
import aiohttp
from app.models.schemas import BaseResponse, NewsResponse, NewsItem

async def get_news(city: str) -> BaseResponse:
    async def _get_news():
        api_key = settings.NEWS_API_KEY
        print(f"Using GNews API key: {api_key}")
        if not api_key or not isinstance(api_key, str) or not api_key.strip():
            return BaseResponse(status="down", message="Invalid or missing API key", error="Invalid or missing API key")
        async with aiohttp.ClientSession() as session:
            url = f"https://gnews.io/api/v4/search?q={city}&apikey={api_key}"
            print(f"Requesting URL: {url}")
            try:
                async with session.get(url) as response:
                    print(f"GNews API response status: {response.status}")
                    if response.status != 200:
                        data = await response.json()
                        print(f"Raw GNews data: {data}")
                        raise Exception(f"API error: {response.status}")
                    data = await response.json()
                    print(f"Raw GNews data: {data}")
                    if data.get("status") == "error":
                        raise Exception(data.get("message", "Unknown error"))
                    articles = data.get("articles", [])
                    if not articles:
                        return BaseResponse(status="up", data=NewsResponse(news=[]))
                    news_items = [NewsItem(
                        title=article.get("title", ""),
                        description=article.get("description", ""),
                        url=article.get("url")
                    ) for article in articles]
                    news_data = NewsResponse(news=news_items)
                    return BaseResponse(status="up", data=news_data)
            except aiohttp.ClientConnectionError:
                raise Exception("Connection error")
            except aiohttp.ClientResponseError as exc:
                raise Exception(f"API error: {exc.status}")
            except Exception as e:
                raise Exception(f"Unexpected error: {str(e)}")

    return await cache_result(
        lambda: with_circuit_breaker("news", _get_news),
        f"news:{city}"
    )