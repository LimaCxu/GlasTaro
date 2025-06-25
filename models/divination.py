# -*- coding: utf-8 -*-
"""
占卜相关数据库模型
"""

import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    BigInteger, String, Boolean, DateTime, Date, Integer, 
    Text, JSON, ForeignKey, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel, BaseUUIDModel

class DivinationSession(BaseUUIDModel):
    """占卜会话表"""
    __tablename__ = "divination_sessions"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID"
    )
    
    session_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="会话类型"
    )
    
    spread_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="牌阵类型"
    )
    
    question: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="用户问题"
    )
    
    cards_drawn: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="抽取的卡牌"
    )
    
    interpretation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="解读结果"
    )
    
    ai_model: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="使用的AI模型"
    )
    
    is_premium_reading: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否为付费占卜"
    )
    
    reading_duration: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="占卜时长(秒)"
    )
    
    user_rating: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="用户评分(1-5)"
    )
    
    user_feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="用户反馈"
    )
    
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        comment="会话状态"
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="完成时间"
    )
    
    # 关联关系
    user = relationship("User", back_populates="divination_sessions")
    
    # 约束和索引
    __table_args__ = (
        CheckConstraint(
            "user_rating >= 1 AND user_rating <= 5",
            name="ck_divination_sessions_rating_range"
        ),
        Index("idx_divination_user_date", "user_id", "created_at"),
        Index("idx_divination_session_type", "session_type"),
        Index("idx_divination_spread_type", "spread_type"),
        Index("idx_divination_status", "status"),
        Index("idx_divination_premium", "is_premium_reading"),
        Index("idx_divination_completed", "completed_at"),
    )
    
    def __repr__(self):
        return f"<DivinationSession(id={self.id}, user_id={self.user_id}, spread_type={self.spread_type})>"

class DailyCard(BaseModel):
    """每日塔罗牌表"""
    __tablename__ = "daily_cards"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
        comment="用户ID"
    )
    
    card_date: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
        comment="卡牌日期"
    )
    
    card_data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="卡牌数据"
    )
    
    interpretation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="卡牌解读"
    )
    
    is_viewed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否已查看"
    )
    
    viewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="查看时间"
    )
    
    user_reaction: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="用户反应"
    )
    
    # 关联关系
    user = relationship("User", back_populates="daily_cards")
    
    # 索引
    __table_args__ = (
        Index("idx_daily_cards_date", "card_date"),
        Index("idx_daily_cards_user_date", "user_id", "card_date"),
        Index("idx_daily_cards_viewed", "is_viewed"),
    )
    
    def __repr__(self):
        return f"<DailyCard(user_id={self.user_id}, date={self.card_date})>"

class TarotCard(BaseModel):
    """塔罗牌基础信息表"""
    __tablename__ = "tarot_cards"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="卡牌ID"
    )
    
    name_en: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment="英文名称"
    )
    
    name_zh: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="中文名称"
    )
    
    name_ru: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="俄文名称"
    )
    
    card_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="卡牌类型"
    )
    
    suit: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="花色"
    )
    
    number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="数字"
    )
    
    keywords: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="关键词"
    )
    
    meanings: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="含义解释"
    )
    
    reversed_meanings: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="逆位含义"
    )
    
    image_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="图片URL"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )
    
    # 索引
    __table_args__ = (
        Index("idx_tarot_cards_type", "card_type"),
        Index("idx_tarot_cards_suit", "suit"),
        Index("idx_tarot_cards_active", "is_active"),
    )
    
    def __repr__(self):
        return f"<TarotCard(id={self.id}, name_en={self.name_en})>"

class SpreadTemplate(BaseModel):
    """牌阵模板表"""
    __tablename__ = "spread_templates"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="模板ID"
    )
    
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment="牌阵名称"
    )
    
    display_names: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="多语言显示名称"
    )
    
    description: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="牌阵描述"
    )
    
    card_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="卡牌数量"
    )
    
    positions: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="位置配置"
    )
    
    is_premium: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否为付费牌阵"
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
    
    # 索引
    __table_args__ = (
        Index("idx_spread_templates_premium", "is_premium"),
        Index("idx_spread_templates_active", "is_active"),
        Index("idx_spread_templates_sort", "sort_order"),
    )
    
    def __repr__(self):
        return f"<SpreadTemplate(id={self.id}, name={self.name})>"