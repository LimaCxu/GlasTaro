# -*- coding: utf-8 -*-
"""
用户相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from core.dependencies import (
    get_user_service,
    get_current_user,
    get_pagination_params,
    rate_limit_check
)
from models.user import User
from services.user_service import UserService
from utils.exceptions import (
    UserNotFoundError,
    ValidationError,
    DuplicateResourceError
)
from utils.helpers import format_datetime

router = APIRouter()

# 请求模型
class UpdateProfileRequest(BaseModel):
    """更新用户资料请求"""
    username: Optional[str] = Field(None, description="用户名")
    first_name: Optional[str] = Field(None, description="名字")
    last_name: Optional[str] = Field(None, description="姓氏")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    language_code: Optional[str] = Field(None, description="语言代码")

class UpdateSettingsRequest(BaseModel):
    """更新用户设置请求"""
    language: Optional[str] = Field(None, description="语言")
    timezone: Optional[str] = Field(None, description="时区")
    notifications_enabled: Optional[bool] = Field(None, description="是否启用通知")
    email_notifications: Optional[bool] = Field(None, description="是否启用邮件通知")
    telegram_notifications: Optional[bool] = Field(None, description="是否启用Telegram通知")
    privacy_level: Optional[str] = Field(None, description="隐私级别")
    theme: Optional[str] = Field(None, description="主题")
    auto_translate: Optional[bool] = Field(None, description="是否自动翻译")
    daily_reminder: Optional[bool] = Field(None, description="是否启用每日提醒")
    reminder_time: Optional[str] = Field(None, description="提醒时间")

class CreateFeedbackRequest(BaseModel):
    """创建反馈请求"""
    feedback_type: str = Field(..., description="反馈类型")
    content: str = Field(..., min_length=1, max_length=1000, description="反馈内容")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分(1-5)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

# 响应模型
class UserProfileResponse(BaseModel):
    """用户资料响应"""
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
    profile: Optional[Dict[str, Any]]
    settings: Optional[Dict[str, Any]]

class UserStatsResponse(BaseModel):
    """用户统计响应"""
    total_divinations: int
    monthly_divinations: int
    registration_days: int
    current_tier: str
    is_premium: bool
    last_login: Optional[str]

class UserListResponse(BaseModel):
    """用户列表响应"""
    users: List[Dict[str, Any]]
    total: int
    page: int
    size: int
    pages: int

class FeedbackResponse(BaseModel):
    """反馈响应"""
    id: int
    user_id: int
    type: str
    content: str
    rating: Optional[int]
    status: str
    created_at: str
    updated_at: Optional[str]

@router.get("/profile", response_model=UserProfileResponse, summary="获取用户资料")
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """获取当前用户的详细资料"""
    # 获取完整的用户信息
    user = await user_service.get_user_by_id(current_user.id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return UserProfileResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        language_code=user.language_code,
        is_premium=user.is_premium,
        is_active=user.is_active,
        registration_date=format_datetime(user.registration_date) if user.registration_date else None,
        last_login=format_datetime(user.last_login) if user.last_login else None,
        profile=user.profile.to_dict() if user.profile else None,
        settings=user.settings.to_dict() if user.settings else None
    )

@router.put("/profile", response_model=UserProfileResponse, summary="更新用户资料")
async def update_user_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """更新用户资料"""
    try:
        # 过滤非空字段
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有提供要更新的字段"
            )
        
        # 更新用户资料
        updated_user = await user_service.update_user_profile(
            user_id=current_user.id,
            **update_data
        )
        
        return UserProfileResponse(
            id=updated_user.id,
            telegram_id=updated_user.telegram_id,
            username=updated_user.username,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            email=updated_user.email,
            phone=updated_user.phone,
            language_code=updated_user.language_code,
            is_premium=updated_user.is_premium,
            is_active=updated_user.is_active,
            registration_date=format_datetime(updated_user.registration_date) if updated_user.registration_date else None,
            last_login=format_datetime(updated_user.last_login) if updated_user.last_login else None,
            profile=updated_user.profile.to_dict() if updated_user.profile else None,
            settings=updated_user.settings.to_dict() if updated_user.settings else None
        )
    
    except (ValidationError, DuplicateResourceError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/settings", summary="更新用户设置")
async def update_user_settings(
    request: UpdateSettingsRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """更新用户设置"""
    try:
        # 过滤非空字段
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有提供要更新的字段"
            )
        
        # 更新用户设置
        settings = await user_service.update_user_settings(
            user_id=current_user.id,
            **update_data
        )
        
        return {
            "message": "设置更新成功",
            "settings": settings.to_dict()
        }
    
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/stats", response_model=UserStatsResponse, summary="获取用户统计")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """获取用户统计信息"""
    stats = await user_service.get_user_stats(current_user.id)
    
    return UserStatsResponse(**stats)

@router.post("/feedback", response_model=FeedbackResponse, summary="创建用户反馈")
async def create_feedback(
    request: CreateFeedbackRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    _: None = Depends(rate_limit_check)
):
    """创建用户反馈"""
    try:
        feedback = await user_service.create_user_feedback(
            user_id=current_user.id,
            feedback_type=request.feedback_type,
            content=request.content,
            rating=request.rating,
            metadata=request.metadata
        )
        
        return FeedbackResponse(
            id=feedback.id,
            user_id=feedback.user_id,
            type=feedback.type,
            content=feedback.content,
            rating=feedback.rating,
            status=feedback.status,
            created_at=format_datetime(feedback.created_at),
            updated_at=format_datetime(feedback.updated_at) if feedback.updated_at else None
        )
    
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/feedback", response_model=List[FeedbackResponse], summary="获取用户反馈列表")
async def get_user_feedback(
    feedback_type: Optional[str] = Query(None, description="反馈类型"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """获取用户反馈列表"""
    feedbacks = await user_service.get_user_feedback(
        user_id=current_user.id,
        feedback_type=feedback_type,
        limit=limit,
        offset=offset
    )
    
    return [
        FeedbackResponse(
            id=feedback.id,
            user_id=feedback.user_id,
            type=feedback.type,
            content=feedback.content,
            rating=feedback.rating,
            status=feedback.status,
            created_at=format_datetime(feedback.created_at),
            updated_at=format_datetime(feedback.updated_at) if feedback.updated_at else None
        )
        for feedback in feedbacks
    ]

@router.get("/export", summary="导出用户数据")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """导出用户数据"""
    try:
        user_data = await user_service.export_user_data(current_user.id)
        
        return {
            "message": "用户数据导出成功",
            "data": user_data
        }
    
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/account", summary="删除用户账户")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """删除用户账户（软删除）"""
    try:
        await user_service.delete_user(current_user.id)
        
        return {"message": "账户删除成功"}
    
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# 管理员专用接口
@router.get("/list", response_model=UserListResponse, summary="获取用户列表（管理员）")
async def get_users_list(
    search: Optional[str] = Query(None, description="搜索关键词"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    is_premium: Optional[bool] = Query(None, description="是否为高级用户"),
    order_by: str = Query("created_at", description="排序字段"),
    order_desc: bool = Query(True, description="是否降序"),
    pagination: Dict[str, int] = Depends(get_pagination_params),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """获取用户列表（管理员专用）"""
    # 检查管理员权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    users, total = await user_service.get_users(
        limit=pagination["size"],
        offset=pagination["offset"],
        search=search,
        is_active=is_active,
        is_premium=is_premium,
        order_by=order_by,
        order_desc=order_desc
    )
    
    # 计算总页数
    pages = (total + pagination["size"] - 1) // pagination["size"]
    
    return UserListResponse(
        users=[
            {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "language_code": user.language_code,
                "is_premium": user.is_premium,
                "is_active": user.is_active,
                "registration_date": format_datetime(user.registration_date) if user.registration_date else None,
                "last_login": format_datetime(user.last_login) if user.last_login else None,
                "current_tier": user.current_tier.name if user.current_tier else None
            }
            for user in users
        ],
        total=total,
        page=pagination["page"],
        size=pagination["size"],
        pages=pages
    )

@router.get("/{user_id}", response_model=UserProfileResponse, summary="获取指定用户信息（管理员）")
async def get_user_by_id(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """获取指定用户信息（管理员专用）"""
    # 检查权限：管理员或用户本人
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return UserProfileResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        language_code=user.language_code,
        is_premium=user.is_premium,
        is_active=user.is_active,
        registration_date=format_datetime(user.registration_date) if user.registration_date else None,
        last_login=format_datetime(user.last_login) if user.last_login else None,
        profile=user.profile.to_dict() if user.profile else None,
        settings=user.settings.to_dict() if user.settings else None
    )

@router.put("/{user_id}/status", summary="更新用户状态（管理员）")
async def update_user_status(
    user_id: int,
    is_active: bool,
    reason: Optional[str] = None,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """更新用户状态（管理员专用）"""
    # 检查管理员权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    try:
        if is_active:
            await user_service.activate_user(user_id)
            message = "用户已激活"
        else:
            await user_service.deactivate_user(user_id, reason)
            message = "用户已停用"
        
        return {"message": message}
    
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )