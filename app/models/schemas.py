from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class ServiceStatus(BaseModel):
    status:str 

class StatusResponse(BaseModel):
    weather:ServiceStatus
    news:ServiceStatus
    geocoding:ServiceStatus
    currency:ServiceStatus
    gateway:ServiceStatus

class BaseResponse(BaseModel):
    status:str
    message: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None

class NewsItem(BaseModel):
    title:str|None= None
    description:Optional[str]= None
    url: Optional[str] = None


class NewsResponse(BaseModel):
    news: List[NewsItem]

class WeatherResponse(BaseModel):
    city:str 
    temperature: float | None = None
    condition: str | None = None

class CurrencyResponse(BaseModel):
    usd_to_rub: Optional[float] = None
    eur_to_rub: Optional[float] = None
    updated_at: Optional[str] = None

class GeocodingResponse(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None 
    city:str

class DashboardResponse(BaseModel):
    city: str
    weather: Optional[WeatherResponse] = None
    news: Optional[NewsResponse] = None
    currency: Optional[CurrencyResponse] = None
    error: Optional[str] = None