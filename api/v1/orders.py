# -*- coding: utf-8 -*-
"""
订单相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal

from core.dependencies import (
    get_order_service,
    get_current_user,
    get_pagination_params,
    rate_limit_check
)
from models.user import User
from services.order_service import OrderService
from utils.exceptions import (
    ValidationError,
    ResourceNotFoundError,
    InsufficientPermissionError
)
from utils.helpers import format_datetime

router = APIRouter()

# 请求模型
class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    tier_id: int = Field(..., description="等级ID")
    payment_method: str = Field(..., description="支付方式")
    currency: str = Field("USD", description="货币")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class UpdateOrderRequest(BaseModel):
    """更新订单请求"""
    status: Optional[str] = Field(None, description="订单状态")
    notes: Optional[str] = Field(None, description="备注")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

# 响应模型
class UserTierResponse(BaseModel):
    """用户等级响应"""
    id: int
    name: str
    name_en: str
    description: str
    price: float
    currency: str
    duration_days: int
    features: List[str]
    daily_divination_limit: int
    priority_support: bool
    custom_spreads: bool
    detailed_interpretation: bool
    is_active: bool
    sort_order: int

class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    order_number: str
    user_id: int
    tier_id: int
    tier_name: str
    amount: float
    currency: str
    status: str
    payment_method: str
    payment_status: str
    created_at: str
    updated_at: Optional[str]
    expires_at: Optional[str]
    completed_at: Optional[str]
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]

class OrderStatsResponse(BaseModel):
    """订单统计响应"""
    total_orders: int
    completed_orders: int
    pending_orders: int
    cancelled_orders: int
    total_revenue: float
    monthly_revenue: float
    average_order_value: float
    conversion_rate: float

class PaymentRecordResponse(BaseModel):
    """支付记录响应"""
    id: int
    order_id: int
    transaction_id: str
    payment_provider: str
    amount: float
    currency: str
    status: str
    payment_method: str
    created_at: str
    updated_at: Optional[str]
    completed_at: Optional[str]
    failure_reason: Optional[str]
    metadata: Optional[Dict[str, Any]]

@router.get("/tiers", response_model=List[UserTierResponse], summary="获取用户等级列表")
async def get_user_tiers(
    is_active: bool = Query(True, description="是否只显示激活的等级"),
    order_service: OrderService = Depends(get_order_service)
):
    """获取用户等级列表"""
    tiers = await order_service.get_user_tiers(is_active=is_active)
    
    return [
        UserTierResponse(
            id=tier.id,
            name=tier.name,
            name_en=tier.name_en,
            description=tier.description,
            price=float(tier.price),
            currency=tier.currency,
            duration_days=tier.duration_days,
            features=tier.features or [],
            daily_divination_limit=tier.daily_divination_limit,
            priority_support=tier.priority_support,
            custom_spreads=tier.custom_spreads,
            detailed_interpretation=tier.detailed_interpretation,
            is_active=tier.is_active,
            sort_order=tier.sort_order
        )
        for tier in tiers
    ]

@router.get("/tiers/{tier_id}", response_model=UserTierResponse, summary="获取指定用户等级")
async def get_user_tier(
    tier_id: int,
    order_service: OrderService = Depends(get_order_service)
):
    """获取指定用户等级详情"""
    tier = await order_service.get_user_tier_by_id(tier_id)
    
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户等级不存在"
        )
    
    return UserTierResponse(
        id=tier.id,
        name=tier.name,
        name_en=tier.name_en,
        description=tier.description,
        price=float(tier.price),
        currency=tier.currency,
        duration_days=tier.duration_days,
        features=tier.features or [],
        daily_divination_limit=tier.daily_divination_limit,
        priority_support=tier.priority_support,
        custom_spreads=tier.custom_spreads,
        detailed_interpretation=tier.detailed_interpretation,
        is_active=tier.is_active,
        sort_order=tier.sort_order
    )

@router.post("/", response_model=OrderResponse, summary="创建订单")
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
    _: None = Depends(rate_limit_check)
):
    """创建新订单"""
    try:
        order = await order_service.create_order(
            user_id=current_user.id,
            tier_id=request.tier_id,
            payment_method=request.payment_method,
            currency=request.currency,
            metadata=request.metadata
        )
        
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            user_id=order.user_id,
            tier_id=order.tier_id,
            tier_name=order.tier.name,
            amount=float(order.amount),
            currency=order.currency,
            status=order.status,
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            created_at=format_datetime(order.created_at),
            updated_at=format_datetime(order.updated_at) if order.updated_at else None,
            expires_at=format_datetime(order.expires_at) if order.expires_at else None,
            completed_at=format_datetime(order.completed_at) if order.completed_at else None,
            notes=order.notes,
            metadata=order.metadata
        )
    
    except (ValidationError, ResourceNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[OrderResponse], summary="获取订单列表")
async def get_orders(
    status_filter: Optional[str] = Query(None, description="状态过滤"),
    payment_status: Optional[str] = Query(None, description="支付状态过滤"),
    limit: int = Query(20, ge=1, le=100, description="数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    """获取用户订单列表"""
    orders = await order_service.get_user_orders(
        user_id=current_user.id,
        status=status_filter,
        payment_status=payment_status,
        limit=limit,
        offset=offset
    )
    
    return [
        OrderResponse(
            id=order.id,
            order_number=order.order_number,
            user_id=order.user_id,
            tier_id=order.tier_id,
            tier_name=order.tier.name,
            amount=float(order.amount),
            currency=order.currency,
            status=order.status,
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            created_at=format_datetime(order.created_at),
            updated_at=format_datetime(order.updated_at) if order.updated_at else None,
            expires_at=format_datetime(order.expires_at) if order.expires_at else None,
            completed_at=format_datetime(order.completed_at) if order.completed_at else None,
            notes=order.notes,
            metadata=order.metadata
        )
        for order in orders
    ]

@router.get("/{order_id}", response_model=OrderResponse, summary="获取订单详情")
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    """获取指定订单详情"""
    order = await order_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # 检查权限
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        user_id=order.user_id,
        tier_id=order.tier_id,
        tier_name=order.tier.name,
        amount=float(order.amount),
        currency=order.currency,
        status=order.status,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        created_at=format_datetime(order.created_at),
        updated_at=format_datetime(order.updated_at) if order.updated_at else None,
        expires_at=format_datetime(order.expires_at) if order.expires_at else None,
        completed_at=format_datetime(order.completed_at) if order.completed_at else None,
        notes=order.notes,
        metadata=order.metadata
    )

@router.put("/{order_id}", response_model=OrderResponse, summary="更新订单")
async def update_order(
    order_id: int,
    request: UpdateOrderRequest,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    """更新订单信息"""
    try:
        # 检查订单存在性和权限
        order = await order_service.get_order_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 只有管理员可以更新订单状态
        if request.status and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        # 用户只能更新自己的订单备注
        if order.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        # 过滤非空字段
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有提供要更新的字段"
            )
        
        updated_order = await order_service.update_order_status(
            order_id=order_id,
            **update_data
        )
        
        return OrderResponse(
            id=updated_order.id,
            order_number=updated_order.order_number,
            user_id=updated_order.user_id,
            tier_id=updated_order.tier_id,
            tier_name=updated_order.tier.name,
            amount=float(updated_order.amount),
            currency=updated_order.currency,
            status=updated_order.status,
            payment_method=updated_order.payment_method,
            payment_status=updated_order.payment_status,
            created_at=format_datetime(updated_order.created_at),
            updated_at=format_datetime(updated_order.updated_at) if updated_order.updated_at else None,
            expires_at=format_datetime(updated_order.expires_at) if updated_order.expires_at else None,
            completed_at=format_datetime(updated_order.completed_at) if updated_order.completed_at else None,
            notes=updated_order.notes,
            metadata=updated_order.metadata
        )
    
    except (ValidationError, InsufficientPermissionError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{order_id}/cancel", summary="取消订单")
async def cancel_order(
    order_id: int,
    reason: Optional[str] = Query(None, description="取消原因"),
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    """取消订单"""
    try:
        # 检查订单存在性和权限
        order = await order_service.get_order_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        if order.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        await order_service.cancel_order(order_id, reason)
        
        return {"message": "订单已取消"}
    
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{order_id}/payments", response_model=List[PaymentRecordResponse], summary="获取订单支付记录")
async def get_order_payments(
    order_id: int,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    """获取订单的支付记录"""
    # 检查订单存在性和权限
    order = await order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    payments = await order_service.get_payment_records_by_order(order_id)
    
    return [
        PaymentRecordResponse(
            id=payment.id,
            order_id=payment.order_id,
            transaction_id=payment.transaction_id,
            payment_provider=payment.payment_provider,
            amount=float(payment.amount),
            currency=payment.currency,
            status=payment.status,
            payment_method=payment.payment_method,
            created_at=format_datetime(payment.created_at),
            updated_at=format_datetime(payment.updated_at) if payment.updated_at else None,
            completed_at=format_datetime(payment.completed_at) if payment.completed_at else None,
            failure_reason=payment.failure_reason,
            metadata=payment.metadata
        )
        for payment in payments
    ]

@router.get("/stats/overview", response_model=OrderStatsResponse, summary="获取订单统计")
async def get_order_stats(
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    """获取用户订单统计信息"""
    stats = await order_service.get_order_stats(user_id=current_user.id)
    
    return OrderStatsResponse(**stats)

# 管理员专用接口
@router.get("/admin/list", summary="获取所有订单列表（管理员）")
async def get_all_orders(
    user_id: Optional[int] = Query(None, description="用户ID"),
    status_filter: Optional[str] = Query(None, description="状态过滤"),
    payment_status: Optional[str] = Query(None, description="支付状态过滤"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    pagination: Dict[str, int] = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    """获取所有订单列表（管理员专用）"""
    # 检查管理员权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    try:
        from datetime import datetime
        
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        orders, total = await order_service.get_orders(
            user_id=user_id,
            status=status_filter,
            payment_status=payment_status,
            start_date=start_dt,
            end_date=end_dt,
            limit=pagination["size"],
            offset=pagination["offset"]
        )
        
        # 计算总页数
        pages = (total + pagination["size"] - 1) // pagination["size"]
        
        return {
            "orders": [
                {
                    "id": order.id,
                    "order_number": order.order_number,
                    "user_id": order.user_id,
                    "user_name": f"{order.user.first_name} {order.user.last_name}".strip() if order.user else None,
                    "tier_name": order.tier.name,
                    "amount": float(order.amount),
                    "currency": order.currency,
                    "status": order.status,
                    "payment_method": order.payment_method,
                    "payment_status": order.payment_status,
                    "created_at": format_datetime(order.created_at),
                    "completed_at": format_datetime(order.completed_at) if order.completed_at else None
                }
                for order in orders
            ],
            "total": total,
            "page": pagination["page"],
            "size": pagination["size"],
            "pages": pages
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"日期格式错误: {str(e)}"
        )

@router.get("/admin/stats", summary="获取全局订单统计（管理员）")
async def get_global_order_stats(
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    """获取全局订单统计信息（管理员专用）"""
    # 检查管理员权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    stats = await order_service.get_order_stats()
    revenue_stats = await order_service.get_revenue_stats()
    
    return {
        "order_stats": stats,
        "revenue_stats": revenue_stats
    }

@router.post("/admin/process-expired", summary="处理过期订单（管理员）")
async def process_expired_orders(
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    """处理过期订单（管理员专用）"""
    # 检查管理员权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    processed_count = await order_service.process_expired_orders()
    
    return {
        "message": f"已处理 {processed_count} 个过期订单",
        "processed_count": processed_count
    }