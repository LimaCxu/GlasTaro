# -*- coding: utf-8 -*-
"""
缓存服务层
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from config.redis_config import RedisManager, CacheKeys

class CacheService:
    """缓存服务"""
    
    def __init__(self, redis: RedisManager):
        self.redis = redis
    
    # 用户相关缓存
    async def cache_user(self, user_id: int, user_data: Dict[str, Any], expire: int = 3600):
        """缓存用户信息"""
        key = CacheKeys.user(user_id)
        await self.redis.set(key, user_data, expire=expire)
    
    async def get_cached_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取缓存的用户信息"""
        key = CacheKeys.user(user_id)
        return await self.redis.get(key)
    
    async def invalidate_user_cache(self, user_id: int):
        """清除用户缓存"""
        key = CacheKeys.user(user_id)
        await self.redis.delete(key)
    
    # 会话相关缓存
    async def cache_session(
        self, 
        session_id: Union[str, uuid.UUID], 
        session_data: Dict[str, Any], 
        expire: int = 86400
    ):
        """缓存会话信息"""
        key = CacheKeys.session(str(session_id))
        await self.redis.set(key, session_data, expire=expire)
    
    async def get_cached_session(self, session_id: Union[str, uuid.UUID]) -> Optional[Dict[str, Any]]:
        """获取缓存的会话信息"""
        key = CacheKeys.session(str(session_id))
        return await self.redis.get(key)
    
    async def invalidate_session_cache(self, session_id: Union[str, uuid.UUID]):
        """清除会话缓存"""
        key = CacheKeys.session(str(session_id))
        await self.redis.delete(key)
    
    # 每日塔罗牌缓存
    async def cache_daily_card(
        self, 
        user_id: int, 
        date: datetime, 
        card_data: Dict[str, Any]
    ):
        """缓存每日塔罗牌"""
        key = CacheKeys.daily_card(user_id, date)
        # 缓存到当天结束
        expire_time = datetime.combine(date.date() + timedelta(days=1), datetime.min.time())
        expire_seconds = int((expire_time - datetime.utcnow()).total_seconds())
        await self.redis.set(key, card_data, expire=max(expire_seconds, 60))
    
    async def get_cached_daily_card(
        self, 
        user_id: int, 
        date: datetime
    ) -> Optional[Dict[str, Any]]:
        """获取缓存的每日塔罗牌"""
        key = CacheKeys.daily_card(user_id, date)
        return await self.redis.get(key)
    
    # 占卜结果缓存
    async def cache_divination_result(
        self, 
        session_id: Union[str, uuid.UUID], 
        result_data: Dict[str, Any], 
        expire: int = 3600
    ):
        """缓存占卜结果"""
        key = CacheKeys.divination_result(str(session_id))
        await self.redis.set(key, result_data, expire=expire)
    
    async def get_cached_divination_result(
        self, 
        session_id: Union[str, uuid.UUID]
    ) -> Optional[Dict[str, Any]]:
        """获取缓存的占卜结果"""
        key = CacheKeys.divination_result(str(session_id))
        return await self.redis.get(key)
    
    # 用户偏好缓存
    async def cache_user_preferences(
        self, 
        user_id: int, 
        preferences: Dict[str, Any], 
        expire: int = 7200
    ):
        """缓存用户偏好"""
        key = CacheKeys.user_preferences(user_id)
        await self.redis.set(key, preferences, expire=expire)
    
    async def get_cached_user_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取缓存的用户偏好"""
        key = CacheKeys.user_preferences(user_id)
        return await self.redis.get(key)
    
    async def invalidate_user_preferences_cache(self, user_id: int):
        """清除用户偏好缓存"""
        key = CacheKeys.user_preferences(user_id)
        await self.redis.delete(key)
    
    # 用户统计缓存
    async def cache_user_stats(
        self, 
        user_id: int, 
        stats: Dict[str, Any], 
        expire: int = 1800
    ):
        """缓存用户统计"""
        key = CacheKeys.user_stats(user_id)
        await self.redis.set(key, stats, expire=expire)
    
    async def get_cached_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取缓存的用户统计"""
        key = CacheKeys.user_stats(user_id)
        return await self.redis.get(key)
    
    async def invalidate_user_stats_cache(self, user_id: int):
        """清除用户统计缓存"""
        key = CacheKeys.user_stats(user_id)
        await self.redis.delete(key)
    
    # 系统配置缓存
    async def cache_system_config(
        self, 
        config_key: str, 
        config_value: Any, 
        expire: int = 3600
    ):
        """缓存系统配置"""
        key = CacheKeys.system_config(config_key)
        await self.redis.set(key, config_value, expire=expire)
    
    async def get_cached_system_config(self, config_key: str) -> Optional[Any]:
        """获取缓存的系统配置"""
        key = CacheKeys.system_config(config_key)
        return await self.redis.get(key)
    
    async def invalidate_system_config_cache(self, config_key: str):
        """清除系统配置缓存"""
        key = CacheKeys.system_config(config_key)
        await self.redis.delete(key)
    
    # 速率限制
    async def check_rate_limit(
        self, 
        user_id: int, 
        action: str, 
        limit: int, 
        window_seconds: int
    ) -> tuple[bool, int]:
        """检查速率限制
        
        Returns:
            tuple: (是否允许, 剩余次数)
        """
        key = CacheKeys.rate_limit(user_id, action)
        
        # 获取当前计数
        current_count = await self.redis.get(key)
        if current_count is None:
            current_count = 0
        else:
            current_count = int(current_count)
        
        if current_count >= limit:
            return False, 0
        
        # 增加计数
        new_count = await self.redis.incr(key)
        if new_count == 1:
            # 第一次设置，设置过期时间
            await self.redis.expire(key, window_seconds)
        
        remaining = max(0, limit - new_count)
        return True, remaining
    
    async def reset_rate_limit(self, user_id: int, action: str):
        """重置速率限制"""
        key = CacheKeys.rate_limit(user_id, action)
        await self.redis.delete(key)
    
    # 临时数据存储
    async def set_temp_data(
        self, 
        key: str, 
        data: Any, 
        expire: int = 300
    ):
        """设置临时数据"""
        temp_key = CacheKeys.temp_data(key)
        await self.redis.set(temp_key, data, expire=expire)
    
    async def get_temp_data(self, key: str) -> Optional[Any]:
        """获取临时数据"""
        temp_key = CacheKeys.temp_data(key)
        return await self.redis.get(temp_key)
    
    async def delete_temp_data(self, key: str):
        """删除临时数据"""
        temp_key = CacheKeys.temp_data(key)
        await self.redis.delete(temp_key)
    
    # 批量操作
    async def invalidate_user_all_cache(self, user_id: int):
        """清除用户所有相关缓存"""
        patterns = [
            CacheKeys.user(user_id),
            CacheKeys.user_preferences(user_id),
            CacheKeys.user_stats(user_id),
            f"user:{user_id}:daily_card:*",
            f"user:{user_id}:rate_limit:*"
        ]
        
        for pattern in patterns:
            if "*" in pattern:
                # 使用模式匹配删除
                keys = await self.redis.keys(pattern)
                if keys:
                    await self.redis.delete(*keys)
            else:
                await self.redis.delete(pattern)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        info = await self.redis.info()
        return {
            "connected_clients": info.get("connected_clients", 0),
            "used_memory": info.get("used_memory_human", "0B"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "total_commands_processed": info.get("total_commands_processed", 0)
        }
    
    async def clear_expired_keys(self):
        """清理过期键（Redis会自动处理，这里主要用于统计）"""
        # Redis会自动清理过期键，这个方法主要用于手动触发清理或统计
        pass
    
    # 分布式锁
    async def acquire_lock(
        self, 
        lock_key: str, 
        expire: int = 30, 
        timeout: int = 10
    ) -> bool:
        """获取分布式锁"""
        import asyncio
        import time
        
        lock_value = str(uuid.uuid4())
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            # 尝试获取锁
            result = await self.redis.set(
                f"lock:{lock_key}", 
                lock_value, 
                expire=expire, 
                nx=True  # 只在键不存在时设置
            )
            
            if result:
                return True
            
            # 等待一小段时间后重试
            await asyncio.sleep(0.1)
        
        return False
    
    async def release_lock(self, lock_key: str, lock_value: str) -> bool:
        """释放分布式锁"""
        # 使用Lua脚本确保原子性
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        result = await self.redis.eval(
            lua_script, 
            1, 
            f"lock:{lock_key}", 
            lock_value
        )
        
        return bool(result)