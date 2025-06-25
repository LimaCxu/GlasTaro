# -*- coding: utf-8 -*-
"""
回调相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
import hmac
import hashlib
from datetime import datetime

from core.dependencies import (
    get_payment_service,
    get_order_service,
    get_user_service,
    rate_limit_check
)
from services.payment_service import PaymentService
from services.order_service import OrderService
from services.user_service import UserService
from utils.exceptions import (
    ValidationError,
    ResourceNotFoundError,
    PaymentError
)
from utils.logger import get_logger
from core.config import settings

router = APIRouter()
logger = get_logger(__name__)

# 请求模型
class StripeWebhookRequest(BaseModel):
    """Stripe Webhook请求"""
    id: str
    object: str
    type: str
    data: Dict[str, Any]
    created: int
    livemode: bool
    pending_webhooks: int
    request: Optional[Dict[str, Any]] = None

class PayPalWebhookRequest(BaseModel):
    """PayPal Webhook请求"""
    id: str
    event_type: str
    resource_type: str
    summary: str
    resource: Dict[str, Any]
    create_time: str
    event_version: str
    links: Optional[list] = None

class AlipayNotifyRequest(BaseModel):
    """支付宝异步通知请求"""
    notify_time: str
    notify_type: str
    notify_id: str
    app_id: str
    charset: str
    version: str
    sign_type: str
    sign: str
    trade_no: str
    out_trade_no: str
    trade_status: str
    total_amount: str
    receipt_amount: Optional[str] = None
    buyer_id: Optional[str] = None
    seller_id: Optional[str] = None
    gmt_create: Optional[str] = None
    gmt_payment: Optional[str] = None
    gmt_close: Optional[str] = None

class WechatNotifyRequest(BaseModel):
    """微信支付异步通知请求"""
    id: str
    create_time: str
    event_type: str
    resource_type: str
    resource: Dict[str, Any]
    summary: str

# 响应模型
class CallbackResponse(BaseModel):
    """回调响应"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# Stripe Webhook
