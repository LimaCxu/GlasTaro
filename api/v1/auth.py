# -*- coding: utf-8 -*-
"""
认证相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional

from core.dependencies import (
    get_user_service,
    get_current_user,
    rate_limit_check
)
from models.user import User
from services.user_service import UserService
from utils.exceptions import (
    UserNotFoundError,
    InvalidCredentialsError,
    ValidationError,
    DuplicateResourceError
)
from utils.validators import validate_email, validate_phone

router = APIRouter()
security = HTTPBearer()

# 请求模型
class LoginRequest(BaseModel):
    """登录请求"""
    identifier: str = Field(..., description="邮箱、手机号或用户名")
    password: str = Field(..., min_length=6, description="密码")
    identifier_type: str = Field("email", description="标识符类型: email, phone, username")

class RegisterRequest(BaseModel):
    """注册请求"""
    telegram_id: int = Field(..., description="Telegram用户ID")
    username: Optional[str] = Field(None, description="用户名")
    first_name: Optional[str] = Field(None, description="名字")
    last_name: Optional[str] = Field(None, description="姓氏")
    language_code: str = Field("en", description="语言代码")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    password: Optional[str] = Field(None, min_length=6, description="密码")

class TelegramAuthRequest(BaseModel):
    """Telegram认证请求"""
    telegram_id: int = Field(..., description="Telegram用户ID")
    username: Optional[str] = Field(None, description="用户名")
    first_name: Optional[str] = Field(None, description="名字")
    last_name: Optional[str] = Field(None, description="姓氏")
    language_code: str = Field("en", description="语言代码")

class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=6, description="新密码")

class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    identifier: str = Field(..., description="邮箱或手机号")
    identifier_type: str = Field("email", description="标识符类型: email, phone")

class ConfirmResetPasswordRequest(BaseModel):
    """确认重置密码请求"""
    user_id: int = Field(..., description="用户ID")
    reset_token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=6, description="新密码")

# 响应模型
class AuthResponse(BaseModel):
    """认证响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field("bearer", description="令牌类型")
    user: dict = Field(..., description="用户信息")

class UserResponse(BaseModel):
    """用户响应"""
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    language_code: str
    is_premium: bool
    is_active: bool
    registration_date: Optional[str]
    last_login: Optional[str]

@router.post("/register", response_model=AuthResponse, summary="用户注册")
async def register(
    request: RegisterRequest,
    user_service: UserService = Depends(get_user_service),
    _: None = Depends(rate_limit_check)
):
    """用户注册"""
    try:
        # 注册用户
        user = await user_service.register_user(
            telegram_id=request.telegram_id,
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name,
            language_code=request.language_code,
            email=request.email,
            phone=request.phone,
            password=request.password
        )
        
        # 生成认证令牌
        _, token = await user_service.authenticate_telegram_user(user.telegram_id)
        
        return AuthResponse(
            access_token=token,
            user={
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "language_code": user.language_code,
                "is_premium": user.is_premium,
                "is_active": user.is_active
            }
        )
    
    except DuplicateResourceError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=AuthResponse, summary="用户登录")
async def login(
    request: LoginRequest,
    user_service: UserService = Depends(get_user_service),
    _: None = Depends(rate_limit_check)
):
    """用户登录"""
    try:
        # 用户认证
        user, token = await user_service.authenticate_user(
            identifier=request.identifier,
            password=request.password,
            identifier_type=request.identifier_type
        )
        
        return AuthResponse(
            access_token=token,
            user={
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "language_code": user.language_code,
                "is_premium": user.is_premium,
                "is_active": user.is_active
            }
        )
    
    except (UserNotFoundError, InvalidCredentialsError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/telegram", response_model=AuthResponse, summary="Telegram认证")
async def telegram_auth(
    request: TelegramAuthRequest,
    user_service: UserService = Depends(get_user_service),
    _: None = Depends(rate_limit_check)
):
    """Telegram用户认证"""
    try:
        # 尝试认证现有用户
        try:
            user, token = await user_service.authenticate_telegram_user(request.telegram_id)
        except UserNotFoundError:
            # 用户不存在，自动注册
            user = await user_service.register_user(
                telegram_id=request.telegram_id,
                username=request.username,
                first_name=request.first_name,
                last_name=request.last_name,
                language_code=request.language_code
            )
            _, token = await user_service.authenticate_telegram_user(user.telegram_id)
        
        return AuthResponse(
            access_token=token,
            user={
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "language_code": user.language_code,
                "is_premium": user.is_premium,
                "is_active": user.is_active
            }
        )
    
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return UserResponse(
        id=current_user.id,
        telegram_id=current_user.telegram_id,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
        phone=current_user.phone,
        language_code=current_user.language_code,
        is_premium=current_user.is_premium,
        is_active=current_user.is_active,
        registration_date=current_user.registration_date.isoformat() if current_user.registration_date else None,
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )

@router.post("/change-password", summary="修改密码")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """修改密码"""
    try:
        await user_service.change_password(
            user_id=current_user.id,
            old_password=request.old_password,
            new_password=request.new_password
        )
        
        return {"message": "密码修改成功"}
    
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/reset-password", summary="重置密码")
async def reset_password(
    request: ResetPasswordRequest,
    user_service: UserService = Depends(get_user_service),
    _: None = Depends(rate_limit_check)
):
    """重置密码"""
    try:
        # 验证标识符格式
        if request.identifier_type == "email" and not validate_email(request.identifier):
            raise ValidationError("邮箱格式无效")
        elif request.identifier_type == "phone" and not validate_phone(request.identifier):
            raise ValidationError("手机号格式无效")
        
        reset_token = await user_service.reset_password(
            identifier=request.identifier,
            identifier_type=request.identifier_type
        )
        
        # 在实际应用中，这里应该发送邮件或短信
        # 为了演示，直接返回令牌（生产环境中不应该这样做）
        return {
            "message": "重置令牌已生成",
            "reset_token": reset_token  # 仅用于演示
        }
    
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/confirm-reset-password", summary="确认重置密码")
async def confirm_reset_password(
    request: ConfirmResetPasswordRequest,
    user_service: UserService = Depends(get_user_service),
    _: None = Depends(rate_limit_check)
):
    """确认重置密码"""
    try:
        await user_service.confirm_password_reset(
            user_id=request.user_id,
            reset_token=request.reset_token,
            new_password=request.new_password
        )
        
        return {"message": "密码重置成功"}
    
    except (UserNotFoundError, InvalidCredentialsError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/logout", summary="用户登出")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """用户登出"""
    # 在实际应用中，这里可以将令牌加入黑名单
    # 或者清除相关的会话信息
    return {"message": "登出成功"}

@router.post("/refresh", response_model=AuthResponse, summary="刷新令牌")
async def refresh_token(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """刷新访问令牌"""
    try:
        # 生成新的访问令牌
        _, token = await user_service.authenticate_telegram_user(current_user.telegram_id)
        
        return AuthResponse(
            access_token=token,
            user={
                "id": current_user.id,
                "telegram_id": current_user.telegram_id,
                "username": current_user.username,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "email": current_user.email,
                "phone": current_user.phone,
                "language_code": current_user.language_code,
                "is_premium": current_user.is_premium,
                "is_active": current_user.is_active
            }
        )
    
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )