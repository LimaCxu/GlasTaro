"""FastAPI中间件模块"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import asyncio
from prometheus_client import Counter, Histogram, Gauge

from core.config import settings
from utils.exceptions import RateLimitExceeded, MaintenanceMode
from core.dependencies import get_cache_service

# 配置日志
logger = logging.getLogger(__name__)

# Prometheus指标
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'http_active_connections',
    'Number of active HTTP connections'
)

RATE_LIMIT_HITS = Counter(
    'rate_limit_hits_total',
    'Total rate limit hits',
    ['endpoint', 'user_type']
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 记录请求信息
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        logger.info(
            f"请求开始 - {request.method} {request.url.path} "
            f"来自 {client_ip} UA: {user_agent[:100]}"
        )
        
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(
                f"请求完成 - {request.method} {request.url.path} "
                f"状态码: {response.status_code} 耗时: {process_time:.3f}s"
            )
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"请求异常 - {request.method} {request.url.path} "
                f"错误: {str(e)} 耗时: {process_time:.3f}s",
                exc_info=True
            )
            raise


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查维护模式
        if settings.MAINTENANCE_MODE:
            # 允许管理员访问
            auth_header = request.headers.get("authorization")
            if not auth_header or not self._is_admin_token(auth_header):
                return JSONResponse(
                    status_code=503,
                    content={
                        "error": {
                            "code": "MAINTENANCE_MODE",
                            "message": "系统正在维护中，请稍后再试"
                        },
                        "success": False
                    }
                )
        
        response = await call_next(request)
        
        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        if not settings.DEBUG:
            response.headers["Server"] = "TarotBot/1.0"
        
        return response
    
    def _is_admin_token(self, auth_header: str) -> bool:
        """检查是否为管理员令牌"""
        # 这里应该实现实际的管理员令牌验证逻辑
        # 暂时返回False，需要与认证系统集成
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.cache_service = None
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 跳过健康检查和指标端点
        if request.url.path in ["/health", "/metrics", "/"]:
            return await call_next(request)
        
        # 如果未启用速率限制，直接通过
        if not settings.ENABLE_RATE_LIMIT:
            return await call_next(request)
        
        try:
            # 获取缓存服务
            if not self.cache_service:
                self.cache_service = await get_cache_service()
            
            # 获取客户端IP
            client_ip = request.client.host if request.client else "unknown"
            
            # 构建速率限制键
            rate_limit_key = f"rate_limit:{client_ip}:{request.url.path}"
            
            # 检查速率限制
            current_requests = await self.cache_service.get(rate_limit_key) or 0
            
            if int(current_requests) >= settings.RATE_LIMIT_REQUESTS:
                # 记录速率限制命中
                RATE_LIMIT_HITS.labels(
                    endpoint=request.url.path,
                    user_type="anonymous"
                ).inc()
                
                logger.warning(f"速率限制触发 - IP: {client_ip} 路径: {request.url.path}")
                
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "请求过于频繁，请稍后再试"
                        },
                        "success": False
                    },
                    headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW)}
                )
            
            # 增加请求计数
            await self.cache_service.set(
                rate_limit_key,
                int(current_requests) + 1,
                expire=settings.RATE_LIMIT_WINDOW
            )
            
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"速率限制中间件错误: {e}")
            # 如果速率限制检查失败，允许请求通过
            return await call_next(request)


class MetricsMiddleware(BaseHTTPMiddleware):
    """指标收集中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.ENABLE_METRICS:
            return await call_next(request)
        
        # 增加活跃连接数
        ACTIVE_CONNECTIONS.inc()
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # 记录请求指标
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(time.time() - start_time)
            
            return response
            
        except Exception as e:
            # 记录异常请求
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=500
            ).inc()
            
            raise
            
        finally:
            # 减少活跃连接数
            ACTIVE_CONNECTIONS.dec()


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """请求大小限制中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查请求体大小
        content_length = request.headers.get("content-length")
        
        if content_length:
            content_length = int(content_length)
            max_size = settings.MAX_REQUEST_SIZE
            
            if content_length > max_size:
                logger.warning(
                    f"请求体过大 - 大小: {content_length} 最大: {max_size} "
                    f"来自: {request.client.host if request.client else 'unknown'}"
                )
                
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": {
                            "code": "REQUEST_TOO_LARGE",
                            "message": f"请求体过大，最大允许 {max_size} 字节"
                        },
                        "success": False
                    }
                )
        
        return await call_next(request)


class GeoLocationMiddleware(BaseHTTPMiddleware):
    """地理位置限制中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 如果未启用地理位置限制，直接通过
        if not settings.ENABLE_GEO_RESTRICTION:
            return await call_next(request)
        
        client_ip = request.client.host if request.client else "unknown"
        
        # 这里应该实现实际的地理位置检查逻辑
        # 例如使用GeoIP数据库或第三方服务
        # 暂时跳过实现
        
        return await call_next(request)