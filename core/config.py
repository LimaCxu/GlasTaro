# -*- coding: utf-8 -*-
"""
应用配置模块
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator
from functools import lru_cache

class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "塔罗占卜机器人"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/tarot_bot"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_RETRY_ON_TIMEOUT: bool = True
    REDIS_SOCKET_KEEPALIVE: bool = True
    
    # Telegram配置
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    TELEGRAM_WEBHOOK_SECRET: Optional[str] = None
    
    # AI配置
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 1000
    OPENAI_TEMPERATURE: float = 0.7
    
    # 支付配置
    STRIPE_PUBLIC_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # 速率限制
    ENABLE_RATE_LIMIT: bool = True
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW: int = 60  # 秒
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000
    RATE_LIMIT_REQUESTS_PER_DAY: int = 10000
    
    # 占卜配置
    FREE_READINGS_PER_DAY: int = 3
    PREMIUM_READINGS_PER_DAY: int = 20
    DAILY_CARD_CACHE_HOURS: int = 24
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_REQUEST_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif"]
    UPLOAD_DIR: str = "uploads"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    
    # 监控配置
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # 地理位置限制
    ENABLE_GEO_RESTRICTION: bool = False
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = ["*"]
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # 缓存配置
    CACHE_TTL_USER: int = 3600  # 1小时
    CACHE_TTL_SESSION: int = 86400  # 24小时
    CACHE_TTL_DAILY_CARD: int = 86400  # 24小时
    CACHE_TTL_SYSTEM_CONFIG: int = 3600  # 1小时
    
    # 邮件配置
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    EMAIL_FROM: Optional[str] = None
    
    # 定时任务配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # 备份配置
    BACKUP_ENABLED: bool = False
    BACKUP_INTERVAL_HOURS: int = 24
    BACKUP_RETENTION_DAYS: int = 30
    BACKUP_S3_BUCKET: Optional[str] = None
    BACKUP_S3_ACCESS_KEY: Optional[str] = None
    BACKUP_S3_SECRET_KEY: Optional[str] = None
    
    # 多语言配置
    DEFAULT_LANGUAGE: str = "zh"
    SUPPORTED_LANGUAGES: List[str] = ["zh", "en", "ru", "ja", "ko"]
    
    # 管理员配置
    ADMIN_EMAIL: Optional[str] = None
    ADMIN_PASSWORD: Optional[str] = None
    
    # 维护模式
    MAINTENANCE_MODE: bool = False
    MAINTENANCE_MESSAGE: str = "系统正在维护中，请稍后再试"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v or not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL必须是有效的PostgreSQL连接字符串")
        return v
    
    @validator("REDIS_URL")
    def validate_redis_url(cls, v):
        if not v or not v.startswith("redis://"):
            raise ValueError("REDIS_URL必须是有效的Redis连接字符串")
        return v
    
    @validator("TELEGRAM_BOT_TOKEN")
    def validate_telegram_token(cls, v):
        if not v:
            raise ValueError("TELEGRAM_BOT_TOKEN不能为空")
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY长度至少32位")
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def validate_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def validate_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @validator("SUPPORTED_LANGUAGES", pre=True)
    def validate_supported_languages(cls, v):
        if isinstance(v, str):
            return [lang.strip() for lang in v.split(",") if lang.strip()]
        return v
    
    @validator("ALLOWED_FILE_TYPES", pre=True)
    def validate_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [file_type.strip() for file_type in v.split(",") if file_type.strip()]
        return v
    
    def get_database_config(self) -> dict:
        """获取数据库配置"""
        return {
            "url": self.DATABASE_URL,
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
            "pool_timeout": self.DATABASE_POOL_TIMEOUT,
            "pool_recycle": self.DATABASE_POOL_RECYCLE
        }
    
    def get_redis_config(self) -> dict:
        """获取Redis配置"""
        return {
            "url": self.REDIS_URL,
            "password": self.REDIS_PASSWORD,
            "max_connections": self.REDIS_MAX_CONNECTIONS,
            "retry_on_timeout": self.REDIS_RETRY_ON_TIMEOUT,
            "socket_keepalive": self.REDIS_SOCKET_KEEPALIVE
        }
    
    def get_rate_limit_config(self) -> dict:
        """获取速率限制配置"""
        return {
            "enabled": self.ENABLE_RATE_LIMIT,
            "requests": self.RATE_LIMIT_REQUESTS,
            "window": self.RATE_LIMIT_WINDOW,
            "requests_per_minute": self.RATE_LIMIT_REQUESTS_PER_MINUTE,
            "requests_per_hour": self.RATE_LIMIT_REQUESTS_PER_HOUR,
            "requests_per_day": self.RATE_LIMIT_REQUESTS_PER_DAY
        }
    
    def get_cache_config(self) -> dict:
        """获取缓存配置"""
        return {
            "user_ttl": self.CACHE_TTL_USER,
            "session_ttl": self.CACHE_TTL_SESSION,
            "daily_card_ttl": self.CACHE_TTL_DAILY_CARD,
            "system_config_ttl": self.CACHE_TTL_SYSTEM_CONFIG
        }
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return not self.DEBUG
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.DEBUG

@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()

# 全局配置实例
settings = get_settings()

# 环境变量检查
def check_required_env_vars():
    """检查必需的环境变量"""
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "DATABASE_URL",
        "REDIS_URL",
        "SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"缺少必需的环境变量: {', '.join(missing_vars)}")

# 配置验证
def validate_config():
    """验证配置"""
    try:
        # 检查必需的环境变量
        check_required_env_vars()
        
        # 验证配置实例
        settings = get_settings()
        
        # 额外的配置验证
        if settings.is_production():
            if settings.SECRET_KEY == "your-secret-key-here":
                raise ValueError("生产环境必须设置安全的SECRET_KEY")
            
            if "*" in settings.ALLOWED_HOSTS:
                raise ValueError("生产环境不应该允许所有主机")
        
        return True
        
    except Exception as e:
        print(f"配置验证失败: {e}")
        return False

if __name__ == "__main__":
    # 配置测试
    if validate_config():
        print("配置验证通过")
        print(f"应用名称: {settings.APP_NAME}")
        print(f"版本: {settings.VERSION}")
        print(f"调试模式: {settings.DEBUG}")
        print(f"主机: {settings.HOST}:{settings.PORT}")
    else:
        print("配置验证失败")