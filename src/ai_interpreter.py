"""
塔罗AI解读器
使用AI模型生成塔罗牌解读

作者: Lima
支持: OpenAI GPT、DeepSeek
"""

import openai
import os
import sys
import json
from typing import List, Dict
from pathlib import Path
from dotenv import load_dotenv

# 确保能正确导入项目模块
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv()

try:
    from src.language_manager import language_manager
except ImportError:
    # 如果language_manager不存在，创建一个简单的替代
    class SimpleLanguageManager:
        def get_user_language(self, user_id):
            return 'zh'
        def get_text(self, key, user_id, **kwargs):
            return "获取文本失败"
        def get_ai_prompt(self, key, user_id):
            return "获取提示词失败"
    language_manager = SimpleLanguageManager()

class TarotAIInterpreter:
    """
    塔罗AI解读器
    支持OpenAI和DeepSeek两种AI模型
    """
    def __init__(self):
        # 从环境变量获取AI模型配置
        self.ai_model = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
        
        # 根据配置的模型类型初始化相应的客户端
        if self.ai_model.startswith('gpt') or self.ai_model.startswith('openai'):
            # OpenAI模型
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("使用OpenAI模型需要设置OPENAI_API_KEY环境变量")
                
            self.client = openai.OpenAI(api_key=api_key)
            self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
            self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
            self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
            
        elif self.ai_model == 'deepseek-chat' or self.ai_model.startswith('deepseek'):
            # DeepSeek模型
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                raise ValueError("使用DeepSeek模型需要设置DEEPSEEK_API_KEY环境变量")
                
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
            )
            self.model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
            self.max_tokens = int(os.getenv('DEEPSEEK_MAX_TOKENS', '1000'))
            self.temperature = float(os.getenv('DEEPSEEK_TEMPERATURE', '0.7'))
            
        else:
            raise ValueError(f"不支持的AI模型: {self.ai_model}。支持的模型: gpt-3.5-turbo, gpt-4, deepseek-chat")
    
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