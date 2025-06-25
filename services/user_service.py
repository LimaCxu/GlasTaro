# -*- coding: utf-8 -*-
"""
用户服务层
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload

from models.user import User, UserSession, UserPreference, UserUsageStats
from models.admin import UserFeedback
from config.redis_config import RedisManager, CacheKeys
from utils.security import hash_password, verify_password
from utils.exceptions import UserNotFoundError, InvalidCredentialsError

class UserService:
    """用户服务"""
    
    def __init__(self, db: AsyncSession, redis: RedisManager):
        self.db = db
        self.redis = redis
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据用户ID获取用户"""
        # 先从缓存获取
        cache_key = CacheKeys.user(user_id)
        cached_user = await self.redis.get(cache_key)
        if cached_user:
            return User(**cached_user)
        
        # 从数据库获取
        stmt = select(User).where(User.user_id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            # 缓存用户信息
            user_data = {
                "user_id": user.user_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language_code": user.language_code,
                "is_premium": user.is_premium,
                "status": user.status,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_active": user.last_active.isoformat() if user.last_active else None
            }
            await self.redis.set(cache_key, user_data, expire=3600)  # 缓存1小时
        
        return user
    
    async def create_or_update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: Optional[str] = None
    ) -> User:
        """创建或更新用户"""
        # 检查用户是否存在
        existing_user = await self.get_user_by_id(user_id)
        
        if existing_user:
            # 更新用户信息
            update_data = {
                "last_active": datetime.utcnow()
            }
            if username is not None:
                update_data["username"] = username
            if first_name is not None:
                update_data["first_name"] = first_name
            if last_name is not None:
                update_data["last_name"] = last_name
            if language_code is not None:
                update_data["language_code"] = language_code
            
            stmt = (
                update(User)
                .where(User.user_id == user_id)
                .values(**update_data)
            )
            await self.db.execute(stmt)
            await self.db.commit()
            
            # 清除缓存
            await self.redis.delete(CacheKeys.user(user_id))
            
            return await self.get_user_by_id(user_id)
        else:
            # 创建新用户
            user = User(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code or "zh",
                status="active",
                created_at=datetime.utcnow(),
                last_active=datetime.utcnow()
            )
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            # 创建用户偏好设置
            preference = UserPreference(
                user_id=user_id,
                language=language_code or "zh",
                timezone="UTC",
                notification_enabled=True
            )
            self.db.add(preference)
            
            # 创建用户使用统计
            stats = UserUsageStats(
                user_id=user_id,
                free_readings_used=0,
                premium_readings_used=0,
                total_usage_time=0
            )
            self.db.add(stats)
            
            await self.db.commit()
            
            return user
    
    async def get_user_session(
        self,
        user_id: int,
        session_type: str = "telegram"
    ) -> Optional[UserSession]:
        """获取用户会话"""
        stmt = (
            select(UserSession)
            .where(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.session_type == session_type,
                    UserSession.expires_at > datetime.utcnow()
                )
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_user_session(
        self,
        user_id: int,
        session_type: str = "telegram",
        session_data: Optional[Dict[str, Any]] = None,
        expires_in_hours: int = 24
    ) -> UserSession:
        """创建用户会话"""
        # 删除旧会话
        await self.cleanup_expired_sessions(user_id)
        
        session = UserSession(
            user_id=user_id,
            session_type=session_type,
            session_data=session_data or {},
            status="active",
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours)
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def update_user_session(
        self,
        session_id: uuid.UUID,
        session_data: Dict[str, Any],
        extend_expiry: bool = True
    ) -> Optional[UserSession]:
        """更新用户会话"""
        update_data = {
            "session_data": session_data,
            "updated_at": datetime.utcnow()
        }
        
        if extend_expiry:
            update_data["expires_at"] = datetime.utcnow() + timedelta(hours=24)
        
        stmt = (
            update(UserSession)
            .where(UserSession.id == session_id)
            .values(**update_data)
        )
        
        await self.db.execute(stmt)
        await self.db.commit()
        
        # 返回更新后的会话
        stmt = select(UserSession).where(UserSession.id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def cleanup_expired_sessions(self, user_id: Optional[int] = None):
        """清理过期会话"""
        conditions = [UserSession.expires_at <= datetime.utcnow()]
        if user_id:
            conditions.append(UserSession.user_id == user_id)
        
        stmt = delete(UserSession).where(and_(*conditions))
        await self.db.execute(stmt)
        await self.db.commit()
    
    async def get_user_preferences(self, user_id: int) -> Optional[UserPreference]:
        """获取用户偏好设置"""
        stmt = select(UserPreference).where(UserPreference.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_user_preferences(
        self,
        user_id: int,
        **preferences
    ) -> UserPreference:
        """更新用户偏好设置"""
        existing_pref = await self.get_user_preferences(user_id)
        
        if existing_pref:
            # 更新现有偏好
            update_data = {k: v for k, v in preferences.items() if hasattr(UserPreference, k)}
            update_data["updated_at"] = datetime.utcnow()
            
            stmt = (
                update(UserPreference)
                .where(UserPreference.user_id == user_id)
                .values(**update_data)
            )
            await self.db.execute(stmt)
            await self.db.commit()
            
            return await self.get_user_preferences(user_id)
        else:
            # 创建新偏好
            preference = UserPreference(
                user_id=user_id,
                **preferences
            )
            self.db.add(preference)
            await self.db.commit()
            await self.db.refresh(preference)
            return preference
    
    async def get_user_stats(self, user_id: int) -> Optional[UserUsageStats]:
        """获取用户使用统计"""
        stmt = select(UserUsageStats).where(UserUsageStats.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_user_stats(
        self,
        user_id: int,
        free_readings_increment: int = 0,
        premium_readings_increment: int = 0,
        usage_time_increment: int = 0
    ) -> UserUsageStats:
        """更新用户使用统计"""
        existing_stats = await self.get_user_stats(user_id)
        
        if existing_stats:
            # 更新现有统计
            update_data = {
                "free_readings_used": UserUsageStats.free_readings_used + free_readings_increment,
                "premium_readings_used": UserUsageStats.premium_readings_used + premium_readings_increment,
                "total_usage_time": UserUsageStats.total_usage_time + usage_time_increment,
                "updated_at": datetime.utcnow()
            }
            
            stmt = (
                update(UserUsageStats)
                .where(UserUsageStats.user_id == user_id)
                .values(**update_data)
            )
            await self.db.execute(stmt)
            await self.db.commit()
            
            return await self.get_user_stats(user_id)
        else:
            # 创建新统计
            stats = UserUsageStats(
                user_id=user_id,
                free_readings_used=max(0, free_readings_increment),
                premium_readings_used=max(0, premium_readings_increment),
                total_usage_time=max(0, usage_time_increment)
            )
            self.db.add(stats)
            await self.db.commit()
            await self.db.refresh(stats)
            return stats
    
    async def create_user_feedback(
        self,
        user_id: int,
        session_id: Optional[uuid.UUID] = None,
        rating: Optional[int] = None,
        feedback_text: Optional[str] = None,
        feedback_type: str = "general"
    ) -> UserFeedback:
        """创建用户反馈"""
        feedback = UserFeedback(
            user_id=user_id,
            session_id=session_id,
            rating=rating,
            feedback_text=feedback_text,
            feedback_type=feedback_type,
            status="pending"
        )
        
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        
        return feedback
    
    async def get_user_feedback_list(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> List[UserFeedback]:
        """获取用户反馈列表"""
        stmt = (
            select(UserFeedback)
            .where(UserFeedback.user_id == user_id)
            .order_by(UserFeedback.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def deactivate_user(self, user_id: int) -> bool:
        """停用用户"""
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(status="inactive", updated_at=datetime.utcnow())
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        # 清除缓存
        await self.redis.delete(CacheKeys.user(user_id))
        
        return result.rowcount > 0
    
    async def get_active_users_count(self, days: int = 30) -> int:
        """获取活跃用户数量"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        stmt = (
            select(func.count(User.user_id))
            .where(
                and_(
                    User.status == "active",
                    User.last_active >= since_date
                )
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def search_users(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[User]:
        """搜索用户"""
        search_pattern = f"%{query}%"
        
        stmt = (
            select(User)
            .where(
                or_(
                    User.username.ilike(search_pattern),
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern)
                )
            )
            .order_by(User.last_active.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()