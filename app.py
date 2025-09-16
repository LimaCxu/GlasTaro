# -*- coding: utf-8 -*-
"""
Глас Таро API服务器
塔罗占卜机器人的后端服务，处理所有的API请求和数据管理

作者: Lima
创建时间: 2025年
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

# 设置日志 - 我喜欢简单直接的日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# 全局Redis管理器 - 简单粗暴但有效
redis_manager = create_redis_manager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用启动和关闭的生命周期管理
    我习惯把所有初始化放在这里，方便调试
    """
    # 启动时的准备工作
    logger.info("🚀 塔罗API服务启动中...")
    
    try:
        # 先搞定数据库
        await init_database()
        logger.info("✅ 数据库连接OK")
        
        # 再连Redis
        await redis_manager.connect()
        logger.info("✅ Redis连接OK")
        
        # 把Redis挂到app上，方便其他地方用
        app.state.redis = redis_manager
        
        logger.info("🎉 所有服务启动完成，准备接收请求")
        
    except Exception as e:
        logger.error(f"💥 启动失败: {e}")
        raise
    
    yield  # 这里是应用运行期间
    
    # 关闭时的清理工作
    logger.info("🛑 开始关闭服务...")
    
    try:
        # 清理顺序很重要，先关Redis再关数据库
        await redis_manager.disconnect()
        logger.info("✅ Redis已断开")
        
        await close_database()
        logger.info("✅ 数据库已断开")
        
        logger.info("👋 服务已完全关闭")
        
    except Exception as e:
        logger.error(f"关闭时出了点问题: {e}")  # 关闭时出错也不是什么大事

# 创建FastAPI应用实例
app = FastAPI(
    title="Глас Таро API",  # 用俄语名字更有个性
    description="我的塔罗占卜机器人后端服务，集成了AI解读功能",
    version="1.0.0",
    # 开发时显示文档，生产环境关闭（安全考虑）
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# 配置CORS - 开发时比较宽松，生产环境要严格
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 生产环境才加主机验证
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# 添加我的自定义中间件 - 顺序很重要
app.add_middleware(SecurityMiddleware)    # 安全第一
app.add_middleware(LoggingMiddleware)     # 日志记录
app.add_middleware(RateLimitMiddleware)   # 防刷
app.add_middleware(MetricsMiddleware)     # 监控

# 异常处理器 - 我喜欢把错误处理得清楚明了
@app.exception_handler(BaseAPIException)
async def my_api_exception_handler(request: Request, exc: BaseAPIException):
    """处理我自定义的API异常"""
    logger.error(f"业务异常: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content=get_error_response(exc),
        headers=exc.headers
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """处理请求参数验证错误"""
    logger.error(f"参数验证失败: {exc.errors()} - {request.url}")
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "请求参数有问题",
                "details": exc.errors()
            },
            "success": False
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    """处理HTTP相关异常"""
    logger.error(f"HTTP错误: {exc.detail} - {request.url}")
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
async def catch_all_handler(request: Request, exc: Exception):
    """兜底的异常处理器，捕获所有未处理的异常"""
    logger.error(f"未知错误: {str(exc)} - {request.url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "UNKNOWN_ERROR",
                "message": "服务器出了点问题" if not settings.DEBUG else str(exc)
            },
            "success": False
        }
    )

# 健康检查端点 - 简单实用
@app.get("/health")
async def health_check():
    """检查服务是否正常运行"""
    try:
        # 简单检查Redis是否还活着
        redis_ok = await redis_manager.ping()
        
        return {
            "status": "healthy",
            "services": {
                "redis": "ok" if redis_ok else "down",
                "database": "ok"  # TODO: 以后可以加数据库检查
            },
            "timestamp": int(asyncio.get_event_loop().time()),
            "message": "塔罗服务运行正常 🔮"
        }
    except Exception as e:
        logger.error(f"健康检查出错: {e}")
        raise HTTPException(status_code=503, detail="服务暂时不可用")

# 首页
@app.get("/")
async def welcome():
    """API首页"""
    return {
        "name": "Глас Таро API",
        "message": "塔罗占卜机器人后端服务",
        "version": "1.0.0",
        "author": "Lima",
        "docs": "/docs" if settings.DEBUG else "文档在生产环境中不可用",
        "health": "/health"
    }

# 挂载API路由
app.include_router(api_router, prefix="/api/v1")

# 监控指标（如果启用的话）
if settings.ENABLE_METRICS:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    logger.info("📊 Prometheus指标已启用")

def run_server():
    """启动服务器的函数"""
    config = {
        "app": "app:app",
        "host": settings.HOST,
        "port": settings.PORT,
        "reload": settings.DEBUG,
        "log_level": "info" if settings.DEBUG else "warning",
        "access_log": settings.DEBUG
    }
    
    # 生产环境用多进程
    if not settings.DEBUG:
        config["workers"] = settings.WORKERS
    
    logger.info(f"🚀 启动服务器 {settings.HOST}:{settings.PORT}")
    uvicorn.run(**config)

# 直接运行时启动服务器
if __name__ == "__main__":
    run_server()