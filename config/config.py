# -*- coding: utf-8 -*-
"""
塔罗预测机器人配置文件

包含机器人的各种配置选项、常量和设置。
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """机器人配置类"""
    
    # Telegram 配置
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    BOT_USERNAME = os.getenv('BOT_USERNAME', 'TarotBot')
    
    # AI 模型配置
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')  # 支持: gpt-3.5-turbo, gpt-4, deepseek-chat
    
    # OpenAI 配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '1500'))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
    
    # DeepSeek 配置
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    DEEPSEEK_MAX_TOKENS = int(os.getenv('DEEPSEEK_MAX_TOKENS', '1500'))
    DEEPSEEK_TEMPERATURE = float(os.getenv('DEEPSEEK_TEMPERATURE', '0.7'))
    
    # 机器人功能配置
    MAX_CARDS_PER_READING = int(os.getenv('MAX_CARDS_PER_READING', '3'))
    READING_TIMEOUT = int(os.getenv('READING_TIMEOUT', '300'))
    DAILY_CARD_CACHE_TIME = int(os.getenv('DAILY_CARD_CACHE_TIME', '3600'))  # 1小时
    
    # 调试和日志配置
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # 用户限制配置
    MAX_REQUESTS_PER_HOUR = int(os.getenv('MAX_REQUESTS_PER_HOUR', '10'))
    MAX_REQUESTS_PER_DAY = int(os.getenv('MAX_REQUESTS_PER_DAY', '50'))
    
    # 文本配置
    WELCOME_MESSAGE = """
🔮 欢迎来到塔罗预测机器人！

我是你的塔罗牌指导师，可以为你提供：

✨ 塔罗牌占卜和解读
🌟 每日塔罗指导
📚 塔罗牌知识学习
💫 人生问题的深度洞察

请选择你想要的服务：
    """
    
    ERROR_MESSAGES = {
        'api_error': '抱歉，AI服务暂时不可用，请稍后再试。',
        'rate_limit': '你的请求过于频繁，请稍后再试。',
        'invalid_question': '请输入有效的问题，或发送"跳过"进行通用占卜。',
        'general_error': '发生了未知错误，请稍后重试。',
        'no_token': '机器人配置错误，请联系管理员。'
    }
    
    # 牌阵配置
    SPREAD_CONFIGS = {
        'single': {
            'name': '单张牌占卜',
            'description': '快速获得指导和建议',
            'card_count': 1,
            'positions': ['当前状况/指导']
        },
        'three_card': {
            'name': '三张牌占卜',
            'description': '了解过去、现在和未来',
            'card_count': 3,
            'positions': ['过去/根源', '现在/当前状况', '未来/结果']
        },
        'love': {
            'name': '爱情占卜',
            'description': '关于感情关系的指导',
            'card_count': 3,
            'positions': ['你的感受', '对方的感受', '关系的未来']
        },
        'career': {
            'name': '事业占卜',
            'description': '关于工作和事业的指导',
            'card_count': 3,
            'positions': ['当前工作状况', '挑战和机遇', '建议和方向']
        },
        'decision': {
            'name': '决策占卜',
            'description': '帮助做出重要决定',
            'card_count': 3,
            'positions': ['选项A的结果', '选项B的结果', '最佳选择']
        },
        'general': {
            'name': '综合占卜',
            'description': '全面的人生指导',
            'card_count': 3,
            'positions': ['当前状况', '挑战', '指导建议']
        }
    }
    
    # AI 提示词模板
    AI_PROMPTS = {
        'system_role': """
你是一位经验丰富的塔罗牌占卜师，擅长解读塔罗牌的含义并提供深刻的人生指导。
你的解读应该富有洞察力、温暖且具有启发性。
请用中文回答，语调要温暖、专业且富有同理心。
        """.strip(),
        
        'daily_guidance_role': """
你是一位温暖的塔罗牌指导师，擅长提供简洁而深刻的每日指导。
你的建议应该积极正面，富有启发性，适合作为每日的精神指导。
        """.strip(),
        
        'card_explanation_role': """
你是一位塔罗牌专家，擅长用简单易懂的方式解释塔罗牌的含义。
你的解释应该深入浅出，帮助人们理解塔罗牌的象征意义和实际应用。
        """.strip()
    }
    
    # 表情符号配置
    EMOJIS = {
        'tarot': '🔮',
        'cards': '🎴',
        'star': '⭐',
        'sparkles': '✨',
        'sun': '🌅',
        'book': '📚',
        'heart': '💕',
        'briefcase': '💼',
        'thinking': '🤔',
        'question': '❓',
        'home': '🏠',
        'back': '🔙',
        'next': '➡️',
        'prev': '⬅️',
        'up': '⬆️',
        'down': '⬇️',
        'fire': '🔥',
        'water': '💧',
        'air': '💨',
        'earth': '🌍',
        'loading': '⏳',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️'
    }
    
    # 验证配置
    @classmethod
    def validate(cls):
        """验证配置是否完整"""
        errors = []
        
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append('TELEGRAM_BOT_TOKEN 未设置')
        
        # 验证AI模型配置
        if cls.AI_MODEL.startswith('gpt'):
            if not cls.OPENAI_API_KEY:
                errors.append('使用GPT模型时，OPENAI_API_KEY 未设置')
            if cls.OPENAI_TEMPERATURE < 0 or cls.OPENAI_TEMPERATURE > 2:
                errors.append('OPENAI_TEMPERATURE 应该在 0-2 之间')
        elif cls.AI_MODEL == 'deepseek-chat':
            if not cls.DEEPSEEK_API_KEY:
                errors.append('使用DeepSeek模型时，DEEPSEEK_API_KEY 未设置')
            if cls.DEEPSEEK_TEMPERATURE < 0 or cls.DEEPSEEK_TEMPERATURE > 2:
                errors.append('DEEPSEEK_TEMPERATURE 应该在 0-2 之间')
        else:
            errors.append(f'不支持的AI模型: {cls.AI_MODEL}')
        
        if cls.MAX_CARDS_PER_READING < 1 or cls.MAX_CARDS_PER_READING > 10:
            errors.append('MAX_CARDS_PER_READING 应该在 1-10 之间')
        
        return errors
    
    @classmethod
    def get_spread_config(cls, spread_type):
        """获取特定牌阵的配置"""
        return cls.SPREAD_CONFIGS.get(spread_type, cls.SPREAD_CONFIGS['general'])
    
    @classmethod
    def get_emoji(cls, name):
        """获取表情符号"""
        return cls.EMOJIS.get(name, '')
    
    @classmethod
    def get_error_message(cls, error_type):
        """获取错误消息"""
        return cls.ERROR_MESSAGES.get(error_type, cls.ERROR_MESSAGES['general_error'])

# 创建全局配置实例
config = Config()

# 导出常用配置
TELEGRAM_BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
AI_MODEL = config.AI_MODEL
OPENAI_API_KEY = config.OPENAI_API_KEY
OPENAI_MODEL = config.OPENAI_MODEL
DEEPSEEK_API_KEY = config.DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL = config.DEEPSEEK_BASE_URL
DEEPSEEK_MODEL = config.DEEPSEEK_MODEL
MAX_CARDS_PER_READING = config.MAX_CARDS_PER_READING
DEBUG = config.DEBUG