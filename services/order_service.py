# -*- coding: utf-8 -*-
"""
订单服务模块
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload

from models.order import Order, UserTier, Payment
from models.user import User
from config.redis_config import RedisManager, CacheKeys
from utils.exceptions import (
    PaymentError,
    ValidationError,
    ResourceNotFoundError,
    BusinessLogicError
)
from utils.validators import validate_amount, validate_currency_code
from utils.helpers import generate_short_id, get_current_timestamp

logger = logging.getLogger(__name__)

class OrderService:
    """订单服务"""
    
    def __init__(self, db: AsyncSession, redis: RedisManager):
        self.db = db
        self.redis = redis
    
    # 用户等级管理
    async def get_user_tiers(self, active_only: bool = True) -> List[UserTier]:
        """获取用户等级列表"""
        cache_key = CacheKeys.user_tiers(active_only)
        
        # 尝试从缓存获取
        cached_tiers = await self.redis.get(cache_key)
        if cached_tiers:
            return cached_tiers
        
        # 从数据库查询
        query = select(UserTier)
        if active_only:
            query = query.where(UserTier.is_active == True)
        
        query = query.order_by(UserTier.monthly_price)
        result = await self.db.execute(query)
        tiers = result.scalars().all()
        
        # 缓存结果
        await self.redis.set(cache_key, tiers, expire=3600)  # 缓存1小时
        
        return tiers
    
    async def get_user_tier_by_id(self, tier_id: int) -> Optional[UserTier]:
        """根据ID获取用户等级"""
        cache_key = CacheKeys.user_tier(tier_id)
        
        # 尝试从缓存获取
        cached_tier = await self.redis.get(cache_key)
        if cached_tier:
            return cached_tier
        
        # 从数据库查询
        result = await self.db.execute(
            select(UserTier).where(UserTier.id == tier_id)
        )
        tier = result.scalar_one_or_none()
        
        if tier:
            # 缓存结果
            await self.redis.set(cache_key, tier, expire=3600)
        
        return tier
    
    async def create_user_tier(
        self,
        name: str,
        description: str,
        daily_free_divinations: int,
        monthly_price: Decimal,
        yearly_price: Decimal,
        features: Dict[str, Any],
        is_active: bool = True
    ) -> UserTier:
        """创建用户等级"""
        # 验证价格
        if not validate_amount(monthly_price) or not validate_amount(yearly_price):
            raise ValidationError("价格格式无效")
        
        if monthly_price < 0 or yearly_price < 0:
            raise ValidationError("价格不能为负数")
        
        if daily_free_divinations < 0:
            raise ValidationError("每日免费占卜次数不能为负数")
        
        # 创建等级
        tier = UserTier(
            name=name,
            description=description,
            daily_free_divinations=daily_free_divinations,
            monthly_price=monthly_price,
            yearly_price=yearly_price,
            features=features,
            is_active=is_active
        )
        
        self.db.add(tier)
        await self.db.commit()
        await self.db.refresh(tier)
        
        # 清除缓存
        await self._clear_tier_cache()
        
        logger.info(f"创建用户等级: {tier.name} (ID: {tier.id})")
        return tier
    
    async def update_user_tier(
        self,
        tier_id: int,
        **updates
    ) -> Optional[UserTier]:
        """更新用户等级"""
        tier = await self.get_user_tier_by_id(tier_id)
        if not tier:
            raise ResourceNotFoundError("用户等级不存在")
        
        # 验证更新数据
        if 'monthly_price' in updates:
            if not validate_amount(updates['monthly_price']):
                raise ValidationError("月费价格格式无效")
        
        if 'yearly_price' in updates:
            if not validate_amount(updates['yearly_price']):
                raise ValidationError("年费价格格式无效")
        
        if 'daily_free_divinations' in updates:
            if updates['daily_free_divinations'] < 0:
                raise ValidationError("每日免费占卜次数不能为负数")
        
        # 更新字段
        for key, value in updates.items():
            if hasattr(tier, key):
                setattr(tier, key, value)
        
        tier.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(tier)
        
        # 清除缓存
        await self._clear_tier_cache(tier_id)
        
        logger.info(f"更新用户等级: {tier.name} (ID: {tier.id})")
        return tier
    
    # 订单管理
    async def create_order(
        self,
        user_id: int,
        tier_id: int,
        order_type: str,
        amount: Decimal,
        currency: str = "USD",
        payment_method: str = "stripe",
        description: str = None,
        metadata: Dict[str, Any] = None
    ) -> Order:
        """创建订单"""
        # 验证参数
        if not validate_amount(amount):
            raise ValidationError("订单金额格式无效")
        
        if not validate_currency_code(currency):
            raise ValidationError("货币代码无效")
        
        if order_type not in ["monthly", "yearly"]:
            raise ValidationError("订单类型无效")
        
        # 验证用户等级
        tier = await self.get_user_tier_by_id(tier_id)
        if not tier or not tier.is_active:
            raise ResourceNotFoundError("用户等级不存在或已停用")
        
        # 验证金额是否匹配
        expected_amount = tier.monthly_price if order_type == "monthly" else tier.yearly_price
        if amount != expected_amount:
            raise ValidationError(f"订单金额不匹配，期望: {expected_amount}，实际: {amount}")
        
        # 检查用户是否已有未完成的订单
        existing_order = await self.get_user_pending_order(user_id)
        if existing_order:
            raise BusinessLogicError("用户已有未完成的订单")
        
        # 生成订单号
        order_number = f"ORD-{generate_short_id()}-{get_current_timestamp()}"
        
        # 创建订单
        order = Order(
            user_id=user_id,
            tier_id=tier_id,
            order_number=order_number,
            order_type=order_type,
            amount=amount,
            currency=currency,
            status="pending",
            payment_method=payment_method,
            description=description or f"{tier.name} - {order_type}",
            metadata=metadata or {},
            expires_at=datetime.utcnow() + timedelta(hours=24)  # 24小时后过期
        )
        
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        
        # 缓存订单
        cache_key = CacheKeys.order(order.id)
        await self.redis.set(cache_key, order, expire=86400)  # 缓存24小时
        
        logger.info(f"创建订单: {order.order_number} (用户: {user_id}, 金额: {amount} {currency})")
        return order
    
    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """根据ID获取订单"""
        cache_key = CacheKeys.order(order_id)
        
        # 尝试从缓存获取
        cached_order = await self.redis.get(cache_key)
        if cached_order:
            return cached_order
        
        # 从数据库查询
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.user), selectinload(Order.tier))
            .where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if order:
            # 缓存结果
            await self.redis.set(cache_key, order, expire=3600)
        
        return order
    
    async def get_order_by_number(self, order_number: str) -> Optional[Order]:
        """根据订单号获取订单"""
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.user), selectinload(Order.tier))
            .where(Order.order_number == order_number)
        )
        return result.scalar_one_or_none()
    
    async def get_user_orders(
        self,
        user_id: int,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Order]:
        """获取用户订单列表"""
        query = select(Order).where(Order.user_id == user_id)
        
        if status:
            query = query.where(Order.status == status)
        
        query = query.order_by(desc(Order.created_at)).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_user_pending_order(self, user_id: int) -> Optional[Order]:
        """获取用户待支付订单"""
        result = await self.db.execute(
            select(Order)
            .where(
                and_(
                    Order.user_id == user_id,
                    Order.status == "pending",
                    Order.expires_at > datetime.utcnow()
                )
            )
            .order_by(desc(Order.created_at))
        )
        return result.scalar_one_or_none()
    
    async def update_order_status(
        self,
        order_id: int,
        status: str,
        payment_provider: str = None,
        payment_id: str = None,
        paid_at: datetime = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[Order]:
        """更新订单状态"""
        order = await self.get_order_by_id(order_id)
        if not order:
            raise ResourceNotFoundError("订单不存在")
        
        # 验证状态转换
        valid_transitions = {
            "pending": ["paid", "cancelled", "expired"],
            "paid": ["refunded"],
            "cancelled": [],
            "expired": [],
            "refunded": []
        }
        
        if status not in valid_transitions.get(order.status, []):
            raise BusinessLogicError(f"无效的状态转换: {order.status} -> {status}")
        
        # 更新订单
        order.status = status
        if payment_provider:
            order.payment_provider = payment_provider
        if payment_id:
            order.payment_id = payment_id
        if paid_at:
            order.paid_at = paid_at
        if metadata:
            order.metadata.update(metadata)
        
        order.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(order)
        
        # 更新缓存
        cache_key = CacheKeys.order(order.id)
        await self.redis.set(cache_key, order, expire=3600)
        
        logger.info(f"更新订单状态: {order.order_number} -> {status}")
        return order
    
    async def cancel_order(self, order_id: int, reason: str = None) -> Optional[Order]:
        """取消订单"""
        order = await self.get_order_by_id(order_id)
        if not order:
            raise ResourceNotFoundError("订单不存在")
        
        if order.status != "pending":
            raise BusinessLogicError("只能取消待支付订单")
        
        # 更新订单状态
        metadata = order.metadata.copy()
        if reason:
            metadata["cancel_reason"] = reason
        
        return await self.update_order_status(
            order_id=order_id,
            status="cancelled",
            metadata=metadata
        )
    
    async def expire_orders(self) -> int:
        """过期订单处理"""
        # 查找过期的待支付订单
        result = await self.db.execute(
            select(Order)
            .where(
                and_(
                    Order.status == "pending",
                    Order.expires_at <= datetime.utcnow()
                )
            )
        )
        expired_orders = result.scalars().all()
        
        count = 0
        for order in expired_orders:
            await self.update_order_status(
                order_id=order.id,
                status="expired"
            )
            count += 1
        
        if count > 0:
            logger.info(f"处理了 {count} 个过期订单")
        
        return count
    
    # 支付记录管理
    async def create_payment(
        self,
        order_id: int,
        amount: Decimal,
        currency: str,
        provider: str,
        transaction_id: str,
        status: str = "pending",
        provider_data: Dict[str, Any] = None
    ) -> Payment:
        """创建支付记录"""
        # 验证订单
        order = await self.get_order_by_id(order_id)
        if not order:
            raise ResourceNotFoundError("订单不存在")
        
        # 验证金额
        if amount != order.amount:
            raise ValidationError(f"支付金额不匹配订单金额: {amount} != {order.amount}")
        
        # 创建支付记录
        payment = Payment(
            order_id=order_id,
            amount=amount,
            currency=currency,
            provider=provider,
            transaction_id=transaction_id,
            status=status,
            provider_data=provider_data or {}
        )
        
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        
        logger.info(f"创建支付记录: {transaction_id} (订单: {order.order_number})")
        return payment
    
    async def update_payment_status(
        self,
        payment_id: int,
        status: str,
        completed_at: datetime = None,
        failure_reason: str = None,
        provider_data: Dict[str, Any] = None
    ) -> Optional[Payment]:
        """更新支付状态"""
        result = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        payment = result.scalar_one_or_none()
        
        if not payment:
            raise ResourceNotFoundError("支付记录不存在")
        
        # 更新支付记录
        payment.status = status
        if completed_at:
            payment.completed_at = completed_at
        if failure_reason:
            payment.failure_reason = failure_reason
        if provider_data:
            payment.provider_data.update(provider_data)
        
        payment.updated_at = datetime.utcnow()
        
        # 如果支付成功，更新订单状态
        if status == "completed":
            await self.update_order_status(
                order_id=payment.order_id,
                status="paid",
                payment_provider=payment.provider,
                payment_id=payment.transaction_id,
                paid_at=completed_at or datetime.utcnow()
            )
        
        await self.db.commit()
        await self.db.refresh(payment)
        
        logger.info(f"更新支付状态: {payment.transaction_id} -> {status}")
        return payment
    
    # 统计和报告
    async def get_order_stats(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """获取订单统计"""
        query = select(Order)
        
        if start_date:
            query = query.where(Order.created_at >= start_date)
        if end_date:
            query = query.where(Order.created_at <= end_date)
        
        # 总订单数
        total_result = await self.db.execute(
            select(func.count(Order.id)).select_from(query.subquery())
        )
        total_orders = total_result.scalar()
        
        # 按状态统计
        status_result = await self.db.execute(
            select(Order.status, func.count(Order.id))
            .select_from(query.subquery())
            .group_by(Order.status)
        )
        status_stats = dict(status_result.fetchall())
        
        # 收入统计
        revenue_result = await self.db.execute(
            select(func.sum(Order.amount))
            .select_from(query.subquery())
            .where(Order.status == "paid")
        )
        total_revenue = revenue_result.scalar() or Decimal("0")
        
        return {
            "total_orders": total_orders,
            "status_stats": status_stats,
            "total_revenue": float(total_revenue),
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def get_revenue_by_period(
        self,
        period: str = "daily",
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Dict[str, Any]]:
        """按时间段获取收入统计"""
        # 根据周期确定日期格式
        date_format = {
            "daily": "%Y-%m-%d",
            "weekly": "%Y-%W",
            "monthly": "%Y-%m",
            "yearly": "%Y"
        }.get(period, "%Y-%m-%d")
        
        query = (
            select(
                func.date_format(Order.created_at, date_format).label("period"),
                func.sum(Order.amount).label("revenue"),
                func.count(Order.id).label("orders")
            )
            .where(Order.status == "paid")
            .group_by("period")
            .order_by("period")
        )
        
        if start_date:
            query = query.where(Order.created_at >= start_date)
        if end_date:
            query = query.where(Order.created_at <= end_date)
        
        result = await self.db.execute(query)
        
        return [
            {
                "period": row.period,
                "revenue": float(row.revenue),
                "orders": row.orders
            }
            for row in result.fetchall()
        ]
    
    # 缓存管理
    async def _clear_tier_cache(self, tier_id: int = None):
        """清除等级缓存"""
        if tier_id:
            await self.redis.delete(CacheKeys.user_tier(tier_id))
        
        # 清除等级列表缓存
        await self.redis.delete(CacheKeys.user_tiers(True))
        await self.redis.delete(CacheKeys.user_tiers(False))
    
    async def clear_order_cache(self, order_id: int):
        """清除订单缓存"""
        cache_key = CacheKeys.order(order_id)
        await self.redis.delete(cache_key)