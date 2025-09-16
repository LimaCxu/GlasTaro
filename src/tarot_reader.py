"""
塔罗牌读取器
处理塔罗牌的抽取和解读逻辑

作者: Lima
"""

import random
import os
import sys
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# 确保能正确导入项目模块
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from data.tarot_cards import get_all_cards, get_card_by_id
from src.ai_interpreter import TarotAIInterpreter

class TarotReader:
    def __init__(self):
        self.cards = get_all_cards()
        self.ai_interpreter = TarotAIInterpreter()
        self.max_cards = int(os.getenv('MAX_CARDS_PER_READING', '3'))
    
    def draw_cards(self, num_cards: int = 3) -> List[Dict]:
        """
        随机抽取指定数量的塔罗牌
        
        Args:
            num_cards: 要抽取的牌数量
            
        Returns:
            抽取的塔罗牌列表
        """
        if num_cards > self.max_cards:
            num_cards = self.max_cards
            
        # 随机选择牌
        selected_cards = random.sample(self.cards, num_cards)
        
        # 为每张牌随机分配正位或逆位
        for card in selected_cards:
            card['orientation'] = random.choice(['正位', '逆位'])
            
        return selected_cards
    
    def draw_specific_cards(self, card_ids: List[str]) -> List[Dict]:
        """
        抽取指定ID的塔罗牌
        
        Args:
            card_ids: 塔罗牌ID列表
            
        Returns:
            抽取的塔罗牌列表
        """
        selected_cards = []
        for card_id in card_ids:
            card = get_card_by_id(card_id)
            if card:
                # 复制牌以避免修改原始数据
                card_copy = card.copy()
                card_copy['orientation'] = random.choice(['正位', '逆位'])
                selected_cards.append(card_copy)
                
        return selected_cards
    
    def get_reading(self, cards: List[Dict], question: str = None, spread_type: str = "general", user_id: int = None) -> str:
        """
        获取塔罗牌解读
        
        Args:
            cards: 抽取的塔罗牌列表
            question: 用户问题
            spread_type: 牌阵类型
            user_id: 用户ID（用于确定语言）
            
        Returns:
            塔罗牌解读文本
        """
        return self.ai_interpreter.generate_reading(cards, question, spread_type, user_id)
    
    def get_daily_card(self, user_id: int = None) -> Tuple[Dict, str]:
        """
        获取每日塔罗牌及其解读
        
        Args:
            user_id: 用户ID（用于确定语言）
        
        Returns:
            (塔罗牌, 解读文本)
        """
        # 抽取一张牌
        card = random.choice(self.cards).copy()
        card['orientation'] = random.choice(['正位', '逆位'])
        
        # 获取AI解读
        reading = self.ai_interpreter.generate_daily_guidance(card, user_id)
        
        return card, reading
    
    def get_card_explanation(self, card_id: str) -> Tuple[Optional[Dict], str]:
        """
        获取特定塔罗牌的详细解释
        
        Args:
            card_id: 塔罗牌ID
            
        Returns:
            (塔罗牌, 解释文本)
        """
        card = get_card_by_id(card_id)
        if not card:
            return None, "未找到指定的塔罗牌"
        
        explanation = self.ai_interpreter.generate_card_explanation(card)
        return card, explanation
    
    def get_spread_options(self) -> Dict[str, str]:
        """
        获取可用的牌阵类型
        
        Returns:
            牌阵类型字典 {spread_id: spread_name}
        """
        return {
            "single": "单张牌阵",
            "three_card": "三张牌阵 (过去-现在-未来)",
            "love": "爱情牌阵",
            "career": "事业牌阵",
            "general": "综合牌阵",
            "decision": "决策牌阵"
        }
    
    def get_card_list(self, card_type: str = None) -> List[Dict]:
        """
        获取塔罗牌列表，可按类型筛选
        
        Args:
            card_type: 牌类型 ('major' 或 'minor')
            
        Returns:
            塔罗牌列表
        """
        if card_type:
            return [card for card in self.cards if card['type'] == card_type]
        return self.cards