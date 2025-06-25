# -*- coding: utf-8 -*-
"""
订单和支付相关数据库模型
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    BigInteger, String, Boolean, DateTime, Integer, 
    Text, JSON, ForeignKey, DECIMAL, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel, BaseUUIDModel

class UserTier(BaseModel):
    """用户等级表"""
    __tablename__ = "user_tiers"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="等级ID"
    )
    
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="等级名称"
    )
    
    daily_free_readings: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
        comment="每日免费占卜次数"
    )
    
    monthly_price: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2),
        nullable=True,
        comment="月费价格"
    )
    
    yearly_price: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2),
        nullable=True,
        comment="年费价格"
    )
    
    features: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="功能特性"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )
    
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="排序顺序"
    )
    
    # 关联关系
    orders = relationship("Order", back_populates="tier")
    
    def __repr__(self):
        return f"<UserTier(id={self.id}, name={self.name})>"

class Order(BaseUUIDModel):
    """订单表"""
    __tablename__ = "orders"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID"
    )
    
    tier_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("user_tiers.id"),
        nullable=True,
        comment="等级ID"
    )
    
    order_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="订单类型"
    )
    
    amount: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
        comment="订单金额"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        default="CNY",
        nullable=False,
        comment="货币类型"
    )
    
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        comment="订单状态"
    )
    
    payment_method: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="支付方式"
    )
    
    payment_provider: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="支付提供商"
    )
    
    payment_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="支付ID"
    )
    
    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="支付时间"
    )
    
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="订单过期时间"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="订单描述"
    )
    
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="订单元数据"
    )
    
    # 关联关系
    user = relationship("User", back_populates="orders")
    tier = relationship("UserTier", back_populates="orders")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index("idx_orders_user_status", "user_id", "status", "created_at"),
        Index("idx_orders_status", "status"),
        Index("idx_orders_payment_id", "payment_id"),
        Index("idx_orders_expires", "expires_at"),
    )
    
    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, status={self.status})>"

class Payment(BaseUUIDModel):
    """支付记录表"""
    __tablename__ = "payments"
    
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        comment="订单ID"
    )
    
    amount: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
        comment="支付金额"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        comment="货币类型"
    )
    
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="支付提供商"
    )
    
    provider_transaction_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="提供商交易ID"
    )
    
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        comment="支付状态"
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="完成时间"
    )
    
    failure_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="失败原因"
    )
    
    provider_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="提供商数据"
    )
    
    # 关联关系
    order = relationship("Order", back_populates="payments")
    
    # 索引
    __table_args__ = (
        Index("idx_payments_order_id", "order_id"),
        Index("idx_payments_status", "status"),
        Index("idx_payments_provider_tx_id", "provider_transaction_id"),
        Index("idx_payments_completed", "completed_at"),
    )
    
    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, status={self.status})>"