# -*- coding: utf-8 -*-
"""
异常处理模块
"""

from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status

class BaseAPIException(HTTPException):
    """API基础异常类"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self.__class__.__name__

class UserNotFoundError(BaseAPIException):
    """用户未找到异常"""
    
    def __init__(self, user_id: Optional[int] = None):
        detail = f"用户 {user_id} 未找到" if user_id else "用户未找到"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="USER_NOT_FOUND"
        )

class InvalidCredentialsError(BaseAPIException):
    """无效凭据异常"""
    
    def __init__(self, detail: str = "用户名或密码错误"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="INVALID_CREDENTIALS",
            headers={"WWW-Authenticate": "Bearer"}
        )

class TokenExpiredError(BaseAPIException):
    """令牌过期异常"""
    
    def __init__(self, detail: str = "令牌已过期"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="TOKEN_EXPIRED",
            headers={"WWW-Authenticate": "Bearer"}
        )

class InsufficientPermissionsError(BaseAPIException):
    """权限不足异常"""
    
    def __init__(self, detail: str = "权限不足"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="INSUFFICIENT_PERMISSIONS"
        )

class RateLimitExceeded(BaseAPIException):
    """速率限制超出异常"""
    
    def __init__(self, detail: str = "请求过于频繁，请稍后再试", retry_after: Optional[int] = None):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED",
            headers=headers
        )

class ValidationError(BaseAPIException):
    """数据验证异常"""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        if field:
            detail = f"{field}: {detail}"
        
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )

class PaymentError(BaseAPIException):
    """支付异常"""
    
    def __init__(self, detail: str, payment_error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=detail,
            error_code=payment_error_code or "PAYMENT_ERROR"
        )

class PaymentRequiredError(PaymentError):
    """需要付费异常"""
    
    def __init__(self, detail: str = "此功能需要付费订阅"):
        super().__init__(
            detail=detail,
            payment_error_code="PAYMENT_REQUIRED"
        )

class InsufficientBalanceError(PaymentError):
    """余额不足异常"""
    
    def __init__(self, detail: str = "账户余额不足"):
        super().__init__(
            detail=detail,
            payment_error_code="INSUFFICIENT_BALANCE"
        )

class PaymentProcessingError(PaymentError):
    """支付处理异常"""
    
    def __init__(self, detail: str = "支付处理失败"):
        super().__init__(
            detail=detail,
            payment_error_code="PAYMENT_PROCESSING_ERROR"
        )

class DivinationError(BaseAPIException):
    """占卜异常"""
    
    def __init__(self, detail: str, divination_error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=divination_error_code or "DIVINATION_ERROR"
        )

class DivinationLimitExceededError(DivinationError):
    """占卜次数超限异常"""
    
    def __init__(self, detail: str = "今日占卜次数已用完"):
        super().__init__(
            detail=detail,
            divination_error_code="DIVINATION_LIMIT_EXCEEDED"
        )

class InvalidDivinationTypeError(DivinationError):
    """无效占卜类型异常"""
    
    def __init__(self, divination_type: str):
        super().__init__(
            detail=f"无效的占卜类型: {divination_type}",
            divination_error_code="INVALID_DIVINATION_TYPE"
        )

class DivinationSessionNotFoundError(DivinationError):
    """占卜会话未找到异常"""
    
    def __init__(self, session_id: str):
        super().__init__(
            detail=f"占卜会话 {session_id} 未找到",
            divination_error_code="DIVINATION_SESSION_NOT_FOUND"
        )

class DatabaseError(BaseAPIException):
    """数据库异常"""
    
    def __init__(self, detail: str = "数据库操作失败"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR"
        )

class CacheError(BaseAPIException):
    """缓存异常"""
    
    def __init__(self, detail: str = "缓存操作失败"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="CACHE_ERROR"
        )

class ExternalServiceError(BaseAPIException):
    """外部服务异常"""
    
    def __init__(self, service_name: str, detail: str = "外部服务调用失败"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service_name}: {detail}",
            error_code="EXTERNAL_SERVICE_ERROR"
        )

class AIServiceError(ExternalServiceError):
    """AI服务异常"""
    
    def __init__(self, detail: str = "AI服务调用失败"):
        super().__init__(
            service_name="AI服务",
            detail=detail
        )

class TelegramAPIError(ExternalServiceError):
    """Telegram API异常"""
    
    def __init__(self, detail: str = "Telegram API调用失败"):
        super().__init__(
            service_name="Telegram API",
            detail=detail
        )

class ConfigurationError(BaseAPIException):
    """配置异常"""
    
    def __init__(self, detail: str = "系统配置错误"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="CONFIGURATION_ERROR"
        )

class ResourceNotFoundError(BaseAPIException):
    """资源未找到异常"""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_type} {resource_id} 未找到",
            error_code="RESOURCE_NOT_FOUND"
        )

class DuplicateResourceError(BaseAPIException):
    """资源重复异常"""
    
    def __init__(self, resource_type: str, detail: str = "资源已存在"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource_type}: {detail}",
            error_code="DUPLICATE_RESOURCE"
        )

class BusinessLogicError(BaseAPIException):
    """业务逻辑异常"""
    
    def __init__(self, detail: str, business_error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=business_error_code or "BUSINESS_LOGIC_ERROR"
        )

class MaintenanceMode(BaseAPIException):
    """维护模式异常"""
    
    def __init__(self, detail: str = "系统正在维护中，请稍后再试"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="MAINTENANCE_MODE"
        )

# 异常处理器映射
EXCEPTION_HANDLERS = {
    UserNotFoundError: "用户相关异常",
    InvalidCredentialsError: "认证异常",
    RateLimitExceededError: "速率限制异常",
    PaymentError: "支付相关异常",
    DivinationError: "占卜相关异常",
    DatabaseError: "数据库异常",
    ExternalServiceError: "外部服务异常",
    ValidationError: "数据验证异常",
    ConfigurationError: "配置异常",
    BusinessLogicError: "业务逻辑异常"
}

def get_error_response(exception: BaseAPIException) -> Dict[str, Any]:
    """获取错误响应格式
    
    Args:
        exception: 异常实例
        
    Returns:
        Dict[str, Any]: 错误响应
    """
    return {
        "error": {
            "code": exception.error_code,
            "message": exception.detail,
            "status_code": exception.status_code
        },
        "success": False,
        "timestamp": int(datetime.utcnow().timestamp())
    }