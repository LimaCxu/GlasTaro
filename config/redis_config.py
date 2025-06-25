# -*- coding: utf-8 -*-
"""
Redis 配置和连接管理
"""

import os
import json
from typing import Optional, Any, Union
import aioredis
from loguru import logger

class RedisConfig:
    """Redis 配置类"""
    
    def __init__(self):
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.REDIS_DB = int(os.getenv("REDIS_DB", "0"))
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        self.REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))
        self.REDIS_RETRY_ON_TIMEOUT = os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() == "true"
        self.REDIS_SOCKET_KEEPALIVE = os.getenv("REDIS_SOCKET_KEEPALIVE", "true").lower() == "true"
        self.REDIS_SOCKET_KEEPALIVE_OPTIONS = {}
        
        # 如果 URL 中没有密码但环境变量中有密码，则构建带密码的 URL
        if self.REDIS_PASSWORD and "@" not in self.REDIS_URL:
            # 解析 URL 并添加密码
            if self.REDIS_URL.startswith("redis://"):
                self.REDIS_URL = f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_URL[8:]}"
            elif self.REDIS_URL.startswith("rediss://"):
                self.REDIS_URL = f"rediss://:{self.REDIS_PASSWORD}@{self.REDIS_URL[9:]}"
        
        # 缓存过期时间配置（秒）
        self.SESSION_EXPIRE = int(os.getenv("SESSION_EXPIRE", "1800"))  # 30分钟
        self.RATE_LIMIT_EXPIRE = int(os.getenv("RATE_LIMIT_EXPIRE", "3600"))  # 1小时
        self.DAILY_CARD_EXPIRE = int(os.getenv("DAILY_CARD_EXPIRE", "86400"))  # 24小时
        self.USER_PREFERENCE_EXPIRE = int(os.getenv("USER_PREFERENCE_EXPIRE", "604800"))  # 7天

class RedisManager:
    """Redis 连接管理器"""
    
    def __init__(self, config: Optional[RedisConfig] = None):
        self.config = config or RedisConfig()
        self.redis: Optional[aioredis.Redis] = None
        
    async def connect(self):
        """连接到 Redis"""
        try:
            # 如果 URL 中已经包含密码，则不再单独传递 password 参数
            connection_params = {
                "db": self.config.REDIS_DB,
                "max_connections": self.config.REDIS_MAX_CONNECTIONS,
                "retry_on_timeout": self.config.REDIS_RETRY_ON_TIMEOUT,
                "socket_keepalive": self.config.REDIS_SOCKET_KEEPALIVE,
                "socket_keepalive_options": self.config.REDIS_SOCKET_KEEPALIVE_OPTIONS,
                "decode_responses": True
            }
            
            # 只有当 URL 中没有密码时才单独传递密码参数
            if "@" not in self.config.REDIS_URL and self.config.REDIS_PASSWORD:
                connection_params["password"] = self.config.REDIS_PASSWORD
            
            self.redis = aioredis.from_url(
                self.config.REDIS_URL,
                **connection_params
            )
            
            # 测试连接
            await self.redis.ping()
            logger.info(f"Redis 连接成功 - URL: {self.config.REDIS_URL.split('@')[-1] if '@' in self.config.REDIS_URL else self.config.REDIS_URL}")
        except Exception as e:
            logger.error(f"Redis 连接失败: {e}")
            raise
    
    async def disconnect(self):
        """断开 Redis 连接"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis 连接已关闭")
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置键值对"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            result = await self.redis.set(key, value, ex=expire)
            return result
        except Exception as e:
            logger.error(f"Redis SET 操作失败 {key}: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """获取值"""
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            
            # 尝试解析 JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis GET 操作失败 {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """删除键"""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE 操作失败 {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            result = await self.redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis EXISTS 操作失败 {key}: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """设置键的过期时间"""
        try:
            result = await self.redis.expire(key, seconds)
            return result
        except Exception as e:
            logger.error(f"Redis EXPIRE 操作失败 {key}: {e}")
            return False
    
    async def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """递增计数器"""
        try:
            result = await self.redis.incr(key, amount)
            return result
        except Exception as e:
            logger.error(f"Redis INCR 操作失败 {key}: {e}")
            return None
    
    async def decr(self, key: str, amount: int = 1) -> Optional[int]:
        """递减计数器"""
        try:
            result = await self.redis.decr(key, amount)
            return result
        except Exception as e:
            logger.error(f"Redis DECR 操作失败 {key}: {e}")
            return None
    
    async def hset(self, name: str, key: str, value: Any) -> bool:
        """设置哈希字段"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            result = await self.redis.hset(name, key, value)
            return result
        except Exception as e:
            logger.error(f"Redis HSET 操作失败 {name}.{key}: {e}")
            return False
    
    async def hget(self, name: str, key: str) -> Optional[Any]:
        """获取哈希字段值"""
        try:
            value = await self.redis.hget(name, key)
            if value is None:
                return None
            
            # 尝试解析 JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis HGET 操作失败 {name}.{key}: {e}")
            return None
    
    async def hdel(self, name: str, *keys: str) -> int:
        """删除哈希字段"""
        try:
            result = await self.redis.hdel(name, *keys)
            return result
        except Exception as e:
            logger.error(f"Redis HDEL 操作失败 {name}: {e}")
            return 0
    
    async def hgetall(self, name: str) -> dict:
        """获取所有哈希字段"""
        try:
            result = await self.redis.hgetall(name)
            # 尝试解析 JSON 值
            parsed_result = {}
            for key, value in result.items():
                try:
                    parsed_result[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    parsed_result[key] = value
            return parsed_result
        except Exception as e:
            logger.error(f"Redis HGETALL 操作失败 {name}: {e}")
            return {}

# 全局 Redis 配置和管理器
redis_config = RedisConfig()

# 创建全局Redis管理器实例
def create_redis_manager() -> RedisManager:
    """创建Redis管理器实例"""
    return RedisManager(redis_config)

# 便捷函数
async def get_redis() -> RedisManager:
    """获取 Redis 管理器实例"""
    return redis_manager

# 缓存键生成器
class CacheKeys:
    """缓存键生成器"""
    
    @staticmethod
    def user_session(user_id: int) -> str:
        """用户会话缓存键"""
        return f"session:user:{user_id}"
    
    @staticmethod
    def user_rate_limit(user_id: int) -> str:
        """用户频率限制缓存键"""
        return f"rate_limit:user:{user_id}"
    
    @staticmethod
    def user_daily_requests(user_id: int, date: str) -> str:
        """用户每日请求计数缓存键"""
        return f"daily_requests:user:{user_id}:{date}"
    
    @staticmethod
    def user_hourly_requests(user_id: int, hour: str) -> str:
        """用户每小时请求计数缓存键"""
        return f"hourly_requests:user:{user_id}:{hour}"
    
    @staticmethod
    def daily_card(user_id: int, date: str) -> str:
        """每日塔罗牌缓存键"""
        return f"daily_card:user:{user_id}:{date}"
    
    @staticmethod
    def user_preferences(user_id: int) -> str:
        """用户偏好设置缓存键"""
        return f"preferences:user:{user_id}"
    
    @staticmethod
    def user_language(user_id: int) -> str:
        """用户语言设置缓存键"""
        return f"language:user:{user_id}"
    
    @staticmethod
    def bot_stats() -> str:
        """机器人统计数据缓存键"""
        return "bot:stats"
    
    @staticmethod
    def system_config(key: str) -> str:
        """系统配置缓存键"""
        return f"system:config:{key}"