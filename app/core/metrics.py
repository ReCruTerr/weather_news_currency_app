from prometheus_client import Gauge, Counter, Histogram

#Инициализация метрик
REQUEST_COUNTER = Counter("api_requests_total", "Total number of API requests")
REQUEST_LATENCY = Histogram("api_request_latency_seconds", "Latency of API requests")
API_STATUS = Gauge("api_status", "Status of API services", ["api_name"])