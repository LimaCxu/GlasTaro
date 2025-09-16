# -*- coding: utf-8 -*-
"""
数据库配置和连接管理
简单实用的数据库连接封装

作者: Lima
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from loguru import logger

class DatabaseConfig:
    """数据库配置类 - 从环境变量读取配置"""
    
    def __init__(self):
        # 从环境变量读取，没有默认的硬编码值
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        if not self.DATABASE_URL:
            raise ValueError("必须设置DATABASE_URL环境变量")
            
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        # 连接池配置 - 简单够用就行
        self.POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
        self.MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

class Base(DeclarativeBase):
    """
    SQLAlchemy基类
    设置了规范的命名约定，避免索引名冲突
    """
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

# 创建数据库引擎 - 异步的，性能更好
engine = create_async_engine(
    db_config.DATABASE_URL,
    pool_size=db_config.POOL_SIZE,
    max_overflow=db_config.MAX_OVERFLOW,
    pool_timeout=db_config.POOL_TIMEOUT,
    pool_recycle=db_config.POOL_RECYCLE,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",  # 开发时可以看SQL
    future=True
)

# 会话工厂 - 用于创建数据库会话
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False  # 提交后对象不过期
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数
    FastAPI会自动管理会话的生命周期
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库操作出错: {e}")
            raise
        finally:
            await session.close()

async def init_database():
    """初始化数据库 - 创建所有表"""
    try:
        async with engine.begin() as conn:
            # 运行所有的建表语句
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ 数据库表创建完成")
    except Exception as e:
        logger.error(f"💥 数据库初始化失败: {e}")
        raise

async def close_database():
    """关闭数据库连接池"""
    await engine.dispose()
    logger.info("📴 数据库连接已关闭")