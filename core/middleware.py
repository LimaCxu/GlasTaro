"""
FastAPI中间件
一些实用中间件，处理日志、安全、限流等

作者: Lima
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from prometheus_client import Counter, Histogram, Gauge

from core.config import settings
from core.dependencies import get_cache_service

# 日志配置
logger = logging.getLogger(__name__)

# 监控指标 - 简单实用的几个指标
REQUEST_COUNT = Counter(
    'http_requests_total', 'HTTP请求总数', 
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds', 'HTTP请求耗时',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'http_active_connections', '当前活跃连接数'
)

RATE_LIMIT_HITS = Counter(
    'rate_limit_hits_total', '限流触发次数',
    ['endpoint', 'user_type']
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    记录所有HTTP请求的基本信息和处理时间
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 获取客户端信息
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")[:100]  # 截断长UA
        
        logger.info(f"🌐 {request.method} {request.url.path} - {client_ip}")
        
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应
            logger.info(
                f"✅ {request.method} {request.url.path} - "
                f"状态:{response.status_code} 耗时:{process_time:.3f}s"
            )
            
            # 在响应头中添加处理时间
            response.headers["X-Process-Time"] = str(round(process_time, 3))
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"💥 {request.method} {request.url.path} - "
                f"错误:{str(e)} 耗时:{process_time:.3f}s",
                exc_info=True
            )
            raise


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    安全中间件
    添加安全响应头，检查维护模式
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 维护模式检查
        if settings.MAINTENANCE_MODE:
            return JSONResponse(
                status_code=503,
                content={
                    "error": {
                        "code": "MAINTENANCE_MODE", 
                        "message": settings.MAINTENANCE_MESSAGE
                    },
                    "success": False
                }
            )
        
        response = await call_next(request)
        
        # 添加基本安全头
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        # 生产环境添加更多安全头
        if not settings.DEBUG:
            security_headers.update({
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "Server": "GlasTaro/1.0"
            })
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    简单的限流中间件
    防止单个IP过于频繁的请求
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.cache_service = None
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 跳过不需要限流的端点
        skip_paths = ["/health", "/metrics", "/"]
        if request.url.path in skip_paths or not settings.ENABLE_RATE_LIMIT:
            return await call_next(request)
        
        try:
            # 懒加载缓存服务
            if not self.cache_service:
                self.cache_service = await get_cache_service()
            
            client_ip = request.client.host if request.client else "unknown"
            rate_key = f"rate_limit:{client_ip}"
            
            # 检查当前请求数
            current_count = await self.cache_service.get(rate_key) or 0
            
            if int(current_count) >= settings.RATE_LIMIT_REQUESTS:
                # 记录限流事件
                RATE_LIMIT_HITS.labels(
                    endpoint=request.url.path,
                    user_type="anonymous"
                ).inc()
                
                logger.warning(f"🚫 限流触发 - IP:{client_ip} 路径:{request.url.path}")
                
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "TOO_MANY_REQUESTS",
                            "message": "请求太频繁了，休息一下吧 😅"
                        },
                        "success": False
                    },
                    headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW)}
                )
            
            # 增加计数
            await self.cache_service.set(
                rate_key,
                int(current_count) + 1,
                expire=settings.RATE_LIMIT_WINDOW
            )
            
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"限流中间件出错: {e}")
            # 出错时放行，避免影响正常请求
            return await call_next(request)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    指标收集中间件
    收集HTTP请求的监控数据
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 如果没启用监控，直接跳过
        if not settings.ENABLE_METRICS:
            return await call_next(request)
        
        # 记录活跃连接
        ACTIVE_CONNECTIONS.inc()
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # 记录成功请求
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
            
        except Exception:
            # 记录失败请求
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=500
            ).inc()
            raise
            
        finally:
            # 减少活跃连接计数
            ACTIVE_CONNECTIONS.dec()