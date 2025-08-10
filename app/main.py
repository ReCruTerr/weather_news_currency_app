from fastapi import FastAPI, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.metrics import  API_STATUS
import redis.asyncio as redis
from prometheus_client import  generate_latest
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.circuit_breaker import close_redis



# Инициализация Limiter с Redis
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT}/minute"],
    storage_uri=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    storage_options={"decode_responses": "true"}
)

app = FastAPI(
    title="Weather API",
    description="API for fetching weather data",
    version="1.0.0",
    contact={
        "name": "Support Team",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Разрешаем запросы с фронтенда
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все HTTP-методы (GET, POST, etc.)
    allow_headers=["*"],  # Разрешаем все заголовки
)

# Обработчик для RateLimitExceeded
def custom_rate_limit_handler(request: Request, exc: Exception):
    print(f"Exception attributes: {dir(exc)}")
    if isinstance(exc, RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too Many Requests", "retry_after": getattr(exc, "retry_after", 30)}
        )
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

# Сохраняем состояние приложения
app.state.limiter = limiter
app.state.API_STATUS = API_STATUS

# Динамическая загрузка роутеров для предотвращения циклических импортов
def setup_routers(app):
    from app.api.v1.endpoints import dashboard, status
    app.include_router(dashboard.router, prefix="/api/v1")  # Добавляем префикс
    app.include_router(status.router, prefix="/api/v1")

setup_routers(app)

# Endpoint для метрик Prometheus
@app.get("/metrics", summary="Prometheus Metrics", description="Возвращает метрики для Prometheus")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")

# Главная страница
@app.get("/", summary="Главная страница", description="Возвращает приветственное сообщение")
async def main_page():
    return {"message": "Welcome to the FastAPI application!"}

@app.on_event("shutdown")
async def shutdown_event():
    await close_redis()