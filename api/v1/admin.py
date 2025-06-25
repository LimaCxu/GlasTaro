# -*- coding: utf-8 -*-
"""
管理员相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date

from core.dependencies import (
    get_admin_service,
    get_user_service,
    get_order_service,
    get_divination_service,
    get_current_user,
    check_admin_permission,
    get_pagination_params
)
from models.user import User
from services.admin_service import AdminService
from services.user_service import UserService
from services.order_service import OrderService
from services.divination_service import DivinationService
from utils.exceptions import (
    ValidationError,
    ResourceNotFoundError,
    InsufficientPermissionError
)
from utils.helpers import format_datetime

router = APIRouter()

# 请求模型
class CreateAdminRequest(BaseModel):
    """创建管理员请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱")
    password: str = Field(..., min_length=8, description="密码")
    role: str = Field("admin", description="角色")
    permissions: List[str] = Field(default_factory=list, description="权限列表")
    is_active: bool = Field(True, description="是否激活")

class UpdateAdminRequest(BaseModel):
    """更新管理员请求"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    role: Optional[str] = Field(None, description="角色")
    permissions: Optional[List[str]] = Field(None, description="权限列表")
    is_active: Optional[bool] = Field(None, description="是否激活")

class UpdateSystemConfigRequest(BaseModel):
    """更新系统配置请求"""
    key: str = Field(..., description="配置键")
    value: Any = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="配置描述")

class UpdateFeedbackStatusRequest(BaseModel):
    """更新反馈状态请求"""
    status: str = Field(..., description="状态")
    admin_response: Optional[str] = Field(None, description="管理员回复")

# 响应模型
class AdminResponse(BaseModel):
    """管理员响应"""
    id: int
    username: str
    email: str
    role: str
    permissions: List[str]
    is_active: bool
    last_login: Optional[str]
    created_at: str
    updated_at: Optional[str]

class SystemConfigResponse(BaseModel):
    """系统配置响应"""
    id: int
    key: str
    value: Any
    description: Optional[str]
    created_at: str
    updated_at: Optional[str]

class FeedbackResponse(BaseModel):
    """反馈响应"""
    id: int
    user_id: int
    user_name: Optional[str]
    type: str
    content: str
    rating: Optional[int]
    status: str
    admin_response: Optional[str]
    created_at: str
    updated_at: Optional[str]

class AuditLogResponse(BaseModel):
    """审计日志响应"""
    id: int
    admin_id: int
    admin_username: str
    action: str
    resource_type: str
    resource_id: Optional[int]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: str

class DashboardStatsResponse(BaseModel):
    """仪表盘统计响应"""
    users: Dict[str, Any]
    orders: Dict[str, Any]
    payments: Dict[str, Any]
    divinations: Dict[str, Any]
    system: Dict[str, Any]

# 管理员管理
@router.get("/admins", response_model=List[AdminResponse], summary="获取管理员列表")
async def get_admins(
    is_active: Optional[bool] = Query(None, description="是否激活"),
    role: Optional[str] = Query(None, description="角色"),
    pagination: Dict[str, int] = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service),
    _: None = Depends(check_admin_permission)
):
    """获取管理员列表"""
    admins = await admin_service.get_admins(
        is_active=is_active,
        role=role,
        limit=pagination["size"],
        offset=pagination["offset"]
    )
    
    return [
        AdminResponse(
            id=admin.id,
            username=admin.username,
            email=admin.email,
            role=admin.role,
            permissions=admin.permissions or [],
            is_active=admin.is_active,
            last_login=format_datetime(admin.last_login) if admin.last_login else None,
            created_at=format_datetime(admin.created_at),
            updated_at=format_datetime(admin.updated_at) if admin.updated_at else None
        )
        for admin in admins
    ]

@router.post("/admins", response_model=AdminResponse, summary="创建管理员")
async def create_admin(
    request: CreateAdminRequest,
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service),
    _: None = Depends(check_admin_permission)
):
    """创建新管理员"""
    try:
        admin = await admin_service.create_admin(
            username=request.username,
            email=request.email,
            password=request.password,
            role=request.role,
            permissions=request.permissions,
            is_active=request.is_active
        )
        
        # 记录审计日志
        await admin_service.create_audit_log(
            admin_id=current_user.id,
            action="create_admin",
            resource_type="admin",
            resource_id=admin.id,
            details={"username": admin.username, "role": admin.role}
        )
        
        return AdminResponse(
            id=admin.id,
            username=admin.username,
            email=admin.email,
            role=admin.role,
            permissions=admin.permissions or [],
            is_active=admin.is_active,
            last_login=None,
            created_at=format_datetime(admin.created_at),
            updated_at=None
        )
    
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/admins/{admin_id}", response_model=AdminResponse, summary="获取管理员详情")
async def get_admin(
    admin_id: int,
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service),
    _: None = Depends(check_admin_permission)
):
    """获取指定管理员详情"""
    admin = await admin_service.get_admin_by_id(admin_id)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )
    
    return AdminResponse(
        id=admin.id,
        username=admin.username,
        email=admin.email,
        role=admin.role,
        permissions=admin.permissions or [],
        is_active=admin.is_active,
        last_login=format_datetime(admin.last_login) if admin.last_login else None,
        created_at=format_datetime(admin.created_at),
        updated_at=format_datetime(admin.updated_at) if admin.updated_at else None
    )

@router.put("/admins/{admin_id}", response_model=AdminResponse, summary="更新管理员")
async def update_admin(
    admin_id: int,
    request: UpdateAdminRequest,
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service),
    _: None = Depends(check_admin_permission)
):
    """更新管理员信息"""
    try:
        # 过滤非空字段
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有提供要更新的字段"
            )
        
        admin = await admin_service.update_admin(
            admin_id=admin_id,
            **update_data
        )
        
        # 记录审计日志
        await admin_service.create_audit_log(
            admin_id=current_user.id,
            action="update_admin",
            resource_type="admin",
            resource_id=admin_id,
            details=update_data
        )
        
        return AdminResponse(
            id=admin.id,
            username=admin.username,
            email=admin.email,
            role=admin.role,
            permissions=admin.permissions or [],
            is_active=admin.is_active,
            last_login=format_datetime(admin.last_login) if admin.last_login else None,
            created_at=format_datetime(admin.created_at),
            updated_at=format_datetime(admin.updated_at) if admin.updated_at else None
        )
    
    except (ValidationError, ResourceNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# 系统配置管理
@router.get("/config", response_model=List[SystemConfigResponse], summary="获取系统配置")
async def get_system_config(
    key: Optional[str] = Query(None, description="配置键"),
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service),
    _: None = Depends(check_admin_permission)
):
    """获取系统配置"""
    if key:
        config = await admin_service.get_system_config(key)
        return [SystemConfigResponse(
            id=config.id,
            key=config.key,
            value=config.value,
            description=config.description,
            created_at=format_datetime(config.created_at),
            updated_at=format_datetime(config.updated_at) if config.updated_at else None
        )] if config else []
    else:
        configs = await admin_service.get_all_system_configs()
        return [
            SystemConfigResponse(
                id=config.id,
                key=config.key,
                value=config.value,
                description=config.description,
                created_at=format_datetime(config.created_at),
                updated_at=format_datetime(config.updated_at) if config.updated_at else None
            )
            for config in configs
        ]

@router.put("/config", response_model=SystemConfigResponse, summary="更新系统配置")
async def update_system_config(
    request: UpdateSystemConfigRequest,
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service),
    _: None = Depends(check_admin_permission)
):
    """更新系统配置"""
    try:
        config = await admin_service.set_system_config(
            key=request.key,
            value=request.value,
            description=request.description
        )
        
        # 记录审计日志
        await admin_service.create_audit_log(
            admin_id=current_user.id,
            action="update_config",
            resource_type="system_config",
            details={"key": request.key, "value": request.value}
        )
        
        return SystemConfigResponse(
            id=config.id,
            key=config.key,
            value=config.value,
            description=config.description,
            created_at=format_datetime(config.created_at),
            updated_at=format_datetime(config.updated_at) if config.updated_at else None
        )
    
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# 用户反馈管理
@router.get("/feedback", response_model=List[FeedbackResponse], summary="获取用户反馈")
async def get_user_feedback(
    feedback_type: Optional[str] = Query(None, description="反馈类型"),
    status_filter: Optional[str] = Query(None, description="状态过滤"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    pagination: Dict[str, int] = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service),
    _: None = Depends(check_admin_permission)
):
    """获取用户反馈列表"""
    feedbacks = await admin_service.get_user_feedback(
        feedback_type=feedback_type,
        status=status_filter,
        user_id=user_id,
        limit=pagination["size"],
        offset=pagination["offset"]
    )
    
    return [
        FeedbackResponse(
            id=feedback.id,
            user_id=feedback.user_id,
            user_name=f"{feedback.user.first_name} {feedback.user.last_name}".strip() if feedback.user else None,
            type=feedback.type,
            content=feedback.content,
            rating=feedback.rating,
            status=feedback.status,
            admin_response=feedback.admin_response,
            created_at=format_datetime(feedback.created_at),
            updated_at=format_datetime(feedback.updated_at) if feedback.updated_at else None
        )
        for feedback in feedbacks
    ]

@router.put("/feedback/{feedback_id}", response_model=FeedbackResponse, summary="更新反馈状态")
async def update_feedback_status(
    feedback_id: int,
    request: UpdateFeedbackStatusRequest,
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service),
    _: None = Depends(check_admin_permission)
):
    """更新用户反馈状态"""
    try:
        feedback = await admin_service.update_feedback_status(
            feedback_id=feedback_id,
            status=request.status,
            admin_response=request.admin_response
        )
        
        # 记录审计日志
        await admin_service.create_audit_log(
            admin_id=current_user.id,
            action="update_feedback",
            resource_type="user_feedback",
            resource_id=feedback_id,
            details={"status": request.status, "has_response": bool(request.admin_response)}
        )
        
        return FeedbackResponse(
            id=feedback.id,
            user_id=feedback.user_id,
            user_name=f"{feedback.user.first_name} {feedback.user.last_name}".strip() if feedback.user else None,
            type=feedback.type,
            content=feedback.content,
            rating=feedback.rating,
            status=feedback.status,
            admin_response=feedback.admin_response,
            created_at=format_datetime(feedback.created_at),
            updated_at=format_datetime(feedback.updated_at) if feedback.updated_at else None
        )
    
    except (ValidationError, ResourceNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# 审计日志
@router.get("/audit-logs", response_model=List[AuditLogResponse], summary="获取审计日志")
async def get_audit_logs(
    admin_id: Optional[int] = Query(None, description="管理员ID"),
    action: Optional[str] = Query(None, description="操作类型"),
    resource_type: Optional[str] = Query(None, description="资源类型"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    pagination: Dict[str, int] = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service),
    _: None = Depends(check_admin_permission)
):
    """获取审计日志"""
    try:
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        logs = await admin_service.get_audit_logs(
            admin_id=admin_id,
            action=action,
            resource_type=resource_type,
            start_date=start_dt,
            end_date=end_dt,
            limit=pagination["size"],
            offset=pagination["offset"]
        )
        
        return [
            AuditLogResponse(
                id=log.id,
                admin_id=log.admin_id,
                admin_username=log.admin.username,
                action=log.action,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                details=log.details,
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                created_at=format_datetime(log.created_at)
            )
            for log in logs
        ]
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"日期格式错误: {str(e)}"
        )

# 仪表盘统计
@router.get("/dashboard", response_model=DashboardStatsResponse, summary="获取仪表盘统计")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service),
    _: None = Depends(check_admin_permission)
):
    """获取仪表盘统计数据"""
    stats = await admin_service.get_dashboard_stats()
    
    return DashboardStatsResponse(**stats)

# 数据导出
@router.get("/export/users", summary="导出用户数据")
async def export_users(
    format_type: str = Query("csv", description="导出格式 (csv, excel)"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service),
    _: None = Depends(check_admin_permission)
):
    """导出用户数据"""
    try:
        from datetime import datetime
        
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        export_data = await admin_service.export_user_data(
            format_type=format_type,
            start_date=start_dt,
            end_date=end_dt
        )
        
        # 记录审计日志
        await admin_service.create_audit_log(
            admin_id=current_user.id,
            action="export_users",
            resource_type="user",
            details={"format": format_type, "date_range": f"{start_date} to {end_date}"}
        )
        
        return {
            "message": "用户数据导出成功",
            "download_url": export_data["download_url"],
            "file_size": export_data["file_size"],
            "record_count": export_data["record_count"]
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"日期格式错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )

@router.get("/export/orders", summary="导出订单数据")
async def export_orders(
    format_type: str = Query("csv", description="导出格式 (csv, excel)"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service),
    _: None = Depends(check_admin_permission)
):
    """导出订单数据"""
    try:
        from datetime import datetime
        
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        export_data = await admin_service.export_order_data(
            format_type=format_type,
            start_date=start_dt,
            end_date=end_dt
        )
        
        # 记录审计日志
        await admin_service.create_audit_log(
            admin_id=current_user.id,
            action="export_orders",
            resource_type="order",
            details={"format": format_type, "date_range": f"{start_date} to {end_date}"}
        )
        
        return {
            "message": "订单数据导出成功",
            "download_url": export_data["download_url"],
            "file_size": export_data["file_size"],
            "record_count": export_data["record_count"]
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"日期格式错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )

# 系统维护
@router.post("/maintenance/enable", summary="启用维护模式")
async def enable_maintenance_mode(
    message: Optional[str] = Query(None, description="维护消息"),
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service),
    _: None = Depends(check_admin_permission)
):
    """启用系统维护模式"""
    await admin_service.set_system_config(
        key="maintenance_mode",
        value=True,
        description="系统维护模式"
    )
    
    if message:
        await admin_service.set_system_config(
            key="maintenance_message",
            value=message,
            description="维护模式消息"
        )
    
    # 记录审计日志
    await admin_service.create_audit_log(
        admin_id=current_user.id,
        action="enable_maintenance",
        resource_type="system",
        details={"message": message}
    )
    
    return {"message": "维护模式已启用"}

@router.post("/maintenance/disable", summary="禁用维护模式")
async def disable_maintenance_mode(
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service),
    _: None = Depends(check_admin_permission)
):
    """禁用系统维护模式"""
    await admin_service.set_system_config(
        key="maintenance_mode",
        value=False,
        description="系统维护模式"
    )
    
    # 记录审计日志
    await admin_service.create_audit_log(
        admin_id=current_user.id,
        action="disable_maintenance",
        resource_type="system"
    )
    
    return {"message": "维护模式已禁用"}

# 系统统计更新
@router.post("/stats/update", summary="更新系统统计")
async def update_system_stats(
    current_user: User = Depends(get_current_user),
    admin_service: AdminService = Depends(get_admin_service),
    _: None = Depends(check_admin_permission)
):
    """手动更新系统统计数据"""
    try:
        await admin_service.update_system_stats()
        
        # 记录审计日志
        await admin_service.create_audit_log(
            admin_id=current_user.id,
            action="update_stats",
            resource_type="system"
        )
        
        return {"message": "系统统计已更新"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新统计失败: {str(e)}"
        )