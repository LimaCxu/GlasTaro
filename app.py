# -*- coding: utf-8 -*-
"""
FastAPI应用主入口
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from prometheus_client import make_asgi_app
import uvicorn

from config.database import init_database, close_database
from config.redis_config import create_redis_manager
from utils.exceptions import BaseAPIException, get_error_response
from api.v1 import api_router
from core.middleware import (
    LoggingMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
    MetricsMiddleware
)
from core.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Redis管理器实例
redis_manager = create_redis_manager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("正在启动应用...")
    
    try:
        # 初始化数据库
        await init_database()
        logger.info("数据库初始化完成")
        
        # 连接Redis
        await redis_manager.connect()
        logger.info("Redis连接成功")
        
        # 设置Redis实例到应用状态
        app.state.redis = redis_manager
        
        logger.info("应用启动完成")
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise
    
    yield
    
    # 关闭时执行
    logger.info("正在关闭应用...")
    
    try:
        # 关闭Redis连接
        await redis_manager.disconnect()
        logger.info("Redis连接已关闭")
        
        # 关闭数据库连接
        await close_database()
        logger.info("数据库连接已关闭")
        
        logger.info("应用关闭完成")
        
    except Exception as e:
        logger.error(f"应用关闭时出错: {e}")

# 创建FastAPI应用
app = FastAPI(
    title="塔罗占卜机器人API",
    description="基于FastAPI的塔罗占卜Telegram机器人后端服务",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 受信任主机中间件
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# 自定义中间件
app.add_middleware(SecurityMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(MetricsMiddleware)

# 异常处理器
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    """API异常处理器"""
    logger.error(f"API异常: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content=get_error_response(exc),
        headers=exc.headers
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    logger.error(f"请求验证失败: {exc.errors()} - {request.url}")
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "请求数据验证失败",
                "details": exc.errors()
            },
            "success": False
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器"""
    logger.error(f"HTTP异常: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code
            },
            "success": False
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {str(exc)} - {request.url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误" if not settings.DEBUG else str(exc)
            },
            "success": False
        }
    )

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查Redis连接
        redis_status = "ok" if await redis_manager.ping() else "error"
        
        return {
            "status": "ok",
            "services": {
                "redis": redis_status,
                "database": "ok"  # 可以添加数据库连接检查
            },
            "timestamp": int(asyncio.get_event_loop().time())
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=503, detail="服务不可用")

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "塔罗占卜机器人API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else None
    }

# 包含API路由
app.include_router(api_router, prefix="/api/v1")

# Prometheus指标端点
if settings.ENABLE_METRICS:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

# 启动函数
def start_server():
    """启动服务器"""
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
        log_level="info" if settings.DEBUG else "warning",
        access_log=settings.DEBUG
    )

if __name__ == "__main__":
    start_server()