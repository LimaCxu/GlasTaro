# -*- coding: utf-8 -*-
"""
管理员和系统配置相关数据库模型
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger, String, Boolean, DateTime, Integer, 
    Text, JSON, ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel, BaseUUIDModel

class Admin(BaseModel):
    """管理员表"""
    __tablename__ = "admins"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="管理员ID"
    )
    
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment="用户名"
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="邮箱地址"
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码哈希"
    )
    
    role: Mapped[str] = mapped_column(
        String(50),
        default="admin",
        nullable=False,
        comment="角色"
    )
    
    permissions: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="权限配置"
    )
    
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后登录时间"
    )
    
    last_login_ip: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="最后登录IP"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )
    
    # 关联关系
    system_configs = relationship("SystemConfig", back_populates="updated_by_admin")
    feedback_responses = relationship("UserFeedback", back_populates="admin")
    
    # 索引
    __table_args__ = (
        Index("idx_admins_role", "role"),
        Index("idx_admins_active", "is_active"),
        Index("idx_admins_last_login", "last_login"),
    )
    
    def __repr__(self):
        return f"<Admin(id={self.id}, username={self.username}, role={self.role})>"

class SystemConfig(BaseModel):
    """系统配置表"""
    __tablename__ = "system_configs"
    
    key: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        comment="配置键"
    )
    
    value: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="配置值"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="配置描述"
    )
    
    category: Mapped[str] = mapped_column(
        String(50),
        default="general",
        nullable=False,
        comment="配置分类"
    )
    
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否公开"
    )
    
    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("admins.id"),
        nullable=True,
        comment="更新者ID"
    )
    
    # 关联关系
    updated_by_admin = relationship("Admin", back_populates="system_configs")
    
    # 索引
    __table_args__ = (
        Index("idx_system_configs_category", "category"),
        Index("idx_system_configs_public", "is_public"),
        Index("idx_system_configs_updated", "updated_at"),
    )
    
    def __repr__(self):
        return f"<SystemConfig(key={self.key}, category={self.category})>"

class UserFeedback(BaseUUIDModel):
    """用户反馈表"""
    __tablename__ = "user_feedback"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID"
    )
    
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("divination_sessions.id"),
        nullable=True,
        comment="占卜会话ID"
    )
    
    rating: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="评分(1-5)"
    )
    
    feedback_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="反馈内容"
    )
    
    feedback_type: Mapped[str] = mapped_column(
        String(50),
        default="general",
        nullable=False,
        comment="反馈类型"
    )
    
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        comment="处理状态"
    )
    
    admin_response: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="管理员回复"
    )
    
    admin_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("admins.id"),
        nullable=True,
        comment="处理管理员ID"
    )
    
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="解决时间"
    )
    
    priority: Mapped[str] = mapped_column(
        String(20),
        default="normal",
        nullable=False,
        comment="优先级"
    )
    
    tags: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        comment="标签"
    )
    
    # 关联关系
    user = relationship("User", back_populates="feedback")
    admin = relationship("Admin", back_populates="feedback_responses")
    
    # 约束和索引
    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="ck_user_feedback_rating_range"
        ),
        Index("idx_feedback_status", "status", "created_at"),
        Index("idx_feedback_type", "feedback_type"),
        Index("idx_feedback_user", "user_id"),
        Index("idx_feedback_priority", "priority"),
        Index("idx_feedback_resolved", "resolved_at"),
    )
    
    def __repr__(self):
        return f"<UserFeedback(id={self.id}, user_id={self.user_id}, type={self.feedback_type})>"

class AuditLog(BaseUUIDModel):
    """审计日志表"""
    __tablename__ = "audit_logs"
    
    admin_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("admins.id"),
        nullable=True,
        comment="操作管理员ID"
    )
    
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id"),
        nullable=True,
        comment="相关用户ID"
    )
    
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="操作类型"
    )
    
    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="资源类型"
    )
    
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="资源ID"
    )
    
    old_values: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="旧值"
    )
    
    new_values: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="新值"
    )
    
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="IP地址"
    )
    
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="用户代理"
    )
    
    # 索引
    __table_args__ = (
        Index("idx_audit_logs_admin", "admin_id", "created_at"),
        Index("idx_audit_logs_user", "user_id", "created_at"),
        Index("idx_audit_logs_action", "action"),
        Index("idx_audit_logs_resource", "resource_type", "resource_id"),
        Index("idx_audit_logs_created", "created_at"),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, resource_type={self.resource_type})>"

class SystemStats(BaseModel):
    """系统统计表"""
    __tablename__ = "system_stats"
    
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
        comment="统计日期"
    )
    
    total_users: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="总用户数"
    )
    
    active_users: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="活跃用户数"
    )
    
    premium_users: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="付费用户数"
    )
    
    total_readings: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="总占卜次数"
    )
    
    premium_readings: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="付费占卜次数"
    )
    
    total_revenue: Mapped[float] = mapped_column(
        String,  # 使用字符串存储避免精度问题
        default="0.00",
        nullable=False,
        comment="总收入"
    )
    
    new_registrations: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="新注册用户数"
    )
    
    # 索引
    __table_args__ = (
        Index("idx_system_stats_date", "date"),
    )
    
    def __repr__(self):
        return f"<SystemStats(date={self.date}, total_users={self.total_users})>"