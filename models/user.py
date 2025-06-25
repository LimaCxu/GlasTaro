# -*- coding: utf-8 -*-
"""
用户相关数据库模型
"""

import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    BigInteger, String, Boolean, DateTime, Date, Integer, 
    Text, JSON, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel, BaseUUIDModel

class User(BaseModel):
    """用户表"""
    __tablename__ = "users"
    
    # 主键使用 Telegram 用户ID
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        comment="Telegram用户ID"
    )
    
    # 基本信息
    username: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="用户名"
    )
    
    first_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="名字"
    )
    
    last_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="姓氏"
    )
    
    language_code: Mapped[str] = mapped_column(
        String(10),
        default="zh",
        nullable=False,
        comment="语言代码"
    )
    
    # 联系信息
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="电话号码"
    )
    
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="邮箱地址"
    )
    
    avatar_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="头像URL"
    )
    
    # 状态信息
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )
    
    is_premium: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否为付费用户"
    )
    
    premium_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="付费到期时间"
    )
    
    # 时间信息
    registration_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        nullable=False,
        comment="注册时间"
    )
    
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后登录时间"
    )
    
    # 关联关系
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")
    usage_stats = relationship("UserUsageStats", back_populates="user", cascade="all, delete-orphan")
    divination_sessions = relationship("DivinationSession", back_populates="user")
    daily_cards = relationship("DailyCard", back_populates="user")
    orders = relationship("Order", back_populates="user")
    feedback = relationship("UserFeedback", back_populates="user")
    
    # 索引
    __table_args__ = (
        Index("idx_users_premium", "is_premium", "premium_expires_at"),
        Index("idx_users_active", "is_active"),
        Index("idx_users_language", "language_code"),
    )
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username})>"

class UserSession(BaseUUIDModel):
    """用户会话表"""
    __tablename__ = "user_sessions"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID"
    )
    
    current_state: Mapped[str] = mapped_column(
        String(50),
        default="idle",
        nullable=False,
        comment="当前状态"
    )
    
    waiting_for_question: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否等待问题输入"
    )
    
    spread_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="牌阵类型"
    )
    
    question: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="用户问题"
    )
    
    session_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="会话数据"
    )
    
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="会话过期时间"
    )
    
    # 关联关系
    user = relationship("User", back_populates="sessions")
    
    # 索引
    __table_args__ = (
        Index("idx_user_sessions_user_id", "user_id"),
        Index("idx_user_sessions_state", "current_state"),
        Index("idx_user_sessions_expires", "expires_at"),
    )
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, state={self.current_state})>"

class UserPreference(BaseModel):
    """用户偏好设置表"""
    __tablename__ = "user_preferences"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
        comment="用户ID"
    )
    
    preference_key: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        comment="偏好键"
    )
    
    preference_value: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="偏好值"
    )
    
    # 关联关系
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, key={self.preference_key})>"

class UserUsageStats(BaseModel):
    """用户使用统计表"""
    __tablename__ = "user_usage_stats"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
        comment="用户ID"
    )
    
    date: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
        comment="统计日期"
    )
    
    free_readings_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="免费占卜次数"
    )
    
    premium_readings_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="付费占卜次数"
    )
    
    total_time_spent: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="总使用时长(秒)"
    )
    
    # 关联关系
    user = relationship("User", back_populates="usage_stats")
    
    # 索引
    __table_args__ = (
        Index("idx_usage_stats_date", "date"),
        Index("idx_usage_stats_user_date", "user_id", "date"),
    )
    
    def __repr__(self):
        return f"<UserUsageStats(user_id={self.user_id}, date={self.date})>"