@router.post("/stripe", response_model=CallbackResponse, summary="Stripe支付回调")
async def stripe_webhook(
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service),
    order_service: OrderService = Depends(get_order_service),
    _: None = Depends(rate_limit_check)
):
    """处理Stripe支付回调"""
    try:
        # 获取原始请求体
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        if not sig_header:
            logger.warning("Missing Stripe signature header")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing signature header"
            )
        
        # 验证Stripe签名
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        if not endpoint_secret:
            logger.error("Stripe webhook secret not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Webhook secret not configured"
            )
        
        try:
            # 验证签名
            expected_sig = hmac.new(
                endpoint_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # 从header中提取签名
            sig_elements = sig_header.split(',')
            timestamp = None
            signature = None
            
            for element in sig_elements:
                key, value = element.split('=')
                if key == 't':
                    timestamp = value
                elif key == 'v1':
                    signature = value
            
            if not signature or signature != expected_sig:
                logger.warning(f"Invalid Stripe signature: {signature} != {expected_sig}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid signature"
                )
        
        except Exception as e:
            logger.error(f"Stripe signature verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signature verification failed"
            )
        
        # 解析事件数据
        try:
            event_data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        event_type = event_data.get('type')
        event_object = event_data.get('data', {}).get('object', {})
        
        logger.info(f"Received Stripe webhook: {event_type}")
        
        # 处理不同类型的事件
        if event_type == 'payment_intent.succeeded':
            # 支付成功
            payment_intent_id = event_object.get('id')
            metadata = event_object.get('metadata', {})
            order_id = metadata.get('order_id')
            
            if order_id:
                await payment_service.handle_payment_callback(
                    provider='stripe',
                    transaction_id=payment_intent_id,
                    status='completed',
                    amount=event_object.get('amount_received', 0) / 100,  # 转换为元
                    currency=event_object.get('currency', 'usd').upper(),
                    raw_data=event_data
                )
                
                logger.info(f"Stripe payment succeeded for order {order_id}")
        
        elif event_type == 'payment_intent.payment_failed':
            # 支付失败
            payment_intent_id = event_object.get('id')
            metadata = event_object.get('metadata', {})
            order_id = metadata.get('order_id')
            
            if order_id:
                await payment_service.handle_payment_callback(
                    provider='stripe',
                    transaction_id=payment_intent_id,
                    status='failed',
                    amount=event_object.get('amount', 0) / 100,
                    currency=event_object.get('currency', 'usd').upper(),
                    raw_data=event_data
                )
                
                logger.info(f"Stripe payment failed for order {order_id}")
        
        elif event_type == 'charge.dispute.created':
            # 争议创建
            charge_id = event_object.get('charge')
            logger.warning(f"Stripe dispute created for charge {charge_id}")
            # 这里可以添加争议处理逻辑
        
        return CallbackResponse(
            success=True,
            message="Webhook processed successfully",
            data={"event_type": event_type}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stripe webhook processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )

# PayPal Webhook
@router.post("/paypal", response_model=CallbackResponse, summary="PayPal支付回调")
async def paypal_webhook(
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service),
    order_service: OrderService = Depends(get_order_service),
    _: None = Depends(rate_limit_check)
):
    """处理PayPal支付回调"""
    try:
        # 获取原始请求体
        payload = await request.body()
        
        # 验证PayPal签名（如果配置了）
        # 这里可以添加PayPal的签名验证逻辑
        
        # 解析事件数据
        try:
            event_data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        event_type = event_data.get('event_type')
        resource = event_data.get('resource', {})
        
        logger.info(f"Received PayPal webhook: {event_type}")
        
        # 处理不同类型的事件
        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            # 支付完成
            capture_id = resource.get('id')
            custom_id = resource.get('custom_id')  # 我们的订单ID
            amount = resource.get('amount', {})
            
            if custom_id:
                await payment_service.handle_payment_callback(
                    provider='paypal',
                    transaction_id=capture_id,
                    status='completed',
                    amount=float(amount.get('value', 0)),
                    currency=amount.get('currency_code', 'USD'),
                    raw_data=event_data
                )
                
                logger.info(f"PayPal payment completed for order {custom_id}")
        
        elif event_type == 'PAYMENT.CAPTURE.DENIED':
            # 支付被拒绝
            capture_id = resource.get('id')
            custom_id = resource.get('custom_id')
            amount = resource.get('amount', {})
            
            if custom_id:
                await payment_service.handle_payment_callback(
                    provider='paypal',
                    transaction_id=capture_id,
                    status='failed',
                    amount=float(amount.get('value', 0)),
                    currency=amount.get('currency_code', 'USD'),
                    raw_data=event_data
                )
                
                logger.info(f"PayPal payment denied for order {custom_id}")
        
        elif event_type == 'PAYMENT.CAPTURE.REFUNDED':
            # 退款完成
            refund_id = resource.get('id')
            logger.info(f"PayPal refund completed: {refund_id}")
            # 这里可以添加退款处理逻辑
        
        return CallbackResponse(
            success=True,
            message="Webhook processed successfully",
            data={"event_type": event_type}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PayPal webhook processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )

# 支付宝异步通知
@router.post("/alipay", response_model=CallbackResponse, summary="支付宝异步通知")
async def alipay_notify(
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service),
    order_service: OrderService = Depends(get_order_service),
    _: None = Depends(rate_limit_check)
):
    """处理支付宝异步通知"""
    try:
        # 获取表单数据
        form_data = await request.form()
        notify_data = dict(form_data)
        
        logger.info(f"Received Alipay notify: {notify_data.get('out_trade_no')}")
        
        # 验证支付宝签名
        # 这里需要实现支付宝的签名验证逻辑
        # sign = notify_data.pop('sign', '')
        # sign_type = notify_data.get('sign_type', 'RSA2')
        
        # 获取关键信息
        out_trade_no = notify_data.get('out_trade_no')  # 我们的订单号
        trade_no = notify_data.get('trade_no')  # 支付宝交易号
        trade_status = notify_data.get('trade_status')
        total_amount = notify_data.get('total_amount')
        
        if not out_trade_no or not trade_no:
            logger.error("Missing required parameters in Alipay notify")
            return Response(content="fail", media_type="text/plain")
        
        # 处理不同的交易状态
        if trade_status == 'TRADE_SUCCESS' or trade_status == 'TRADE_FINISHED':
            # 支付成功
            await payment_service.handle_payment_callback(
                provider='alipay',
                transaction_id=trade_no,
                status='completed',
                amount=float(total_amount) if total_amount else 0,
                currency='CNY',
                raw_data=notify_data
            )
            
            logger.info(f"Alipay payment succeeded for order {out_trade_no}")
        
        elif trade_status == 'TRADE_CLOSED':
            # 交易关闭
            await payment_service.handle_payment_callback(
                provider='alipay',
                transaction_id=trade_no,
                status='failed',
                amount=float(total_amount) if total_amount else 0,
                currency='CNY',
                raw_data=notify_data
            )
            
            logger.info(f"Alipay payment closed for order {out_trade_no}")
        
        # 返回success给支付宝
        return Response(content="success", media_type="text/plain")
    
    except Exception as e:
        logger.error(f"Alipay notify processing failed: {str(e)}")
        return Response(content="fail", media_type="text/plain")

