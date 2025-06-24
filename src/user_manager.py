# -*- coding: utf-8 -*-
"""
用户管理模块

处理用户会话、请求限制、数据存储等功能。
"""

import time
import json
import os
import sys
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import config

class UserSession:
    """用户会话类"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.data = {}
        self.current_state = 'idle'
        self.waiting_for_question = False
        self.spread_type = None
        self.question = None
        self.cards = []
        
    def update_activity(self):
        """更新最后活动时间"""
        self.last_activity = datetime.now()
    
    def set_state(self, state: str, **kwargs):
        """设置用户状态"""
        self.current_state = state
        self.data.update(kwargs)
        self.update_activity()
    
    def get_data(self, key: str, default=None):
        """获取会话数据"""
        return self.data.get(key, default)
    
    def set_data(self, key: str, value: Any):
        """设置会话数据"""
        self.data[key] = value
        self.update_activity()
    
    def clear_reading_data(self):
        """清除占卜相关数据"""
        self.waiting_for_question = False
        self.spread_type = None
        self.question = None
        self.cards = []
        self.current_state = 'idle'
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """检查会话是否过期"""
        return (datetime.now() - self.last_activity).total_seconds() > timeout_minutes * 60

class RateLimiter:
    """请求频率限制器"""
    
    def __init__(self):
        self.requests = defaultdict(list)  # user_id -> [timestamp, ...]
        self.daily_requests = defaultdict(int)  # user_id -> count
        self.last_reset = datetime.now().date()
    
    def _reset_daily_if_needed(self):
        """如果需要，重置每日计数"""
        today = datetime.now().date()
        if today > self.last_reset:
            self.daily_requests.clear()
            self.last_reset = today
    
    def _clean_old_requests(self, user_id: int):
        """清理过期的请求记录"""
        now = time.time()
        hour_ago = now - 3600  # 1小时前
        
        self.requests[user_id] = [
            timestamp for timestamp in self.requests[user_id]
            if timestamp > hour_ago
        ]
    
    def can_make_request(self, user_id: int) -> Tuple[bool, str]:
        """检查用户是否可以发起请求"""
        self._reset_daily_if_needed()
        self._clean_old_requests(user_id)
        
        # 检查每小时限制
        hourly_count = len(self.requests[user_id])
        if hourly_count >= config.MAX_REQUESTS_PER_HOUR:
            return False, f"每小时最多可以进行 {config.MAX_REQUESTS_PER_HOUR} 次占卜，请稍后再试。"
        
        # 检查每日限制
        daily_count = self.daily_requests[user_id]
        if daily_count >= config.MAX_REQUESTS_PER_DAY:
            return False, f"每日最多可以进行 {config.MAX_REQUESTS_PER_DAY} 次占卜，请明天再试。"
        
        return True, ""
    
    def record_request(self, user_id: int):
        """记录用户请求"""
        now = time.time()
        self.requests[user_id].append(now)
        self.daily_requests[user_id] += 1
    
    def get_user_stats(self, user_id: int) -> Dict[str, int]:
        """获取用户使用统计"""
        self._reset_daily_if_needed()
        self._clean_old_requests(user_id)
        
        return {
            'hourly_requests': len(self.requests[user_id]),
            'daily_requests': self.daily_requests[user_id],
            'hourly_remaining': config.MAX_REQUESTS_PER_HOUR - len(self.requests[user_id]),
            'daily_remaining': config.MAX_REQUESTS_PER_DAY - self.daily_requests[user_id]
        }

class UserManager:
    """用户管理器"""
    
    def __init__(self):
        self.sessions: Dict[int, UserSession] = {}
        self.rate_limiter = RateLimiter()
        self.user_preferences: Dict[int, Dict] = defaultdict(dict)
        
    def get_session(self, user_id: int) -> UserSession:
        """获取或创建用户会话"""
        if user_id not in self.sessions:
            self.sessions[user_id] = UserSession(user_id)
        else:
            self.sessions[user_id].update_activity()
        
        return self.sessions[user_id]
    
    def cleanup_expired_sessions(self):
        """清理过期的会话"""
        expired_users = [
            user_id for user_id, session in self.sessions.items()
            if session.is_expired()
        ]
        
        for user_id in expired_users:
            del self.sessions[user_id]
    
    def can_user_make_request(self, user_id: int) -> Tuple[bool, str]:
        """检查用户是否可以发起请求"""
        return self.rate_limiter.can_make_request(user_id)
    
    def record_user_request(self, user_id: int):
        """记录用户请求"""
        self.rate_limiter.record_request(user_id)
    
    def get_user_stats(self, user_id: int) -> Dict[str, int]:
        """获取用户统计信息"""
        return self.rate_limiter.get_user_stats(user_id)
    
    def set_user_preference(self, user_id: int, key: str, value: Any):
        """设置用户偏好"""
        self.user_preferences[user_id][key] = value
    
    def get_user_preference(self, user_id: int, key: str, default=None):
        """获取用户偏好"""
        return self.user_preferences[user_id].get(key, default)
    
    def get_user_info(self, user_id: int) -> Dict[str, Any]:
        """获取用户完整信息"""
        session = self.get_session(user_id)
        stats = self.get_user_stats(user_id)
        preferences = self.user_preferences[user_id]
        
        return {
            'user_id': user_id,
            'session': {
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'current_state': session.current_state,
                'waiting_for_question': session.waiting_for_question,
                'spread_type': session.spread_type
            },
            'stats': stats,
            'preferences': preferences
        }
    
    def export_user_data(self, user_id: int) -> str:
        """导出用户数据（JSON格式）"""
        user_info = self.get_user_info(user_id)
        return json.dumps(user_info, indent=2, ensure_ascii=False)
    
    def reset_user_data(self, user_id: int):
        """重置用户数据"""
        if user_id in self.sessions:
            del self.sessions[user_id]
        
        if user_id in self.user_preferences:
            del self.user_preferences[user_id]
        
        # 清理频率限制记录
        if user_id in self.rate_limiter.requests:
            del self.rate_limiter.requests[user_id]
        
        if user_id in self.rate_limiter.daily_requests:
            del self.rate_limiter.daily_requests[user_id]

class DailyCardCache:
    """每日塔罗牌缓存"""
    
    def __init__(self):
        self.cache: Dict[str, Dict] = {}  # date -> {card_data, timestamp}
        self.user_daily_cards: Dict[int, Dict] = {}  # user_id -> {date: card_data}
    
    def get_daily_card(self, user_id: int) -> Optional[Dict]:
        """获取用户的每日塔罗牌"""
        today = datetime.now().date().isoformat()
        
        if user_id in self.user_daily_cards:
            if today in self.user_daily_cards[user_id]:
                return self.user_daily_cards[user_id][today]
        
        return None
    
    def set_daily_card(self, user_id: int, card_data: Dict):
        """设置用户的每日塔罗牌"""
        today = datetime.now().date().isoformat()
        
        if user_id not in self.user_daily_cards:
            self.user_daily_cards[user_id] = {}
        
        self.user_daily_cards[user_id][today] = {
            'card': card_data,
            'timestamp': datetime.now().isoformat()
        }
    
    def cleanup_old_cache(self, days_to_keep: int = 7):
        """清理旧的缓存数据"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).date()
        
        # 清理全局缓存
        expired_dates = [
            date for date in self.cache.keys()
            if datetime.fromisoformat(date).date() < cutoff_date
        ]
        
        for date in expired_dates:
            del self.cache[date]
        
        # 清理用户缓存
        for user_id in self.user_daily_cards:
            expired_dates = [
                date for date in self.user_daily_cards[user_id].keys()
                if datetime.fromisoformat(date).date() < cutoff_date
            ]
            
            for date in expired_dates:
                del self.user_daily_cards[user_id][date]

# 创建全局用户管理器实例
user_manager = UserManager()
daily_card_cache = DailyCardCache()