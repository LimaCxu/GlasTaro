# -*- coding: utf-8 -*-
"""
依赖注入模块
"""

from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db as _get_db
from config.redis_config import RedisManager
from services.user_service import UserService
from services.cache_service import CacheService
from services.order_service import OrderService
from services.divination_service import DivinationService
from services.admin_service import AdminService
from services.payment_service import PaymentService
from utils.exceptions import RateLimitExceededError, MaintenanceModeError
from core.config import settings

# 数据库依赖
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async for session in _get_db():
        yield session

# Redis依赖
async def get_redis(request: Request) -> RedisManager:
    """获取Redis管理器"""
    return request.app.state.redis

# 缓存服务依赖
async def get_cache_service(redis: RedisManager = Depends(get_redis)) -> CacheService:
    """获取缓存服务"""
    return CacheService(redis)

# 用户服务依赖
async def get_user_service(
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
) -> UserService:
    """获取用户服务"""
    return UserService(db, redis)

# 订单服务依赖
async def get_order_service(
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
) -> OrderService:
    """获取订单服务"""
    return OrderService(db, redis)

# 占卜服务依赖
async def get_divination_service(
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
) -> DivinationService:
    """获取占卜服务"""
    return DivinationService(db, redis)

# 管理员服务依赖
async def get_admin_service(
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
) -> AdminService:
    """获取管理员服务"""
    return AdminService(db, redis)

# 支付服务依赖
async def get_payment_service(
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
) -> PaymentService:
    """获取支付服务"""
    return PaymentService(db, redis)

# 速率限制检查
async def check_rate_limit(
    request: Request,
    cache_service: CacheService = Depends(get_cache_service)
):
    """检查速率限制"""
    if not settings.RATE_LIMIT_ENABLED:
        return
    
    # 获取客户端IP
    client_ip = request.client.host
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    
    # 检查每分钟限制
    allowed, remaining = await cache_service.check_rate_limit(
        user_id=hash(client_ip),  # 使用IP哈希作为用户ID
        action="api_request",
        limit=settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
        window_seconds=60
    )
    
    if not allowed:
        raise RateLimitExceededError(
            detail=f"请求过于频繁，请在 {60} 秒后重试",
            retry_after=60
        )
    
    # 设置响应头
    request.state.rate_limit_remaining = remaining

# 维护模式检查
async def check_maintenance_mode():
    """检查维护模式"""
    if settings.MAINTENANCE_MODE:
        raise MaintenanceModeError(detail=settings.MAINTENANCE_MESSAGE)

# 用户认证依赖（可选）
async def get_optional_current_user(
    request: Request,
    user_service: UserService = Depends(get_user_service)
) -> Optional[int]:
    """获取当前用户（可选）"""
    # 从请求头或查询参数获取用户ID
    user_id = None
    
    # 从Telegram webhook获取用户ID
    if hasattr(request.state, "telegram_user_id"):
        user_id = request.state.telegram_user_id
    
    # 从Authorization头获取
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # 这里可以添加JWT令牌验证逻辑
        # user_id = verify_token(token)
    
    # 从查询参数获取（仅用于开发/测试）
    if settings.DEBUG:
        user_id_param = request.query_params.get("user_id")
        if user_id_param:
            try:
                user_id = int(user_id_param)
            except ValueError:
                pass
    
    return user_id

# 必需的用户认证依赖
async def get_current_user(
    user_id: Optional[int] = Depends(get_optional_current_user)
) -> int:
    """获取当前用户（必需）"""
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要用户认证",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user_id

# 管理员认证依赖
async def get_current_admin(
    request: Request,
    admin_service: AdminService = Depends(get_admin_service)
) -> int:
    """获取当前管理员"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要管理员认证",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = auth_header[7:]
    # 这里应该验证管理员JWT令牌
    # admin_id = verify_admin_token(token)
    # 临时返回固定值，实际应该从令牌中解析
    admin_id = 1
    
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的管理员令牌",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return admin_id

# 权限检查依赖
def require_permission(permission: str):
    """权限检查装饰器"""
    async def permission_checker(
        admin_id: int = Depends(get_current_admin),
        admin_service: AdminService = Depends(get_admin_service)
    ):
        admin = await admin_service.get_admin_by_id(admin_id)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="管理员不存在"
            )
        
        # 检查权限
        if not admin_service.check_permission(admin, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {permission}"
            )
        
        return admin_id
    
    return permission_checker

# 分页依赖
class PaginationParams:
    """分页参数"""
    
    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100
    ):
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), max_page_size)
        self.offset = (self.page - 1) * self.page_size
        self.limit = self.page_size

async def get_pagination_params(
    page: int = 1,
    page_size: int = 20
) -> PaginationParams:
    """获取分页参数"""
    return PaginationParams(page=page, page_size=page_size)

# 语言依赖
async def get_user_language(
    request: Request,
    user_id: Optional[int] = Depends(get_optional_current_user),
    user_service: Optional[UserService] = None
) -> str:
    """获取用户语言"""
    # 优先级：用户设置 > Accept-Language头 > 默认语言
    
    # 1. 从用户设置获取
    if user_id and user_service:
        try:
            preferences = await user_service.get_user_preferences(user_id)
            if preferences and preferences.language:
                return preferences.language
        except Exception:
            pass
    
    # 2. 从Accept-Language头获取
    accept_language = request.headers.get("Accept-Language")
    if accept_language:
        # 解析Accept-Language头
        languages = []
        for lang_range in accept_language.split(","):
            lang = lang_range.split(";")[0].strip().lower()
            if lang in settings.SUPPORTED_LANGUAGES:
                languages.append(lang)
        
        if languages:
            return languages[0]
    
    # 3. 返回默认语言
    return settings.DEFAULT_LANGUAGE

# 文件上传依赖
class FileUploadParams:
    """文件上传参数"""
    
    def __init__(
        self,
        max_size: int = None,
        allowed_types: list = None
    ):
        self.max_size = max_size or settings.MAX_FILE_SIZE
        self.allowed_types = allowed_types or settings.ALLOWED_FILE_TYPES

async def get_file_upload_params() -> FileUploadParams:
    """获取文件上传参数"""
    return FileUploadParams()

# 请求日志依赖
async def log_request(request: Request):
    """记录请求日志"""
    import logging
    logger = logging.getLogger("api.request")
    
    # 记录请求信息
    logger.info(
        f"{request.method} {request.url.path} - "
        f"IP: {request.client.host} - "
        f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
    )

# 响应头依赖
async def add_response_headers(request: Request):
    """添加响应头"""
    # 这个函数会在中间件中使用
    headers = {
        "X-API-Version": settings.VERSION,
        "X-Request-ID": getattr(request.state, "request_id", "unknown")
    }
    
    # 添加速率限制信息
    if hasattr(request.state, "rate_limit_remaining"):
        headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)
        headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS_PER_MINUTE)
    
    return headers