# 微信支付异步通知
@router.post("/wechat", response_model=CallbackResponse, summary="微信支付异步通知")
async def wechat_notify(
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service),
    order_service: OrderService = Depends(get_order_service),
    _: None = Depends(rate_limit_check)
):
    """处理微信支付异步通知"""
    try:
        # 获取原始请求体
        payload = await request.body()
        
        # 验证微信签名
        # 这里需要实现微信支付的签名验证逻辑
        
        # 解析事件数据
        try:
            event_data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {str(e)}")
            return Response(
                content=json.dumps({"code": "FAIL", "message": "Invalid JSON"}),
                media_type="application/json"
            )
        
        event_type = event_data.get('event_type')
        resource = event_data.get('resource', {})
        
        logger.info(f"Received WeChat webhook: {event_type}")
        
        # 解密资源数据（微信支付v3需要解密）
        # 这里需要实现微信支付的解密逻辑
        # decrypted_data = decrypt_wechat_resource(resource)
        
        # 处理不同类型的事件
        if event_type == 'TRANSACTION.SUCCESS':
            # 支付成功
            # transaction_id = decrypted_data.get('transaction_id')
            # out_trade_no = decrypted_data.get('out_trade_no')
            # amount = decrypted_data.get('amount', {})
            
            # 这里暂时使用模拟数据
            transaction_id = "wechat_" + str(datetime.now().timestamp())
            out_trade_no = "test_order_123"
            
            await payment_service.handle_payment_callback(
                provider='wechat',
                transaction_id=transaction_id,
                status='completed',
                amount=0.01,  # 模拟金额
                currency='CNY',
                raw_data=event_data
            )
            
            logger.info(f"WeChat payment succeeded for order {out_trade_no}")
        
        # 返回成功响应给微信
        return Response(
            content=json.dumps({"code": "SUCCESS", "message": "成功"}),
            media_type="application/json"
        )
    
    except Exception as e:
        logger.error(f"WeChat notify processing failed: {str(e)}")
        return Response(
            content=json.dumps({"code": "FAIL", "message": str(e)}),
            media_type="application/json"
        )

# 通用回调状态查询
@router.get("/status/{payment_id}", response_model=CallbackResponse, summary="查询回调处理状态")
async def get_callback_status(
    payment_id: int,
    payment_service: PaymentService = Depends(get_payment_service),
    _: None = Depends(rate_limit_check)
):
    """查询支付回调处理状态"""
    try:
        payment_record = await payment_service.get_payment_by_id(payment_id)
        
        if not payment_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付记录不存在"
            )
        
        return CallbackResponse(
            success=True,
            message="查询成功",
            data={
                "payment_id": payment_record.id,
                "status": payment_record.status,
                "provider": payment_record.provider,
                "transaction_id": payment_record.transaction_id,
                "amount": float(payment_record.amount),
                "currency": payment_record.currency,
                "created_at": payment_record.created_at.isoformat(),
                "updated_at": payment_record.updated_at.isoformat() if payment_record.updated_at else None
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query callback status failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询失败"
        )

# 手动重试回调处理
@router.post("/retry/{payment_id}", response_model=CallbackResponse, summary="重试回调处理")
async def retry_callback_processing(
    payment_id: int,
    payment_service: PaymentService = Depends(get_payment_service),
    _: None = Depends(rate_limit_check)
):
    """手动重试支付回调处理"""
    try:
        payment_record = await payment_service.get_payment_by_id(payment_id)
        
        if not payment_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付记录不存在"
            )
        
        if payment_record.status == 'completed':
            return CallbackResponse(
                success=True,
                message="支付已完成，无需重试",
                data={"payment_id": payment_id, "status": "completed"}
            )
        
        # 重新处理回调
        await payment_service.handle_payment_callback(
            provider=payment_record.provider,
            transaction_id=payment_record.transaction_id,
            status='completed',  # 假设重试是为了标记为成功
            amount=float(payment_record.amount),
            currency=payment_record.currency,
            raw_data=payment_record.raw_data or {}
        )
        
        logger.info(f"Payment callback retried for payment {payment_id}")
        
        return CallbackResponse(
            success=True,
            message="回调处理重试成功",
            data={"payment_id": payment_id, "status": "completed"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Retry callback processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="重试失败"
        )