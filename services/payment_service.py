# -*- coding: utf-8 -*-
"""
支付服务模块
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload

from models.order import Order, Payment, UserTier
from models.user import User
from config.redis_config import RedisManager, CacheKeys
from utils.exceptions import (
    PaymentError,
    ValidationError,
    ResourceNotFoundError,
    BusinessLogicError,
    ExternalServiceError
)
from utils.validators import validate_amount, validate_currency_code
from utils.helpers import generate_short_id, get_current_timestamp
from core.config import settings

logger = logging.getLogger(__name__)

class PaymentService:
    """支付服务"""
    
    def __init__(self, db: AsyncSession, redis: RedisManager):
        self.db = db
        self.redis = redis
        self._stripe_client = None
        self._paypal_client = None
    
    @property
    def stripe_client(self):
        """Stripe客户端（懒加载）"""
        if self._stripe_client is None and settings.STRIPE_SECRET_KEY:
            try:
                import stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                self._stripe_client = stripe
            except ImportError:
                logger.warning("Stripe库未安装")
        return self._stripe_client
    
    @property
    def paypal_client(self):
        """PayPal客户端（懒加载）"""
        if self._paypal_client is None and settings.PAYPAL_CLIENT_ID:
            try:
                # 这里应该初始化PayPal客户端
                # 由于PayPal SDK比较复杂，这里只是示例
                pass
            except ImportError:
                logger.warning("PayPal库未安装")
        return self._paypal_client
    
    # 支付意图创建
    async def create_payment_intent(
        self,
        order_id: int,
        payment_method: str = "stripe",
        return_url: str = None,
        cancel_url: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """创建支付意图"""
        # 获取订单信息
        order = await self._get_order_with_validation(order_id)
        
        # 根据支付方式创建支付意图
        if payment_method == "stripe":
            return await self._create_stripe_payment_intent(order, metadata)
        elif payment_method == "paypal":
            return await self._create_paypal_payment_intent(order, return_url, cancel_url, metadata)
        elif payment_method == "alipay":
            return await self._create_alipay_payment_intent(order, return_url, cancel_url, metadata)
        elif payment_method == "wechat":
            return await self._create_wechat_payment_intent(order, metadata)
        else:
            raise ValidationError(f"不支持的支付方式: {payment_method}")
    
    async def _get_order_with_validation(self, order_id: int) -> Order:
        """获取订单并验证"""
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.user), selectinload(Order.tier))
            .where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise ResourceNotFoundError("订单不存在")
        
        if order.status != "pending":
            raise BusinessLogicError(f"订单状态无效: {order.status}")
        
        if order.expires_at <= datetime.utcnow():
            raise BusinessLogicError("订单已过期")
        
        return order
    
    # Stripe支付
    async def _create_stripe_payment_intent(
        self,
        order: Order,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """创建Stripe支付意图"""
        if not self.stripe_client:
            raise ExternalServiceError("Stripe服务未配置")
        
        try:
            # 转换金额为分
            amount_cents = int(order.amount * 100)
            
            # 创建支付意图
            intent = self.stripe_client.PaymentIntent.create(
                amount=amount_cents,
                currency=order.currency.lower(),
                metadata={
                    "order_id": str(order.id),
                    "order_number": order.order_number,
                    "user_id": str(order.user_id),
                    **(metadata or {})
                },
                description=order.description,
                automatic_payment_methods={
                    "enabled": True
                }
            )
            
            # 创建支付记录
            payment = Payment(
                order_id=order.id,
                amount=order.amount,
                currency=order.currency,
                provider="stripe",
                transaction_id=intent.id,
                status="pending",
                provider_data={
                    "payment_intent_id": intent.id,
                    "client_secret": intent.client_secret
                }
            )
            
            self.db.add(payment)
            await self.db.commit()
            await self.db.refresh(payment)
            
            logger.info(f"创建Stripe支付意图: {intent.id} (订单: {order.order_number})")
            
            return {
                "payment_id": payment.id,
                "provider": "stripe",
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": order.amount,
                "currency": order.currency
            }
        
        except Exception as e:
            logger.error(f"创建Stripe支付意图失败: {e}")
            raise PaymentError(f"创建支付失败: {str(e)}")
    
    # PayPal支付
    async def _create_paypal_payment_intent(
        self,
        order: Order,
        return_url: str = None,
        cancel_url: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """创建PayPal支付意图"""
        # PayPal支付实现
        # 这里需要集成PayPal SDK
        
        # 创建支付记录
        payment = Payment(
            order_id=order.id,
            amount=order.amount,
            currency=order.currency,
            provider="paypal",
            transaction_id=f"paypal_{generate_short_id()}",
            status="pending",
            provider_data={
                "return_url": return_url,
                "cancel_url": cancel_url,
                "metadata": metadata or {}
            }
        )
        
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        
        # 这里应该返回PayPal的支付URL
        payment_url = f"https://www.paypal.com/checkoutnow?token={payment.transaction_id}"
        
        return {
            "payment_id": payment.id,
            "provider": "paypal",
            "payment_url": payment_url,
            "transaction_id": payment.transaction_id,
            "amount": order.amount,
            "currency": order.currency
        }
    
    # 支付宝支付
    async def _create_alipay_payment_intent(
        self,
        order: Order,
        return_url: str = None,
        cancel_url: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """创建支付宝支付意图"""
        # 支付宝支付实现
        # 这里需要集成支付宝SDK
        
        # 创建支付记录
        payment = Payment(
            order_id=order.id,
            amount=order.amount,
            currency=order.currency,
            provider="alipay",
            transaction_id=f"alipay_{generate_short_id()}",
            status="pending",
            provider_data={
                "return_url": return_url,
                "cancel_url": cancel_url,
                "metadata": metadata or {}
            }
        )
        
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        
        # 这里应该返回支付宝的支付URL或二维码
        payment_url = f"https://openapi.alipay.com/gateway.do?trade_no={payment.transaction_id}"
        
        return {
            "payment_id": payment.id,
            "provider": "alipay",
            "payment_url": payment_url,
            "qr_code": f"data:image/png;base64,{self._generate_qr_code(payment_url)}",
            "transaction_id": payment.transaction_id,
            "amount": order.amount,
            "currency": order.currency
        }
    
    # 微信支付
    async def _create_wechat_payment_intent(
        self,
        order: Order,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """创建微信支付意图"""
        # 微信支付实现
        # 这里需要集成微信支付SDK
        
        # 创建支付记录
        payment = Payment(
            order_id=order.id,
            amount=order.amount,
            currency=order.currency,
            provider="wechat",
            transaction_id=f"wechat_{generate_short_id()}",
            status="pending",
            provider_data={
                "metadata": metadata or {}
            }
        )
        
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        
        # 这里应该返回微信支付的二维码
        payment_url = f"weixin://wxpay/bizpayurl?pr={payment.transaction_id}"
        
        return {
            "payment_id": payment.id,
            "provider": "wechat",
            "qr_code": f"data:image/png;base64,{self._generate_qr_code(payment_url)}",
            "transaction_id": payment.transaction_id,
            "amount": order.amount,
            "currency": order.currency
        }
    
    # 支付状态处理
    async def handle_payment_webhook(
        self,
        provider: str,
        payload: Dict[str, Any],
        signature: str = None
    ) -> Dict[str, Any]:
        """处理支付回调"""
        if provider == "stripe":
            return await self._handle_stripe_webhook(payload, signature)
        elif provider == "paypal":
            return await self._handle_paypal_webhook(payload)
        elif provider == "alipay":
            return await self._handle_alipay_webhook(payload)
        elif provider == "wechat":
            return await self._handle_wechat_webhook(payload)
        else:
            raise ValidationError(f"不支持的支付提供商: {provider}")
    
    async def _handle_stripe_webhook(
        self,
        payload: Dict[str, Any],
        signature: str = None
    ) -> Dict[str, Any]:
        """处理Stripe回调"""
        if not self.stripe_client:
            raise ExternalServiceError("Stripe服务未配置")
        
        try:
            # 验证webhook签名
            if signature and settings.STRIPE_WEBHOOK_SECRET:
                event = self.stripe_client.Webhook.construct_event(
                    payload, signature, settings.STRIPE_WEBHOOK_SECRET
                )
            else:
                event = payload
            
            event_type = event.get("type")
            event_data = event.get("data", {}).get("object", {})
            
            if event_type == "payment_intent.succeeded":
                return await self._process_successful_payment(
                    provider="stripe",
                    transaction_id=event_data.get("id"),
                    amount=Decimal(str(event_data.get("amount", 0) / 100)),
                    currency=event_data.get("currency", "usd").upper(),
                    provider_data=event_data
                )
            
            elif event_type == "payment_intent.payment_failed":
                return await self._process_failed_payment(
                    provider="stripe",
                    transaction_id=event_data.get("id"),
                    failure_reason=event_data.get("last_payment_error", {}).get("message"),
                    provider_data=event_data
                )
            
            return {"status": "ignored", "event_type": event_type}
        
        except Exception as e:
            logger.error(f"处理Stripe回调失败: {e}")
            raise PaymentError(f"处理支付回调失败: {str(e)}")
    
    async def _handle_paypal_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理PayPal回调"""
        # PayPal回调处理实现
        event_type = payload.get("event_type")
        resource = payload.get("resource", {})
        
        if event_type == "PAYMENT.CAPTURE.COMPLETED":
            return await self._process_successful_payment(
                provider="paypal",
                transaction_id=resource.get("id"),
                amount=Decimal(str(resource.get("amount", {}).get("value", 0))),
                currency=resource.get("amount", {}).get("currency_code", "USD"),
                provider_data=resource
            )
        
        return {"status": "ignored", "event_type": event_type}
    
    async def _handle_alipay_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理支付宝回调"""
        # 支付宝回调处理实现
        trade_status = payload.get("trade_status")
        
        if trade_status == "TRADE_SUCCESS":
            return await self._process_successful_payment(
                provider="alipay",
                transaction_id=payload.get("out_trade_no"),
                amount=Decimal(str(payload.get("total_amount", 0))),
                currency="CNY",
                provider_data=payload
            )
        
        return {"status": "ignored", "trade_status": trade_status}
    
    async def _handle_wechat_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理微信支付回调"""
        # 微信支付回调处理实现
        result_code = payload.get("result_code")
        
        if result_code == "SUCCESS":
            return await self._process_successful_payment(
                provider="wechat",
                transaction_id=payload.get("out_trade_no"),
                amount=Decimal(str(payload.get("total_fee", 0) / 100)),
                currency="CNY",
                provider_data=payload
            )
        
        return {"status": "ignored", "result_code": result_code}
    
    async def _process_successful_payment(
        self,
        provider: str,
        transaction_id: str,
        amount: Decimal,
        currency: str,
        provider_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """处理成功支付"""
        # 查找支付记录
        result = await self.db.execute(
            select(Payment)
            .options(selectinload(Payment.order))
            .where(
                and_(
                    Payment.provider == provider,
                    Payment.transaction_id == transaction_id
                )
            )
        )
        payment = result.scalar_one_or_none()
        
        if not payment:
            logger.warning(f"未找到支付记录: {provider} - {transaction_id}")
            return {"status": "payment_not_found"}
        
        if payment.status == "completed":
            logger.info(f"支付已处理: {transaction_id}")
            return {"status": "already_processed"}
        
        # 验证金额
        if payment.amount != amount:
            logger.error(f"支付金额不匹配: 期望 {payment.amount}, 实际 {amount}")
            return {"status": "amount_mismatch"}
        
        # 更新支付状态
        payment.status = "completed"
        payment.completed_at = datetime.utcnow()
        if provider_data:
            payment.provider_data.update(provider_data)
        
        # 更新订单状态
        order = payment.order
        order.status = "paid"
        order.payment_provider = provider
        order.payment_id = transaction_id
        order.paid_at = datetime.utcnow()
        
        await self.db.commit()
        
        # 处理订单完成后的业务逻辑
        await self._handle_order_completion(order)
        
        logger.info(f"支付处理成功: {transaction_id} (订单: {order.order_number})")
        
        return {
            "status": "success",
            "payment_id": payment.id,
            "order_id": order.id,
            "order_number": order.order_number
        }
    
    async def _process_failed_payment(
        self,
        provider: str,
        transaction_id: str,
        failure_reason: str = None,
        provider_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """处理失败支付"""
        # 查找支付记录
        result = await self.db.execute(
            select(Payment)
            .where(
                and_(
                    Payment.provider == provider,
                    Payment.transaction_id == transaction_id
                )
            )
        )
        payment = result.scalar_one_or_none()
        
        if not payment:
            logger.warning(f"未找到支付记录: {provider} - {transaction_id}")
            return {"status": "payment_not_found"}
        
        # 更新支付状态
        payment.status = "failed"
        payment.failure_reason = failure_reason
        if provider_data:
            payment.provider_data.update(provider_data)
        
        await self.db.commit()
        
        logger.info(f"支付失败: {transaction_id} - {failure_reason}")
        
        return {
            "status": "failed",
            "payment_id": payment.id,
            "failure_reason": failure_reason
        }
    
    async def _handle_order_completion(self, order: Order):
        """处理订单完成后的业务逻辑"""
        # 这里可以添加订单完成后的处理逻辑
        # 例如：激活用户会员、发送确认邮件等
        
        # 激活用户会员（示例）
        if order.tier:
            await self._activate_user_membership(order.user_id, order.tier_id, order.order_type)
        
        # 发送确认通知（示例）
        await self._send_payment_confirmation(order)
    
    async def _activate_user_membership(self, user_id: int, tier_id: int, order_type: str):
        """激活用户会员"""
        # 这里应该实现会员激活逻辑
        # 例如：更新用户等级、设置过期时间等
        logger.info(f"激活用户会员: 用户 {user_id}, 等级 {tier_id}, 类型 {order_type}")
    
    async def _send_payment_confirmation(self, order: Order):
        """发送支付确认"""
        # 这里应该实现发送确认通知的逻辑
        # 例如：发送邮件、Telegram消息等
        logger.info(f"发送支付确认: 订单 {order.order_number}")
    
    # 退款处理
    async def create_refund(
        self,
        payment_id: int,
        amount: Decimal = None,
        reason: str = None,
        admin_id: int = None
    ) -> Dict[str, Any]:
        """创建退款"""
        # 获取支付记录
        result = await self.db.execute(
            select(Payment)
            .options(selectinload(Payment.order))
            .where(Payment.id == payment_id)
        )
        payment = result.scalar_one_or_none()
        
        if not payment:
            raise ResourceNotFoundError("支付记录不存在")
        
        if payment.status != "completed":
            raise BusinessLogicError("只能退款已完成的支付")
        
        # 默认全额退款
        if amount is None:
            amount = payment.amount
        
        if amount > payment.amount:
            raise ValidationError("退款金额不能超过支付金额")
        
        # 根据支付提供商处理退款
        if payment.provider == "stripe":
            return await self._create_stripe_refund(payment, amount, reason)
        elif payment.provider == "paypal":
            return await self._create_paypal_refund(payment, amount, reason)
        else:
            raise BusinessLogicError(f"不支持的退款提供商: {payment.provider}")
    
    async def _create_stripe_refund(
        self,
        payment: Payment,
        amount: Decimal,
        reason: str = None
    ) -> Dict[str, Any]:
        """创建Stripe退款"""
        if not self.stripe_client:
            raise ExternalServiceError("Stripe服务未配置")
        
        try:
            # 创建退款
            refund = self.stripe_client.Refund.create(
                payment_intent=payment.transaction_id,
                amount=int(amount * 100),  # 转换为分
                reason=reason or "requested_by_customer",
                metadata={
                    "payment_id": str(payment.id),
                    "order_id": str(payment.order_id)
                }
            )
            
            # 更新支付状态
            if amount == payment.amount:
                payment.status = "refunded"
            else:
                payment.status = "partially_refunded"
            
            # 更新订单状态
            order = payment.order
            if amount == payment.amount:
                order.status = "refunded"
            
            await self.db.commit()
            
            logger.info(f"创建Stripe退款: {refund.id} (金额: {amount})")
            
            return {
                "refund_id": refund.id,
                "amount": amount,
                "status": refund.status,
                "provider": "stripe"
            }
        
        except Exception as e:
            logger.error(f"创建Stripe退款失败: {e}")
            raise PaymentError(f"创建退款失败: {str(e)}")
    
    async def _create_paypal_refund(
        self,
        payment: Payment,
        amount: Decimal,
        reason: str = None
    ) -> Dict[str, Any]:
        """创建PayPal退款"""
        # PayPal退款实现
        # 这里需要集成PayPal退款API
        
        refund_id = f"paypal_refund_{generate_short_id()}"
        
        # 更新支付状态
        if amount == payment.amount:
            payment.status = "refunded"
        else:
            payment.status = "partially_refunded"
        
        await self.db.commit()
        
        return {
            "refund_id": refund_id,
            "amount": amount,
            "status": "pending",
            "provider": "paypal"
        }
    
    # 支付查询
    async def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """根据ID获取支付记录"""
        result = await self.db.execute(
            select(Payment)
            .options(selectinload(Payment.order))
            .where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_payment_by_transaction_id(
        self,
        transaction_id: str,
        provider: str = None
    ) -> Optional[Payment]:
        """根据交易ID获取支付记录"""
        query = select(Payment).where(Payment.transaction_id == transaction_id)
        
        if provider:
            query = query.where(Payment.provider == provider)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_order_payments(self, order_id: int) -> List[Payment]:
        """获取订单的所有支付记录"""
        result = await self.db.execute(
            select(Payment)
            .where(Payment.order_id == order_id)
            .order_by(desc(Payment.created_at))
        )
        return result.scalars().all()
    
    # 工具方法
    def _generate_qr_code(self, data: str) -> str:
        """生成二维码（Base64编码）"""
        try:
            import qrcode
            from io import BytesIO
            import base64
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            
            return base64.b64encode(buffer.getvalue()).decode()
        
        except ImportError:
            logger.warning("qrcode库未安装，无法生成二维码")
            return ""
    
    # 支付统计
    async def get_payment_stats(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        provider: str = None
    ) -> Dict[str, Any]:
        """获取支付统计"""
        query = select(Payment)
        
        if start_date:
            query = query.where(Payment.created_at >= start_date)
        if end_date:
            query = query.where(Payment.created_at <= end_date)
        if provider:
            query = query.where(Payment.provider == provider)
        
        # 总支付数
        total_result = await self.db.execute(
            select(func.count(Payment.id)).select_from(query.subquery())
        )
        total_payments = total_result.scalar()
        
        # 按状态统计
        status_result = await self.db.execute(
            select(Payment.status, func.count(Payment.id))
            .select_from(query.subquery())
            .group_by(Payment.status)
        )
        status_stats = dict(status_result.fetchall())
        
        # 按提供商统计
        provider_result = await self.db.execute(
            select(Payment.provider, func.count(Payment.id), func.sum(Payment.amount))
            .select_from(query.subquery())
            .group_by(Payment.provider)
        )
        provider_stats = {
            row.provider: {"count": row[1], "amount": float(row[2] or 0)}
            for row in provider_result.fetchall()
        }
        
        # 成功支付总额
        success_amount_result = await self.db.execute(
            select(func.sum(Payment.amount))
            .select_from(query.subquery())
            .where(Payment.status == "completed")
        )
        success_amount = float(success_amount_result.scalar() or 0)
        
        return {
            "total_payments": total_payments,
            "status_stats": status_stats,
            "provider_stats": provider_stats,
            "success_amount": success_amount,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }