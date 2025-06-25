# -*- coding: utf-8 -*-
"""
占卜服务模块
"""

import logging
import random
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload

from models.divination import DivinationSession, DailyCard, TarotCard, SpreadTemplate
from models.user import User, UserUsageStats
from models.order import UserTier
from config.redis_config import RedisManager, CacheKeys
from utils.exceptions import (
    DivinationError,
    ValidationError,
    ResourceNotFoundError,
    BusinessLogicError,
    RateLimitExceededError
)
from utils.validators import validate_divination_type
from utils.helpers import generate_short_id, get_current_timestamp

logger = logging.getLogger(__name__)

class DivinationService:
    """占卜服务"""
    
    def __init__(self, db: AsyncSession, redis: RedisManager):
        self.db = db
        self.redis = redis
    
    # 塔罗牌管理
    async def get_all_tarot_cards(self, active_only: bool = True) -> List[TarotCard]:
        """获取所有塔罗牌"""
        cache_key = CacheKeys.tarot_cards(active_only)
        
        # 尝试从缓存获取
        cached_cards = await self.redis.get(cache_key)
        if cached_cards:
            return cached_cards
        
        # 从数据库查询
        query = select(TarotCard)
        if active_only:
            query = query.where(TarotCard.is_active == True)
        
        query = query.order_by(TarotCard.card_number)
        result = await self.db.execute(query)
        cards = result.scalars().all()
        
        # 缓存结果
        await self.redis.set(cache_key, cards, expire=3600)  # 缓存1小时
        
        return cards
    
    async def get_tarot_card_by_id(self, card_id: int) -> Optional[TarotCard]:
        """根据ID获取塔罗牌"""
        cache_key = CacheKeys.tarot_card(card_id)
        
        # 尝试从缓存获取
        cached_card = await self.redis.get(cache_key)
        if cached_card:
            return cached_card
        
        # 从数据库查询
        result = await self.db.execute(
            select(TarotCard).where(TarotCard.id == card_id)
        )
        card = result.scalar_one_or_none()
        
        if card:
            # 缓存结果
            await self.redis.set(cache_key, card, expire=3600)
        
        return card
    
    async def get_random_tarot_cards(self, count: int = 1, exclude_ids: List[int] = None) -> List[TarotCard]:
        """随机获取塔罗牌"""
        if count <= 0:
            raise ValidationError("抽取数量必须大于0")
        
        # 获取所有可用的塔罗牌
        all_cards = await self.get_all_tarot_cards(active_only=True)
        
        # 排除指定的牌
        if exclude_ids:
            all_cards = [card for card in all_cards if card.id not in exclude_ids]
        
        if len(all_cards) < count:
            raise DivinationError(f"可用塔罗牌数量不足，需要 {count} 张，可用 {len(all_cards)} 张")
        
        # 随机选择
        selected_cards = random.sample(all_cards, count)
        
        return selected_cards
    
    # 牌阵模板管理
    async def get_spread_templates(self, active_only: bool = True) -> List[SpreadTemplate]:
        """获取牌阵模板列表"""
        cache_key = CacheKeys.spread_templates(active_only)
        
        # 尝试从缓存获取
        cached_templates = await self.redis.get(cache_key)
        if cached_templates:
            return cached_templates
        
        # 从数据库查询
        query = select(SpreadTemplate)
        if active_only:
            query = query.where(SpreadTemplate.is_active == True)
        
        query = query.order_by(SpreadTemplate.card_count, SpreadTemplate.name)
        result = await self.db.execute(query)
        templates = result.scalars().all()
        
        # 缓存结果
        await self.redis.set(cache_key, templates, expire=3600)
        
        return templates
    
    async def get_spread_template_by_id(self, template_id: int) -> Optional[SpreadTemplate]:
        """根据ID获取牌阵模板"""
        cache_key = CacheKeys.spread_template(template_id)
        
        # 尝试从缓存获取
        cached_template = await self.redis.get(cache_key)
        if cached_template:
            return cached_template
        
        # 从数据库查询
        result = await self.db.execute(
            select(SpreadTemplate).where(SpreadTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()
        
        if template:
            # 缓存结果
            await self.redis.set(cache_key, template, expire=3600)
        
        return template
    
    async def get_spread_template_by_name(self, name: str) -> Optional[SpreadTemplate]:
        """根据名称获取牌阵模板"""
        result = await self.db.execute(
            select(SpreadTemplate).where(
                and_(
                    SpreadTemplate.name == name,
                    SpreadTemplate.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    # 每日塔罗牌
    async def get_daily_card(self, user_id: int, target_date: date = None) -> Optional[DailyCard]:
        """获取每日塔罗牌"""
        if target_date is None:
            target_date = date.today()
        
        cache_key = CacheKeys.daily_card(user_id, target_date)
        
        # 尝试从缓存获取
        cached_card = await self.redis.get(cache_key)
        if cached_card:
            return cached_card
        
        # 从数据库查询
        result = await self.db.execute(
            select(DailyCard)
            .options(selectinload(DailyCard.card))
            .where(
                and_(
                    DailyCard.user_id == user_id,
                    DailyCard.date == target_date
                )
            )
        )
        daily_card = result.scalar_one_or_none()
        
        if daily_card:
            # 缓存结果
            await self.redis.set(cache_key, daily_card, expire=86400)  # 缓存24小时
        
        return daily_card
    
    async def create_daily_card(self, user_id: int, target_date: date = None) -> DailyCard:
        """创建每日塔罗牌"""
        if target_date is None:
            target_date = date.today()
        
        # 检查是否已存在
        existing_card = await self.get_daily_card(user_id, target_date)
        if existing_card:
            return existing_card
        
        # 随机选择一张塔罗牌
        selected_cards = await self.get_random_tarot_cards(count=1)
        if not selected_cards:
            raise DivinationError("无法获取塔罗牌")
        
        card = selected_cards[0]
        
        # 随机选择正逆位
        is_reversed = random.choice([True, False])
        
        # 创建每日塔罗牌记录
        daily_card = DailyCard(
            user_id=user_id,
            card_id=card.id,
            date=target_date,
            is_reversed=is_reversed,
            interpretation=self._get_card_interpretation(card, is_reversed)
        )
        
        self.db.add(daily_card)
        await self.db.commit()
        await self.db.refresh(daily_card)
        
        # 加载关联的塔罗牌信息
        await self.db.refresh(daily_card, ["card"])
        
        # 缓存结果
        cache_key = CacheKeys.daily_card(user_id, target_date)
        await self.redis.set(cache_key, daily_card, expire=86400)
        
        logger.info(f"创建每日塔罗牌: 用户 {user_id}, 日期 {target_date}, 牌 {card.name}")
        return daily_card
    
    # 占卜会话管理
    async def create_divination_session(
        self,
        user_id: int,
        divination_type: str,
        question: str = None,
        spread_template_id: int = None,
        is_free: bool = False
    ) -> DivinationSession:
        """创建占卜会话"""
        # 验证占卜类型
        if not validate_divination_type(divination_type):
            raise ValidationError("无效的占卜类型")
        
        # 检查用户占卜次数限制
        if not is_free:
            can_divinate, reason = await self._check_divination_limit(user_id)
            if not can_divinate:
                raise RateLimitExceededError(reason)
        
        # 获取牌阵模板
        spread_template = None
        if spread_template_id:
            spread_template = await self.get_spread_template_by_id(spread_template_id)
            if not spread_template:
                raise ResourceNotFoundError("牌阵模板不存在")
        else:
            # 根据占卜类型选择默认牌阵
            spread_template = await self._get_default_spread_template(divination_type)
        
        if not spread_template:
            raise DivinationError("无法找到合适的牌阵模板")
        
        # 抽取塔罗牌
        cards = await self.get_random_tarot_cards(count=spread_template.card_count)
        
        # 生成会话ID
        session_id = f"DIV-{generate_short_id()}-{get_current_timestamp()}"
        
        # 准备牌的数据
        cards_data = []
        for i, card in enumerate(cards):
            is_reversed = random.choice([True, False])
            position_name = spread_template.positions.get(str(i), f"位置{i+1}")
            
            cards_data.append({
                "position": i,
                "position_name": position_name,
                "card_id": card.id,
                "card_name": card.name,
                "is_reversed": is_reversed,
                "interpretation": self._get_card_interpretation(card, is_reversed, position_name)
            })
        
        # 创建占卜会话
        session = DivinationSession(
            user_id=user_id,
            session_id=session_id,
            divination_type=divination_type,
            question=question,
            spread_template_id=spread_template.id,
            cards_data=cards_data,
            status="completed",
            is_free=is_free,
            interpretation=self._generate_overall_interpretation(cards_data, question, divination_type)
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        # 更新用户使用统计
        await self._update_user_usage_stats(user_id, is_free)
        
        # 缓存结果
        cache_key = CacheKeys.divination_session(session.id)
        await self.redis.set(cache_key, session, expire=3600)
        
        logger.info(f"创建占卜会话: {session_id} (用户: {user_id}, 类型: {divination_type})")
        return session
    
    async def get_divination_session_by_id(self, session_id: int) -> Optional[DivinationSession]:
        """根据ID获取占卜会话"""
        cache_key = CacheKeys.divination_session(session_id)
        
        # 尝试从缓存获取
        cached_session = await self.redis.get(cache_key)
        if cached_session:
            return cached_session
        
        # 从数据库查询
        result = await self.db.execute(
            select(DivinationSession)
            .options(selectinload(DivinationSession.user), selectinload(DivinationSession.spread_template))
            .where(DivinationSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if session:
            # 缓存结果
            await self.redis.set(cache_key, session, expire=3600)
        
        return session
    
    async def get_divination_session_by_session_id(self, session_id: str) -> Optional[DivinationSession]:
        """根据会话ID获取占卜会话"""
        result = await self.db.execute(
            select(DivinationSession)
            .options(selectinload(DivinationSession.user), selectinload(DivinationSession.spread_template))
            .where(DivinationSession.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_divination_sessions(
        self,
        user_id: int,
        divination_type: str = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[DivinationSession]:
        """获取用户占卜会话列表"""
        query = select(DivinationSession).where(DivinationSession.user_id == user_id)
        
        if divination_type:
            query = query.where(DivinationSession.divination_type == divination_type)
        
        query = query.order_by(desc(DivinationSession.created_at)).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_user_divination_history(
        self,
        user_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """获取用户占卜历史统计"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 按日期统计占卜次数
        result = await self.db.execute(
            select(
                func.date(DivinationSession.created_at).label("date"),
                DivinationSession.divination_type,
                func.count(DivinationSession.id).label("count")
            )
            .where(
                and_(
                    DivinationSession.user_id == user_id,
                    DivinationSession.created_at >= start_date
                )
            )
            .group_by("date", DivinationSession.divination_type)
            .order_by("date")
        )
        
        history = []
        for row in result.fetchall():
            history.append({
                "date": row.date.isoformat(),
                "divination_type": row.divination_type,
                "count": row.count
            })
        
        return history
    
    # 占卜限制检查
    async def _check_divination_limit(self, user_id: int) -> Tuple[bool, str]:
        """检查用户占卜次数限制"""
        # 获取用户等级信息
        user_tier = await self._get_user_current_tier(user_id)
        if not user_tier:
            # 免费用户，检查每日免费次数
            daily_free_limit = 3  # 默认每日免费次数
        else:
            daily_free_limit = user_tier.daily_free_divinations
        
        # 检查今日已使用次数
        today = date.today()
        result = await self.db.execute(
            select(func.count(DivinationSession.id))
            .where(
                and_(
                    DivinationSession.user_id == user_id,
                    func.date(DivinationSession.created_at) == today,
                    DivinationSession.is_free == True
                )
            )
        )
        used_count = result.scalar() or 0
        
        if used_count >= daily_free_limit:
            return False, f"今日免费占卜次数已用完 ({used_count}/{daily_free_limit})"
        
        return True, f"剩余免费占卜次数: {daily_free_limit - used_count}"
    
    async def _get_user_current_tier(self, user_id: int) -> Optional[UserTier]:
        """获取用户当前等级"""
        # 这里需要查询用户的订阅状态
        # 暂时返回None，表示免费用户
        return None
    
    async def _get_default_spread_template(self, divination_type: str) -> Optional[SpreadTemplate]:
        """根据占卜类型获取默认牌阵模板"""
        # 定义默认牌阵映射
        default_spreads = {
            "love": "爱情三角阵",
            "career": "事业发展阵",
            "fortune": "财运分析阵",
            "health": "健康指导阵",
            "general": "综合运势阵",
            "daily": "每日指引阵"
        }
        
        spread_name = default_spreads.get(divination_type, "综合运势阵")
        return await self.get_spread_template_by_name(spread_name)
    
    async def _update_user_usage_stats(self, user_id: int, is_free: bool):
        """更新用户使用统计"""
        # 获取或创建用户统计记录
        result = await self.db.execute(
            select(UserUsageStats).where(UserUsageStats.user_id == user_id)
        )
        stats = result.scalar_one_or_none()
        
        if not stats:
            stats = UserUsageStats(
                user_id=user_id,
                total_divinations=0,
                free_divinations=0,
                paid_divinations=0,
                total_usage_time=0
            )
            self.db.add(stats)
        
        # 更新统计
        stats.total_divinations += 1
        if is_free:
            stats.free_divinations += 1
        else:
            stats.paid_divinations += 1
        
        stats.last_divination_at = datetime.utcnow()
        stats.updated_at = datetime.utcnow()
        
        await self.db.commit()
    
    # 解释生成
    def _get_card_interpretation(self, card: TarotCard, is_reversed: bool, position_name: str = None) -> str:
        """获取塔罗牌解释"""
        if is_reversed:
            interpretation = card.reversed_meaning or f"{card.upright_meaning}（逆位）"
        else:
            interpretation = card.upright_meaning
        
        if position_name:
            interpretation = f"在{position_name}位置：{interpretation}"
        
        return interpretation
    
    def _generate_overall_interpretation(
        self,
        cards_data: List[Dict[str, Any]],
        question: str = None,
        divination_type: str = None
    ) -> str:
        """生成整体解释"""
        # 这里可以集成AI服务来生成更智能的解释
        # 目前使用简单的模板
        
        interpretation_parts = []
        
        if question:
            interpretation_parts.append(f"针对您的问题：{question}")
        
        interpretation_parts.append("塔罗牌为您揭示：")
        
        for card_info in cards_data:
            card_desc = f"{card_info['position_name']}抽到了{card_info['card_name']}"
            if card_info['is_reversed']:
                card_desc += "（逆位）"
            card_desc += f"，{card_info['interpretation']}"
            interpretation_parts.append(card_desc)
        
        # 添加总结
        type_advice = {
            "love": "在感情方面，建议您保持开放的心态，真诚地面对自己的感受。",
            "career": "在事业发展上，需要您积极主动，把握机遇的同时也要谨慎决策。",
            "fortune": "在财运方面，理性投资和稳健理财是关键。",
            "health": "在健康方面，注意身心平衡，适当休息和锻炼。",
            "general": "总体而言，保持积极乐观的心态，相信自己的能力。"
        }
        
        if divination_type in type_advice:
            interpretation_parts.append(type_advice[divination_type])
        
        return "\n\n".join(interpretation_parts)
    
    # 统计和分析
    async def get_divination_stats(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """获取占卜统计"""
        query = select(DivinationSession)
        
        if start_date:
            query = query.where(DivinationSession.created_at >= start_date)
        if end_date:
            query = query.where(DivinationSession.created_at <= end_date)
        
        # 总占卜次数
        total_result = await self.db.execute(
            select(func.count(DivinationSession.id)).select_from(query.subquery())
        )
        total_divinations = total_result.scalar()
        
        # 按类型统计
        type_result = await self.db.execute(
            select(DivinationSession.divination_type, func.count(DivinationSession.id))
            .select_from(query.subquery())
            .group_by(DivinationSession.divination_type)
        )
        type_stats = dict(type_result.fetchall())
        
        # 免费vs付费统计
        free_result = await self.db.execute(
            select(DivinationSession.is_free, func.count(DivinationSession.id))
            .select_from(query.subquery())
            .group_by(DivinationSession.is_free)
        )
        free_stats = dict(free_result.fetchall())
        
        return {
            "total_divinations": total_divinations,
            "type_stats": type_stats,
            "free_stats": {
                "free": free_stats.get(True, 0),
                "paid": free_stats.get(False, 0)
            },
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def get_popular_cards(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门塔罗牌"""
        # 这需要分析占卜会话中的牌数据
        # 由于cards_data是JSON字段，查询会比较复杂
        # 这里返回一个示例结果
        return [
            {"card_name": "愚者", "usage_count": 150},
            {"card_name": "魔术师", "usage_count": 142},
            {"card_name": "女祭司", "usage_count": 138},
        ]
    
    # 缓存管理
    async def clear_divination_cache(self, session_id: int):
        """清除占卜会话缓存"""
        cache_key = CacheKeys.divination_session(session_id)
        await self.redis.delete(cache_key)
    
    async def clear_daily_card_cache(self, user_id: int, target_date: date = None):
        """清除每日塔罗牌缓存"""
        if target_date is None:
            target_date = date.today()
        
        cache_key = CacheKeys.daily_card(user_id, target_date)
        await self.redis.delete(cache_key)