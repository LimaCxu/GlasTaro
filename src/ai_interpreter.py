import openai
import os
from typing import List, Dict
import json
import openai
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.language_manager import language_manager
from config.config import Config

load_dotenv()

class TarotAIInterpreter:
    def __init__(self):
        self.ai_model = Config.AI_MODEL
        
        # 根据配置的模型类型初始化相应的客户端
        if self.ai_model.startswith('gpt'):
            self.client = openai.OpenAI(
                api_key=Config.OPENAI_API_KEY
            )
            self.model = Config.OPENAI_MODEL
            self.max_tokens = Config.OPENAI_MAX_TOKENS
            self.temperature = Config.OPENAI_TEMPERATURE
        elif self.ai_model == 'deepseek-chat':
            self.client = openai.OpenAI(
                api_key=Config.DEEPSEEK_API_KEY,
                base_url=Config.DEEPSEEK_BASE_URL
            )
            self.model = Config.DEEPSEEK_MODEL
            self.max_tokens = Config.DEEPSEEK_MAX_TOKENS
            self.temperature = Config.DEEPSEEK_TEMPERATURE
        else:
            raise ValueError(f"不支持的AI模型: {self.ai_model}")
    
    def generate_reading(self, cards: List[Dict], question: str = None, spread_type: str = "general", user_id: int = None) -> str:
        """
        生成塔罗牌解读
        
        Args:
            cards: 抽取的塔罗牌列表
            question: 用户问题
            spread_type: 牌阵类型
            user_id: 用户ID（用于确定语言）
        
        Returns:
            AI生成的塔罗牌解读
        """
        try:
            # 获取用户语言
            user_lang = language_manager.get_user_language(user_id) if user_id else 'zh'
            
            # 构建提示词
            prompt = self._build_prompt(cards, question, spread_type, user_lang, user_id)
            
            # 获取系统提示词
            system_prompt = language_manager.get_ai_prompt('system_prompt', user_id)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            if user_id:
                error_msg = language_manager.get_text('errors', user_id, ai_reading_failed=True)
                return f"{error_msg}: {str(e)}"
            else:
                return f"AI解读失败: {str(e)}"
    
    def _build_prompt(self, cards: List[Dict], question: str, spread_type: str, user_lang: str = 'zh', user_id: int = None) -> str:
        """
        构建AI提示词
        """
        # 获取多语言文本
        prompt_template = language_manager.get_ai_prompt('reading_prompt', user_id)
        question_label = language_manager.get_ai_prompt('question_label', user_id)
        spread_label = language_manager.get_ai_prompt('spread_label', user_id)
        cards_label = language_manager.get_ai_prompt('cards_label', user_id)
        
        prompt = prompt_template + "\n\n"
        
        if question:
            prompt += f"{question_label}: {question}\n\n"
        
        prompt += f"{spread_label}: {self._get_spread_description(spread_type, user_id, user_lang)}\n\n"
        prompt += cards_label + ":\n"
        
        for i, card in enumerate(cards, 1):
            position = self._get_position_meaning(spread_type, i-1, user_id, user_lang)
            orientation = card.get('orientation', '正位')
            if user_lang == 'en':
                orientation = 'Upright' if orientation == '正位' else 'Reversed'
            elif user_lang == 'ru':
                orientation = 'Прямое' if orientation == '正位' else 'Обратное'
            
            prompt += f"{i}. {card['name']} ({orientation})\n"
            position_label = language_manager.get_ai_prompt('position_label', user_id)
            prompt += f"   {position_label}: {position}\n"
            
            if card['type'] == 'major':
                meaning = card.get('upright_meaning' if card.get('orientation') == '正位' else 'reversed_meaning', '')
                prompt += f"   牌义: {meaning}\n"
                prompt += f"   描述: {card.get('description', '')}\n"
            else:
                prompt += f"   牌义: {card.get('meaning', '')}\n"
                prompt += f"   花色: {card.get('suit', '')} ({card.get('element', '')})\n"
            prompt += "\n"
        
        # 获取解读要求文本
        reading_requirements = language_manager.get_ai_prompt('reading_requirements', user_id)
        closing_instruction = language_manager.get_ai_prompt('closing_instruction', user_id)
        
        prompt += reading_requirements + "\n\n"
        prompt += closing_instruction
        
        return prompt
    
    def _get_spread_description(self, spread_type: str, user_id: int = None, user_lang: str = 'zh') -> str:
        """
        获取牌阵描述
        """
        if user_id is not None:
            return language_manager.get_text('spreads', user_id, **{spread_type: user_lang})
        else:
            # 默认返回中文描述
            spread_names = {
                'single': '单张牌占卜',
                'three_card': '三张牌占卜',
                'love': '爱情占卜',
                'career': '事业占卜',
                'decision': '决策占卜'
            }
            return spread_names.get(spread_type, spread_type)
    
    def _get_position_meaning(self, spread_type: str, position: int, user_id: int = None, user_lang: str = 'zh') -> str:
        """
        获取牌阵中特定位置的含义
        """
        if user_id is not None:
            # 从语言配置中获取位置含义
            position_key = f"{spread_type}_positions"
            positions = language_manager.get_text('spreads', user_id, **{position_key: user_lang})
            
            if isinstance(positions, list) and position < len(positions):
                return positions[position]
        
        # 默认返回位置编号
        if user_lang == 'en':
            return f"Position {position + 1}"
        elif user_lang == 'ru':
            return f"Позиция {position + 1}"
        else:
            return f"牌位{position + 1}"
    
    def generate_daily_guidance(self, card: Dict, user_id: int = None) -> str:
        """
        生成每日指导
        """
        try:
            # 获取用户语言
            user_lang = language_manager.get_user_language(user_id) if user_id else 'zh'
            
            # 获取多语言文本
            daily_prompt = language_manager.get_ai_prompt('daily_prompt', user_id)
            daily_system = language_manager.get_ai_prompt('daily_system', user_id)
            
            # 构建提示词
            card_meaning = card.get('upright_meaning' if card.get('orientation') == '正位' else 'reversed_meaning', card.get('meaning', ''))
            prompt = daily_prompt.format(card_name=card['name'], card_meaning=card_meaning)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": daily_system
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=min(800, self.max_tokens),
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            if user_id:
                error_msg = language_manager.get_text('errors', user_id, daily_guidance_failed=True)
                return f"{error_msg}: {str(e)}"
            else:
                return f"每日指导生成失败: {str(e)}"
    
    def generate_card_explanation(self, card: Dict, user_id: int = None) -> str:
        """
        生成单张牌的详细解释
        """
        try:
            # 获取用户语言
            user_lang = language_manager.get_user_language(user_id) if user_id else 'zh'
            
            # 获取多语言文本
            explanation_prompt = language_manager.get_ai_prompt('explanation_prompt', user_id)
            explanation_system = language_manager.get_ai_prompt('explanation_system', user_id)
            
            # 构建基本信息
            card_type = language_manager.get_ai_prompt('major_arcana', user_id) if card['type'] == 'major' else language_manager.get_ai_prompt('minor_arcana', user_id)
            
            basic_info = f"""- {language_manager.get_ai_prompt('card_name_label', user_id)}: {card['name']}
- {language_manager.get_ai_prompt('card_type_label', user_id)}: {card_type}"""
            
            if card['type'] == 'major':
                upright_label = language_manager.get_ai_prompt('upright_meaning_label', user_id)
                reversed_label = language_manager.get_ai_prompt('reversed_meaning_label', user_id)
                description_label = language_manager.get_ai_prompt('description_label', user_id)
                
                basic_info += f"""
- {upright_label}: {card.get('upright_meaning', '')}
- {reversed_label}: {card.get('reversed_meaning', '')}
- {description_label}: {card.get('description', '')}"""
            else:
                suit_label = language_manager.get_ai_prompt('suit_label', user_id)
                element_label = language_manager.get_ai_prompt('element_label', user_id)
                meaning_label = language_manager.get_ai_prompt('meaning_label', user_id)
                
                basic_info += f"""
- {suit_label}: {card.get('suit', '')}
- {element_label}: {card.get('element', '')}
- {meaning_label}: {card.get('meaning', '')}"""
            
            # 构建完整提示词
            prompt = explanation_prompt.format(card_name=card['name'], basic_info=basic_info)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": explanation_system
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=min(1000, self.max_tokens),
                temperature=min(0.6, self.temperature)
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            if user_id:
                error_msg = language_manager.get_text('errors', user_id, explanation_failed=True)
                return f"{error_msg}: {str(e)}"
            else:
                return f"牌面解释生成失败: {str(e)}"