# -*- coding: utf-8 -*-
"""
支付相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal

from core.dependencies import (
    get_payment_service,
    get_order_service,
    get_current_user,
    rate_limit_check
)
from models.user import User
from services.payment_service import PaymentService
from services.order_service import OrderService
from utils.exceptions import (
    ValidationError,
    ResourceNotFoundError,
    PaymentError
)
from utils.helpers import format_datetime

router = APIRouter()

# 请求模型
class CreatePaymentIntentRequest(BaseModel):
    """创建支付意图请求"""
    order_id: int = Field(..., description="订单ID")
    payment_method: str = Field(..., description="支付方式")
    return_url: Optional[str] = Field(None, description="返回URL")
    cancel_url: Optional[str] = Field(None, description="取消URL")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class CreateRefundRequest(BaseModel):
    """创建退款请求"""
    payment_id: int = Field(..., description="支付记录ID")
    amount: Optional[float] = Field(None, description="退款金额（不填则全额退款）")
    reason: str = Field(..., description="退款原因")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

# 响应模型
class PaymentIntentResponse(BaseModel):
    """支付意图响应"""
    payment_id: int
    order_id: int
    payment_provider: str
    payment_method: str
    amount: float
    currency: str
    status: str
    client_secret: Optional[str]
    payment_url: Optional[str]
    qr_code_url: Optional[str]
    expires_at: Optional[str]
    metadata: Optional[Dict[str, Any]]

class PaymentRecordResponse(BaseModel):
    """支付记录响应"""
    id: int
    order_id: int
    transaction_id: str
    payment_provider: str
    payment_method: str
    amount: float
    currency: str
    status: str
    created_at: str
    updated_at: Optional[str]
    completed_at: Optional[str]
    failure_reason: Optional[str]
    refund_amount: Optional[float]
    metadata: Optional[Dict[str, Any]]

class RefundResponse(BaseModel):
    """退款响应"""
    id: int
    payment_id: int
    refund_id: str
    amount: float
    currency: str
    status: str
    reason: str
    created_at: str
    completed_at: Optional[str]
    metadata: Optional[Dict[str, Any]]

class PaymentStatsResponse(BaseModel):
    """支付统计响应"""
    total_payments: int
    successful_payments: int
    failed_payments: int
    pending_payments: int
    total_amount: float
    successful_amount: float
    refunded_amount: float
    by_provider: Dict[str, Dict[str, Any]]
    by_method: Dict[str, Dict[str, Any]]

@router.post("/intent", response_model=PaymentIntentResponse, summary="创建支付意图")
async def create_payment_intent(
    request: CreatePaymentIntentRequest,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service),
    order_service: OrderService = Depends(get_order_service),
    _: None = Depends(rate_limit_check)
):
    """创建支付意图"""
    try:
        # 验证订单
        order = await order_service.get_order_by_id(request.order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 检查订单归属
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        # 检查订单状态
        if order.status not in ["pending", "payment_pending"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单状态不允许支付"
            )
        
        # 创建支付意图
        payment_intent = await payment_service.create_payment_intent(
            order=order,
            payment_method=request.payment_method,
            return_url=request.return_url,
            cancel_url=request.cancel_url,
            metadata=request.metadata
        )
        
        return PaymentIntentResponse(
            payment_id=payment_intent["payment_id"],
            order_id=payment_intent["order_id"],
            payment_provider=payment_intent["payment_provider"],
            payment_method=payment_intent["payment_method"],
            amount=payment_intent["amount"],
            currency=payment_intent["currency"],
            status=payment_intent["status"],
            client_secret=payment_intent.get("client_secret"),
            payment_url=payment_intent.get("payment_url"),
            qr_code_url=payment_intent.get("qr_code_url"),
            expires_at=payment_intent.get("expires_at"),
            metadata=payment_intent.get("metadata")
        )
    
    except (ValidationError, PaymentError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建支付意图失败: {str(e)}"
        )

@router.get("/records", response_model=List[PaymentRecordResponse], summary="获取支付记录列表")
async def get_payment_records(
    order_id: Optional[int] = Query(None, description="订单ID"),
    status_filter: Optional[str] = Query(None, description="状态过滤"),
    payment_provider: Optional[str] = Query(None, description="支付提供商"),
    limit: int = Query(20, ge=1, le=100, description="数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """获取用户支付记录列表"""
    payments = await payment_service.get_payment_records(
        user_id=current_user.id,
        order_id=order_id,
        status=status_filter,
        payment_provider=payment_provider,
        limit=limit,
        offset=offset
    )
    
    return [
        PaymentRecordResponse(
            id=payment.id,
            order_id=payment.order_id,
            transaction_id=payment.transaction_id,
            payment_provider=payment.payment_provider,
            payment_method=payment.payment_method,
            amount=float(payment.amount),
            currency=payment.currency,
            status=payment.status,
            created_at=format_datetime(payment.created_at),
            updated_at=format_datetime(payment.updated_at) if payment.updated_at else None,
            completed_at=format_datetime(payment.completed_at) if payment.completed_at else None,
            failure_reason=payment.failure_reason,
            refund_amount=float(payment.refund_amount) if payment.refund_amount else None,
            metadata=payment.metadata
        )
        for payment in payments
    ]

@router.get("/records/{payment_id}", response_model=PaymentRecordResponse, summary="获取支付记录详情")
async def get_payment_record(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """获取指定支付记录详情"""
    payment = await payment_service.get_payment_record_by_id(payment_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支付记录不存在"
        )
    
    # 检查权限
    if payment.order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return PaymentRecordResponse(
        id=payment.id,
        order_id=payment.order_id,
        transaction_id=payment.transaction_id,
        payment_provider=payment.payment_provider,
        payment_method=payment.payment_method,
        amount=float(payment.amount),
        currency=payment.currency,
        status=payment.status,
        created_at=format_datetime(payment.created_at),
        updated_at=format_datetime(payment.updated_at) if payment.updated_at else None,
        completed_at=format_datetime(payment.completed_at) if payment.completed_at else None,
        failure_reason=payment.failure_reason,
        refund_amount=float(payment.refund_amount) if payment.refund_amount else None,
        metadata=payment.metadata
    )

@router.get("/records/transaction/{transaction_id}", response_model=PaymentRecordResponse, summary="通过交易ID获取支付记录")
async def get_payment_by_transaction_id(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """通过交易ID获取支付记录"""
    payment = await payment_service.get_payment_record_by_transaction_id(transaction_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支付记录不存在"
        )
    
    # 检查权限
    if payment.order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return PaymentRecordResponse(
        id=payment.id,
        order_id=payment.order_id,
        transaction_id=payment.transaction_id,
        payment_provider=payment.payment_provider,
        payment_method=payment.payment_method,
        amount=float(payment.amount),
        currency=payment.currency,
        status=payment.status,
        created_at=format_datetime(payment.created_at),
        updated_at=format_datetime(payment.updated_at) if payment.updated_at else None,
        completed_at=format_datetime(payment.completed_at) if payment.completed_at else None,
        failure_reason=payment.failure_reason,
        refund_amount=float(payment.refund_amount) if payment.refund_amount else None,
        metadata=payment.metadata
    )

@router.post("/refund", response_model=RefundResponse, summary="创建退款")
async def create_refund(
    request: CreateRefundRequest,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """创建退款"""
    try:
        # 验证支付记录
        payment = await payment_service.get_payment_record_by_id(request.payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付记录不存在"
            )
        
        # 检查权限（只有管理员可以创建退款）
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        # 检查支付状态
        if payment.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能对已完成的支付进行退款"
            )
        
        # 创建退款
        refund = await payment_service.create_refund(
            payment_id=request.payment_id,
            amount=Decimal(str(request.amount)) if request.amount else None,
            reason=request.reason,
            metadata=request.metadata
        )
        
        return RefundResponse(
            id=refund["id"],
            payment_id=refund["payment_id"],
            refund_id=refund["refund_id"],
            amount=refund["amount"],
            currency=refund["currency"],
            status=refund["status"],
            reason=refund["reason"],
            created_at=refund["created_at"],
            completed_at=refund.get("completed_at"),
            metadata=refund.get("metadata")
        )
    
    except (ValidationError, PaymentError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建退款失败: {str(e)}"
        )

@router.get("/qr-code/{payment_id}", summary="获取支付二维码")
async def get_payment_qr_code(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """获取支付二维码"""
    try:
        # 验证支付记录
        payment = await payment_service.get_payment_record_by_id(payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付记录不存在"
            )
        
        # 检查权限
        if payment.order.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        # 检查支付方式是否支持二维码
        if payment.payment_method not in ["alipay", "wechat_pay"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该支付方式不支持二维码"
            )
        
        # 生成二维码
        qr_code_data = await payment_service.generate_qr_code(
            payment_id=payment_id,
            payment_method=payment.payment_method
        )
        
        return {
            "qr_code_url": qr_code_data["qr_code_url"],
            "payment_url": qr_code_data["payment_url"],
            "expires_at": qr_code_data.get("expires_at")
        }
    
    except PaymentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成二维码失败: {str(e)}"
        )

@router.get("/stats", response_model=PaymentStatsResponse, summary="获取支付统计")
async def get_payment_stats(
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """获取用户支付统计信息"""
    stats = await payment_service.get_payment_stats(user_id=current_user.id)
    
    return PaymentStatsResponse(**stats)

# 管理员专用接口
@router.get("/admin/records", summary="获取所有支付记录（管理员）")
async def get_all_payment_records(
    user_id: Optional[int] = Query(None, description="用户ID"),
    order_id: Optional[int] = Query(None, description="订单ID"),
    status_filter: Optional[str] = Query(None, description="状态过滤"),
    payment_provider: Optional[str] = Query(None, description="支付提供商"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    limit: int = Query(50, ge=1, le=200, description="数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """获取所有支付记录（管理员专用）"""
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
        
        payments, total = await payment_service.get_payment_records(
            user_id=user_id,
            order_id=order_id,
            status=status_filter,
            payment_provider=payment_provider,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit,
            offset=offset
        )
        
        # 计算总页数
        pages = (total + limit - 1) // limit
        
        return {
            "payments": [
                {
                    "id": payment.id,
                    "order_id": payment.order_id,
                    "order_number": payment.order.order_number,
                    "user_id": payment.order.user_id,
                    "user_name": f"{payment.order.user.first_name} {payment.order.user.last_name}".strip() if payment.order.user else None,
                    "transaction_id": payment.transaction_id,
                    "payment_provider": payment.payment_provider,
                    "payment_method": payment.payment_method,
                    "amount": float(payment.amount),
                    "currency": payment.currency,
                    "status": payment.status,
                    "created_at": format_datetime(payment.created_at),
                    "completed_at": format_datetime(payment.completed_at) if payment.completed_at else None,
                    "failure_reason": payment.failure_reason,
                    "refund_amount": float(payment.refund_amount) if payment.refund_amount else None
                }
                for payment in payments
            ],
            "total": total,
            "page": (offset // limit) + 1,
            "size": limit,
            "pages": pages
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"日期格式错误: {str(e)}"
        )

@router.get("/admin/stats", summary="获取全局支付统计（管理员）")
async def get_global_payment_stats(
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """获取全局支付统计信息（管理员专用）"""
    # 检查管理员权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    stats = await payment_service.get_payment_stats()
    
    return PaymentStatsResponse(**stats)

@router.post("/admin/retry/{payment_id}", summary="重试失败支付（管理员）")
async def retry_failed_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """重试失败的支付（管理员专用）"""
    # 检查管理员权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    try:
        # 验证支付记录
        payment = await payment_service.get_payment_record_by_id(payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付记录不存在"
            )
        
        # 检查支付状态
        if payment.status not in ["failed", "cancelled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能重试失败或已取消的支付"
            )
        
        # 重试支付（这里需要根据具体的支付提供商实现）
        result = await payment_service.retry_payment(payment_id)
        
        return {
            "message": "支付重试成功",
            "payment_id": payment_id,
            "new_status": result["status"]
        }
    
    except PaymentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重试支付失败: {str(e)}"
        )