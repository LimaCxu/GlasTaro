# -*- coding: utf-8 -*-
"""
管理员服务模块
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, text
from sqlalchemy.orm import selectinload

from models.admin import Admin, SystemConfig, UserFeedback, AuditLog, SystemStats
from models.user import User, UserUsageStats
from models.order import Order, Payment
from models.divination import DivinationSession
from config.redis_config import RedisManager, CacheKeys
from utils.exceptions import (
    ValidationError,
    ResourceNotFoundError,
    BusinessLogicError,
    PermissionDeniedError
)
from utils.security import hash_password, verify_password, generate_token
from utils.validators import validate_email, validate_password_strength
from utils.helpers import generate_short_id, get_current_timestamp

logger = logging.getLogger(__name__)

class AdminService:
    """管理员服务"""
    
    def __init__(self, db: AsyncSession, redis: RedisManager):
        self.db = db
        self.redis = redis
    
    # 管理员管理
    async def create_admin(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: str = "admin",
        permissions: List[str] = None,
        is_active: bool = True
    ) -> Admin:
        """创建管理员"""
        # 验证输入
        if not validate_email(email):
            raise ValidationError("邮箱格式无效")
        
        if not validate_password_strength(password):
            raise ValidationError("密码强度不足")
        
        if role not in ["super_admin", "admin", "moderator", "viewer"]:
            raise ValidationError("无效的角色")
        
        # 检查用户名和邮箱是否已存在
        existing_admin = await self.get_admin_by_username(username)
        if existing_admin:
            raise BusinessLogicError("用户名已存在")
        
        existing_admin = await self.get_admin_by_email(email)
        if existing_admin:
            raise BusinessLogicError("邮箱已存在")
        
        # 创建管理员
        admin = Admin(
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
            permissions=permissions or [],
            is_active=is_active
        )
        
        self.db.add(admin)
        await self.db.commit()
        await self.db.refresh(admin)
        
        # 记录审计日志
        await self.create_audit_log(
            admin_id=admin.id,
            action="create_admin",
            resource_type="admin",
            resource_id=admin.id,
            details={"username": username, "role": role}
        )
        
        logger.info(f"创建管理员: {username} (ID: {admin.id})")
        return admin
    
    async def get_admin_by_id(self, admin_id: int) -> Optional[Admin]:
        """根据ID获取管理员"""
        cache_key = CacheKeys.admin(admin_id)
        
        # 尝试从缓存获取
        cached_admin = await self.redis.get(cache_key)
        if cached_admin:
            return cached_admin
        
        # 从数据库查询
        result = await self.db.execute(
            select(Admin).where(Admin.id == admin_id)
        )
        admin = result.scalar_one_or_none()
        
        if admin:
            # 缓存结果
            await self.redis.set(cache_key, admin, expire=3600)
        
        return admin
    
    async def get_admin_by_username(self, username: str) -> Optional[Admin]:
        """根据用户名获取管理员"""
        result = await self.db.execute(
            select(Admin).where(Admin.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_admin_by_email(self, email: str) -> Optional[Admin]:
        """根据邮箱获取管理员"""
        result = await self.db.execute(
            select(Admin).where(Admin.email == email)
        )
        return result.scalar_one_or_none()
    
    async def authenticate_admin(self, username: str, password: str) -> Optional[Admin]:
        """管理员认证"""
        admin = await self.get_admin_by_username(username)
        if not admin:
            return None
        
        if not admin.is_active:
            raise BusinessLogicError("管理员账户已被禁用")
        
        if not verify_password(password, admin.password_hash):
            # 记录登录失败
            await self.create_audit_log(
                admin_id=admin.id,
                action="login_failed",
                resource_type="admin",
                resource_id=admin.id,
                details={"reason": "密码错误"}
            )
            return None
        
        # 更新最后登录时间
        admin.last_login_at = datetime.utcnow()
        await self.db.commit()
        
        # 记录登录成功
        await self.create_audit_log(
            admin_id=admin.id,
            action="login_success",
            resource_type="admin",
            resource_id=admin.id
        )
        
        return admin
    
    async def update_admin(
        self,
        admin_id: int,
        **updates
    ) -> Optional[Admin]:
        """更新管理员信息"""
        admin = await self.get_admin_by_id(admin_id)
        if not admin:
            raise ResourceNotFoundError("管理员不存在")
        
        # 验证更新数据
        if 'email' in updates:
            if not validate_email(updates['email']):
                raise ValidationError("邮箱格式无效")
            
            # 检查邮箱是否已被其他管理员使用
            existing_admin = await self.get_admin_by_email(updates['email'])
            if existing_admin and existing_admin.id != admin_id:
                raise BusinessLogicError("邮箱已被使用")
        
        if 'password' in updates:
            if not validate_password_strength(updates['password']):
                raise ValidationError("密码强度不足")
            updates['password_hash'] = hash_password(updates['password'])
            del updates['password']
        
        if 'role' in updates:
            if updates['role'] not in ["super_admin", "admin", "moderator", "viewer"]:
                raise ValidationError("无效的角色")
        
        # 更新字段
        old_values = {}
        for key, value in updates.items():
            if hasattr(admin, key):
                old_values[key] = getattr(admin, key)
                setattr(admin, key, value)
        
        admin.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(admin)
        
        # 清除缓存
        cache_key = CacheKeys.admin(admin_id)
        await self.redis.delete(cache_key)
        
        # 记录审计日志
        await self.create_audit_log(
            admin_id=admin_id,
            action="update_admin",
            resource_type="admin",
            resource_id=admin_id,
            details={"old_values": old_values, "new_values": updates}
        )
        
        logger.info(f"更新管理员: {admin.username} (ID: {admin_id})")
        return admin
    
    async def get_admins(
        self,
        role: str = None,
        is_active: bool = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Admin]:
        """获取管理员列表"""
        query = select(Admin)
        
        if role:
            query = query.where(Admin.role == role)
        if is_active is not None:
            query = query.where(Admin.is_active == is_active)
        
        query = query.order_by(desc(Admin.created_at)).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    def check_permission(self, admin: Admin, permission: str) -> bool:
        """检查管理员权限"""
        # 超级管理员拥有所有权限
        if admin.role == "super_admin":
            return True
        
        # 检查角色权限
        role_permissions = {
            "admin": [
                "user_management", "order_management", "divination_management",
                "system_config", "audit_log", "statistics"
            ],
            "moderator": [
                "user_management", "divination_management", "audit_log"
            ],
            "viewer": [
                "statistics", "audit_log"
            ]
        }
        
        # 检查角色默认权限
        if permission in role_permissions.get(admin.role, []):
            return True
        
        # 检查自定义权限
        return permission in admin.permissions
    
    # 系统配置管理
    async def get_system_config(self, key: str) -> Optional[SystemConfig]:
        """获取系统配置"""
        cache_key = CacheKeys.system_config(key)
        
        # 尝试从缓存获取
        cached_config = await self.redis.get(cache_key)
        if cached_config:
            return cached_config
        
        # 从数据库查询
        result = await self.db.execute(
            select(SystemConfig).where(SystemConfig.key == key)
        )
        config = result.scalar_one_or_none()
        
        if config:
            # 缓存结果
            await self.redis.set(cache_key, config, expire=3600)
        
        return config
    
    async def set_system_config(
        self,
        key: str,
        value: Any,
        description: str = None,
        admin_id: int = None
    ) -> SystemConfig:
        """设置系统配置"""
        # 获取现有配置
        config = await self.get_system_config(key)
        
        if config:
            # 更新现有配置
            old_value = config.value
            config.value = value
            if description:
                config.description = description
            config.updated_at = datetime.utcnow()
            
            action = "update_config"
            details = {"key": key, "old_value": old_value, "new_value": value}
        else:
            # 创建新配置
            config = SystemConfig(
                key=key,
                value=value,
                description=description
            )
            self.db.add(config)
            
            action = "create_config"
            details = {"key": key, "value": value}
        
        await self.db.commit()
        await self.db.refresh(config)
        
        # 清除缓存
        cache_key = CacheKeys.system_config(key)
        await self.redis.delete(cache_key)
        
        # 记录审计日志
        if admin_id:
            await self.create_audit_log(
                admin_id=admin_id,
                action=action,
                resource_type="system_config",
                resource_id=config.id,
                details=details
            )
        
        logger.info(f"设置系统配置: {key} = {value}")
        return config
    
    async def get_all_system_configs(self) -> List[SystemConfig]:
        """获取所有系统配置"""
        result = await self.db.execute(
            select(SystemConfig).order_by(SystemConfig.key)
        )
        return result.scalars().all()
    
    # 用户反馈管理
    async def get_user_feedbacks(
        self,
        status: str = None,
        category: str = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[UserFeedback]:
        """获取用户反馈列表"""
        query = select(UserFeedback).options(selectinload(UserFeedback.user))
        
        if status:
            query = query.where(UserFeedback.status == status)
        if category:
            query = query.where(UserFeedback.category == category)
        
        query = query.order_by(desc(UserFeedback.created_at)).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_feedback_status(
        self,
        feedback_id: int,
        status: str,
        admin_response: str = None,
        admin_id: int = None
    ) -> Optional[UserFeedback]:
        """更新反馈状态"""
        result = await self.db.execute(
            select(UserFeedback).where(UserFeedback.id == feedback_id)
        )
        feedback = result.scalar_one_or_none()
        
        if not feedback:
            raise ResourceNotFoundError("反馈不存在")
        
        if status not in ["pending", "in_progress", "resolved", "closed"]:
            raise ValidationError("无效的状态")
        
        old_status = feedback.status
        feedback.status = status
        if admin_response:
            feedback.admin_response = admin_response
        feedback.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(feedback)
        
        # 记录审计日志
        if admin_id:
            await self.create_audit_log(
                admin_id=admin_id,
                action="update_feedback",
                resource_type="user_feedback",
                resource_id=feedback_id,
                details={
                    "old_status": old_status,
                    "new_status": status,
                    "admin_response": admin_response
                }
            )
        
        logger.info(f"更新反馈状态: {feedback_id} -> {status}")
        return feedback
    
    # 审计日志管理
    async def create_audit_log(
        self,
        admin_id: int,
        action: str,
        resource_type: str = None,
        resource_id: int = None,
        details: Dict[str, Any] = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> AuditLog:
        """创建审计日志"""
        audit_log = AuditLog(
            admin_id=admin_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(audit_log)
        await self.db.commit()
        
        return audit_log
    
    async def get_audit_logs(
        self,
        admin_id: int = None,
        action: str = None,
        resource_type: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AuditLog]:
        """获取审计日志"""
        query = select(AuditLog).options(selectinload(AuditLog.admin))
        
        if admin_id:
            query = query.where(AuditLog.admin_id == admin_id)
        if action:
            query = query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)
        
        query = query.order_by(desc(AuditLog.created_at)).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    # 系统统计
    async def get_system_stats(self, date: datetime = None) -> Optional[SystemStats]:
        """获取系统统计"""
        if date is None:
            date = datetime.utcnow().date()
        
        result = await self.db.execute(
            select(SystemStats).where(SystemStats.date == date)
        )
        return result.scalar_one_or_none()
    
    async def update_system_stats(self, date: datetime = None) -> SystemStats:
        """更新系统统计"""
        if date is None:
            date = datetime.utcnow().date()
        
        # 获取或创建统计记录
        stats = await self.get_system_stats(date)
        if not stats:
            stats = SystemStats(date=date)
            self.db.add(stats)
        
        # 计算各项统计
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        
        # 总用户数
        total_users_result = await self.db.execute(
            select(func.count(User.id))
        )
        stats.total_users = total_users_result.scalar()
        
        # 活跃用户数（当日有活动的用户）
        active_users_result = await self.db.execute(
            select(func.count(func.distinct(DivinationSession.user_id)))
            .where(
                and_(
                    DivinationSession.created_at >= start_of_day,
                    DivinationSession.created_at <= end_of_day
                )
            )
        )
        stats.active_users = active_users_result.scalar() or 0
        
        # 新注册用户数
        new_users_result = await self.db.execute(
            select(func.count(User.id))
            .where(
                and_(
                    User.created_at >= start_of_day,
                    User.created_at <= end_of_day
                )
            )
        )
        stats.new_users = new_users_result.scalar() or 0
        
        # 总占卜次数
        total_divinations_result = await self.db.execute(
            select(func.count(DivinationSession.id))
        )
        stats.total_divinations = total_divinations_result.scalar() or 0
        
        # 当日占卜次数
        daily_divinations_result = await self.db.execute(
            select(func.count(DivinationSession.id))
            .where(
                and_(
                    DivinationSession.created_at >= start_of_day,
                    DivinationSession.created_at <= end_of_day
                )
            )
        )
        stats.daily_divinations = daily_divinations_result.scalar() or 0
        
        # 总收入
        total_revenue_result = await self.db.execute(
            select(func.sum(Order.amount))
            .where(Order.status == "paid")
        )
        stats.total_revenue = float(total_revenue_result.scalar() or 0)
        
        # 当日收入
        daily_revenue_result = await self.db.execute(
            select(func.sum(Order.amount))
            .where(
                and_(
                    Order.status == "paid",
                    Order.paid_at >= start_of_day,
                    Order.paid_at <= end_of_day
                )
            )
        )
        stats.daily_revenue = float(daily_revenue_result.scalar() or 0)
        
        stats.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(stats)
        
        logger.info(f"更新系统统计: {date}")
        return stats
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """获取仪表板统计数据"""
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        # 获取今日和昨日统计
        today_stats = await self.get_system_stats(today)
        yesterday_stats = await self.get_system_stats(yesterday)
        
        if not today_stats:
            today_stats = await self.update_system_stats(today)
        
        # 计算增长率
        def calculate_growth(current, previous):
            if not previous or previous == 0:
                return 0
            return ((current - previous) / previous) * 100
        
        yesterday_values = {
            "users": yesterday_stats.new_users if yesterday_stats else 0,
            "divinations": yesterday_stats.daily_divinations if yesterday_stats else 0,
            "revenue": yesterday_stats.daily_revenue if yesterday_stats else 0,
            "active_users": yesterday_stats.active_users if yesterday_stats else 0
        }
        
        return {
            "total_users": today_stats.total_users,
            "new_users_today": today_stats.new_users,
            "new_users_growth": calculate_growth(today_stats.new_users, yesterday_values["users"]),
            
            "active_users_today": today_stats.active_users,
            "active_users_growth": calculate_growth(today_stats.active_users, yesterday_values["active_users"]),
            
            "total_divinations": today_stats.total_divinations,
            "divinations_today": today_stats.daily_divinations,
            "divinations_growth": calculate_growth(today_stats.daily_divinations, yesterday_values["divinations"]),
            
            "total_revenue": today_stats.total_revenue,
            "revenue_today": today_stats.daily_revenue,
            "revenue_growth": calculate_growth(today_stats.daily_revenue, yesterday_values["revenue"]),
            
            "last_updated": today_stats.updated_at.isoformat()
        }
    
    # 数据导出
    async def export_user_data(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        format: str = "csv"
    ) -> Dict[str, Any]:
        """导出用户数据"""
        query = select(User)
        
        if start_date:
            query = query.where(User.created_at >= start_date)
        if end_date:
            query = query.where(User.created_at <= end_date)
        
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        # 这里应该实现实际的数据导出逻辑
        # 返回导出文件的信息
        return {
            "total_records": len(users),
            "format": format,
            "generated_at": datetime.utcnow().isoformat(),
            "download_url": f"/admin/exports/users_{get_current_timestamp()}.{format}"
        }
    
    async def export_order_data(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        format: str = "csv"
    ) -> Dict[str, Any]:
        """导出订单数据"""
        query = select(Order).options(selectinload(Order.user))
        
        if start_date:
            query = query.where(Order.created_at >= start_date)
        if end_date:
            query = query.where(Order.created_at <= end_date)
        
        result = await self.db.execute(query)
        orders = result.scalars().all()
        
        return {
            "total_records": len(orders),
            "format": format,
            "generated_at": datetime.utcnow().isoformat(),
            "download_url": f"/admin/exports/orders_{get_current_timestamp()}.{format}"
        }
    
    # 缓存管理
    async def clear_admin_cache(self, admin_id: int):
        """清除管理员缓存"""
        cache_key = CacheKeys.admin(admin_id)
        await self.redis.delete(cache_key)
    
    async def clear_system_config_cache(self, key: str = None):
        """清除系统配置缓存"""
        if key:
            cache_key = CacheKeys.system_config(key)
            await self.redis.delete(cache_key)
        else:
            # 清除所有系统配置缓存
            pattern = CacheKeys.system_config("*")
            await self.redis.delete_pattern(pattern)