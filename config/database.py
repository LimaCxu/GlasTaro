# -*- coding: utf-8 -*-
"""
数据库配置和连接管理
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from loguru import logger

# 数据库配置
class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            "postgresql+asyncpg://tarot_user:tarot_pass@localhost:5432/tarot_bot"
        )
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # 数据库连接池配置
        self.POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
        self.MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        
        # 连接重试配置
        self.MAX_RETRIES = int(os.getenv("DB_MAX_RETRIES", "3"))
        self.RETRY_DELAY = int(os.getenv("DB_RETRY_DELAY", "1"))

# 数据库基类
class Base(DeclarativeBase):
    """SQLAlchemy 基类"""
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )

# 全局配置实例
db_config = DatabaseConfig()

# 创建异步引擎
engine = create_async_engine(
    db_config.DATABASE_URL,
    pool_size=db_config.POOL_SIZE,
    max_overflow=db_config.MAX_OVERFLOW,
    pool_timeout=db_config.POOL_TIMEOUT,
    pool_recycle=db_config.POOL_RECYCLE,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    future=True
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库会话错误: {e}")
            raise
        finally:
            await session.close()

async def init_database():
    """初始化数据库"""
    try:
        async with engine.begin() as conn:
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

async def close_database():
    """关闭数据库连接"""
    await engine.dispose()
    logger.info("数据库连接已关闭")