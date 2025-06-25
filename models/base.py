# -*- coding: utf-8 -*-
"""
数据库基础模型
"""

import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    """SQLAlchemy 基类"""
    pass

class TimestampMixin:
    """时间戳混入类"""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )

class UUIDMixin:
    """UUID 主键混入类"""
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="主键ID"
    )

class SoftDeleteMixin:
    """软删除混入类"""
    
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="是否已删除"
    )
    
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="删除时间"
    )

class BaseModel(Base, TimestampMixin):
    """基础模型类"""
    __abstract__ = True

class BaseUUIDModel(Base, UUIDMixin, TimestampMixin):
    """带UUID主键的基础模型类"""
    __abstract__ = True

class BaseSoftDeleteModel(Base, TimestampMixin, SoftDeleteMixin):
    """支持软删除的基础模型类"""
    __abstract__ = True