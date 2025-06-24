# -*- coding: utf-8 -*-
"""
用户语言管理器

管理用户的语言偏好设置
"""

import json
import os
import sys
from typing import Dict, Optional
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.languages import languages

class LanguageManager:
    """用户语言管理器"""
    
    def __init__(self, data_file: str = "user_languages.json"):
        self.data_file = os.path.join(os.path.dirname(__file__), '..', 'data', data_file)
        self.user_languages: Dict[int, str] = {}
        self.load_user_languages()
    
    def load_user_languages(self):
        """从文件加载用户语言设置"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 转换字符串键为整数键
                    self.user_languages = {int(k): v for k, v in data.items()}
        except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
            print(f"加载用户语言设置失败: {e}")
            self.user_languages = {}
    
    def save_user_languages(self):
        """保存用户语言设置到文件"""
        try:
            # 确保数据目录存在
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # 转换整数键为字符串键以便JSON序列化
            data = {str(k): v for k, v in self.user_languages.items()}
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存用户语言设置失败: {e}")
    
    def set_user_language(self, user_id: int, language: str):
        """设置用户语言"""
        if language in languages.SUPPORTED_LANGUAGES:
            self.user_languages[user_id] = language
            self.save_user_languages()
            return True
        return False
    
    def get_user_language(self, user_id: int) -> str:
        """获取用户语言，如果未设置则返回默认语言"""
        return self.user_languages.get(user_id, languages.DEFAULT_LANGUAGE)
    
    def get_text(self, key: str, user_id: int, **kwargs) -> str:
        """获取用户语言对应的文本"""
        user_language = self.get_user_language(user_id)
        return languages.get_text(key, user_language, **kwargs)
    
    def get_spread_name(self, spread_type: str, user_id: int) -> str:
        """获取用户语言对应的牌阵名称"""
        user_language = self.get_user_language(user_id)
        return languages.get_spread_name(spread_type, user_language)
    
    def get_ai_prompt(self, prompt_type: str, user_id: int) -> str:
        """获取用户语言对应的AI提示词"""
        user_language = self.get_user_language(user_id)
        return languages.get_ai_prompt(prompt_type, user_language)
    
    def is_supported_language(self, language: str) -> bool:
        """检查是否为支持的语言"""
        return language in languages.SUPPORTED_LANGUAGES
    
    def get_supported_languages(self) -> Dict[str, str]:
        """获取支持的语言列表"""
        return languages.SUPPORTED_LANGUAGES.copy()
    
    def remove_user_language(self, user_id: int):
        """移除用户语言设置"""
        if user_id in self.user_languages:
            del self.user_languages[user_id]
            self.save_user_languages()
    
    def get_user_count_by_language(self) -> Dict[str, int]:
        """获取各语言的用户数量统计"""
        stats = {}
        for language in languages.SUPPORTED_LANGUAGES.keys():
            stats[language] = 0
        
        for user_language in self.user_languages.values():
            if user_language in stats:
                stats[user_language] += 1
        
        return stats
    
    def auto_detect_language_by_locale(self, user_id: int, language_code: str = None, country_code: str = None) -> str:
        """根据用户地区自动检测语言"""
        # 如果用户已经设置了语言，直接返回
        if user_id in self.user_languages:
            return self.user_languages[user_id]
        
        # 根据语言代码或国家代码自动检测
        detected_language = 'en'  # 默认英语
        
        if language_code:
            # 根据语言代码检测
            if language_code.startswith('zh'):
                detected_language = 'zh'
            elif language_code.startswith('ru'):
                detected_language = 'ru'
            elif language_code.startswith('en'):
                detected_language = 'en'
        
        if country_code:
            # 根据国家代码检测
            if country_code.upper() in ['CN', 'TW', 'HK', 'MO']:
                detected_language = 'zh'
            elif country_code.upper() == 'RU':
                detected_language = 'ru'
            else:
                detected_language = 'en'
        
        # 自动设置用户语言
        self.set_user_language(user_id, detected_language)
        return detected_language

# 创建全局实例
language_manager = LanguageManager()