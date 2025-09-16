# -*- coding: utf-8 -*-
"""
Глас Таро 配置文件
这里放所有的配置项，我喜欢集中管理

作者: Lima
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator
from functools import lru_cache

class Settings(BaseSettings):
    """
    应用配置类
    从环境变量读取配置，有默认值
    """
    
    # 基本信息
    APP_NAME: str = "Глас Таро"
    VERSION: str = "1.0.0"
    DEBUG: bool = False  # 生产环境记得设为False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4  # 生产环境的进程数
    
    # 安全相关 - 生产环境一定要改SECRET_KEY
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 数据库连接 - 从环境变量读取
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/tarot_bot"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    
    # Redis缓存配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_RETRY_ON_TIMEOUT: bool = True
    REDIS_SOCKET_KEEPALIVE: bool = True
    
    # Telegram机器人配置
    TELEGRAM_BOT_TOKEN: str = ""  # 必须设置
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    TELEGRAM_WEBHOOK_SECRET: Optional[str] = None
    
    # AI模型配置 - 支持OpenAI和DeepSeek
    AI_MODEL: str = "gpt-3.5-turbo"  # 可选: gpt-3.5-turbo, gpt-4, deepseek-chat
    
    # OpenAI配置
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 1000
    OPENAI_TEMPERATURE: float = 0.7
    
    # DeepSeek配置（更便宜的选择）
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_MAX_TOKENS: int = 1000
    DEEPSEEK_TEMPERATURE: float = 0.7
    
    # 支付功能（暂时不用，以后可能会加）
    STRIPE_PUBLIC_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # 防刷配置 - 简单有效
    ENABLE_RATE_LIMIT: bool = True
    RATE_LIMIT_REQUESTS: int = 60  # 每分钟60次请求
    RATE_LIMIT_WINDOW: int = 60    # 时间窗口60秒
    
    # 占卜业务配置
    FREE_READINGS_PER_DAY: int = 3   # 免费用户每天3次
    PREMIUM_READINGS_PER_DAY: int = 20  # 付费用户每天20次
    DAILY_CARD_CACHE_HOURS: int = 24    # 每日卡牌缓存24小时
    
    # 文件上传限制（主要是用户头像）
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB够用了
    MAX_REQUEST_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif"]
    UPLOAD_DIR: str = "uploads"
    
    # 日志配置 - 简单明了
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    LOG_FILE: Optional[str] = None
    
    # 监控开关
    ENABLE_METRICS: bool = True
    
    # 地理限制（暂时不需要）
    ENABLE_GEO_RESTRICTION: bool = False
    
    # CORS配置 - 开发时宽松，生产环境要严格
    ALLOWED_HOSTS: List[str] = ["*"]  # TODO: 生产环境改为具体域名
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # 缓存时间配置（秒）
    CACHE_TTL_USER: int = 3600      # 用户信息缓存1小时
    CACHE_TTL_SESSION: int = 86400  # 会话缓存24小时
    CACHE_TTL_DAILY_CARD: int = 86400  # 每日卡牌缓存24小时
    
    # 多语言支持 - 这是核心功能
    DEFAULT_LANGUAGE: str = "zh"
    SUPPORTED_LANGUAGES: List[str] = ["zh", "en", "ru"]  # 先支持这几种
    
    # 管理员配置（简单版）
    ADMIN_EMAIL: Optional[str] = None
    ADMIN_PASSWORD: Optional[str] = None
    
    # 维护模式开关
    MAINTENANCE_MODE: bool = False
    MAINTENANCE_MESSAGE: str = "系统维护中，请稍后再试 🔧"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    # 简单的配置验证 - 只验证关键项目
    @validator("DATABASE_URL")
    def check_database_url(cls, v):
        if not v or not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("数据库URL格式不对，需要PostgreSQL连接字符串")
        return v
    
    @validator("REDIS_URL")
    def check_redis_url(cls, v):
        if not v or not v.startswith("redis://"):
            raise ValueError("Redis URL格式不对")
        return v
    
    @validator("TELEGRAM_BOT_TOKEN")
    def check_bot_token(cls, v):
        if not v:
            raise ValueError("必须设置Telegram Bot Token")
        return v
    
    @validator("SECRET_KEY")
    def check_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY太短，至少32位")
        return v
    
    # 处理逗号分隔的配置项
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v
    
    @validator("SUPPORTED_LANGUAGES", pre=True)
    def parse_languages(cls, v):
        if isinstance(v, str):
            return [lang.strip() for lang in v.split(",") if lang.strip()]
        return v
    
    # 一些实用的方法
    def is_debug(self) -> bool:
        """是否为调试模式"""
        return self.DEBUG
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return not self.DEBUG

@lru_cache()
def get_settings() -> Settings:
    """获取配置实例 - 单例模式，避免重复创建"""
    return Settings()

# 全局配置实例，方便其他地方导入使用
settings = get_settings()

def check_config():
    """检查配置是否正确"""
    try:
        # 基本检查
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("必须设置TELEGRAM_BOT_TOKEN")
        
        # 生产环境额外检查
        if settings.is_production():
            if "your-secret-key" in settings.SECRET_KEY:
                raise ValueError("生产环境必须修改默认SECRET_KEY")
            
            if "*" in settings.ALLOWED_HOSTS:
                print("⚠️  警告: 生产环境建议限制ALLOWED_HOSTS")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        return False

# 如果直接运行这个文件，就做配置检查
if __name__ == "__main__":
    if check_config():
        print("✅ 配置检查通过")
        print(f"📱 应用: {settings.APP_NAME} v{settings.VERSION}")
        print(f"🔧 模式: {'开发' if settings.is_debug() else '生产'}")
        print(f"🌐 地址: {settings.HOST}:{settings.PORT}")
    else:
        print("💥 配置有问题，请检查")