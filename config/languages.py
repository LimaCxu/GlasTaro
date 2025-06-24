# -*- coding: utf-8 -*-
"""
多语言配置文件

支持中文、英语、俄语三种语言
"""

class Languages:
    """多语言文本配置"""
    
    # 支持的语言列表
    SUPPORTED_LANGUAGES = {
        'zh': '中文 🇨🇳',
        'en': 'English 🇺🇸', 
        'ru': 'Русский 🇷🇺'
    }
    
    # 默认语言
    DEFAULT_LANGUAGE = 'zh'
    
    # 多语言文本
    TEXTS = {
        # 欢迎消息
        'welcome': {
            'zh': """🔮 欢迎来到塔罗预测机器人！

你好 {name}！我是你的塔罗牌指导师，可以为你提供：

✨ 塔罗牌占卜和解读
🌟 每日塔罗指导
📚 塔罗牌知识学习
💫 人生问题的深度洞察

请选择你想要的服务：""",
            'en': """🔮 Welcome to Tarot Prediction Bot!

Hello {name}! I'm your tarot guide, offering:

✨ Tarot card readings and interpretations
🌟 Daily tarot guidance
📚 Tarot knowledge learning
💫 Deep insights into life questions

Please choose your desired service:""",
            'ru': """🔮 Добро пожаловать в бота предсказаний Таро!

Привет {name}! Я ваш гид по Таро, предлагаю:

✨ Расклады и толкования карт Таро
🌟 Ежедневные указания Таро
📚 Изучение знаний Таро
💫 Глубокие прозрения в жизненные вопросы

Пожалуйста, выберите желаемую услугу:"""
        },
        
        # 主菜单按钮
        'menu_reading': {
            'zh': '🎴 开始占卜',
            'en': '🎴 Start Reading',
            'ru': '🎴 Начать расклад'
        },
        'menu_daily': {
            'zh': '🌅 每日塔罗',
            'en': '🌅 Daily Tarot',
            'ru': '🌅 Ежедневное Таро'
        },
        'menu_learn': {
            'zh': '📖 学习塔罗',
            'en': '📖 Learn Tarot',
            'ru': '📖 Изучить Таро'
        },
        'menu_help': {
            'zh': '❓ 帮助',
            'en': '❓ Help',
            'ru': '❓ Помощь'
        },
        'menu_language': {
            'zh': '🌐 语言设置',
            'en': '🌐 Language',
            'ru': '🌐 Язык'
        },
        
        # 语言选择
        'language_select': {
            'zh': '🌐 请选择你的语言：',
            'en': '🌐 Please select your language:',
            'ru': '🌐 Пожалуйста, выберите ваш язык:'
        },
        'language_changed': {
            'zh': '✅ 语言已切换为中文',
            'en': '✅ Language changed to English',
            'ru': '✅ Язык изменен на русский'
        },
        
        # 占卜类型
        'spread_select': {
            'zh': '🎴 请选择占卜类型：',
            'en': '🎴 Please select reading type:',
            'ru': '🎴 Пожалуйста, выберите тип расклада:'
        },
        'spread_single': {
            'zh': '🌟 单张牌占卜',
            'en': '🌟 Single Card Reading',
            'ru': '🌟 Расклад одной карты'
        },
        'spread_three': {
            'zh': '🔮 三张牌占卜',
            'en': '🔮 Three Card Reading',
            'ru': '🔮 Расклад трех карт'
        },
        'spread_love': {
            'zh': '💕 爱情占卜',
            'en': '💕 Love Reading',
            'ru': '💕 Любовный расклад'
        },
        'spread_career': {
            'zh': '💼 事业占卜',
            'en': '💼 Career Reading',
            'ru': '💼 Карьерный расклад'
        },
        'spread_decision': {
            'zh': '🤔 决策占卜',
            'en': '🤔 Decision Reading',
            'ru': '🤔 Расклад для решений'
        },
        
        # 问题输入
        'ask_question': {
            'zh': """🎴 {spread_name}

请输入你想要占卜的问题，或者发送 "跳过" 进行通用占卜。

💡 提示：
• 问题越具体，解读越准确
• 避免是非题，多问"如何"、"为什么"
• 保持开放的心态""",
            'en': """🎴 {spread_name}

Please enter your question for the reading, or send "skip" for a general reading.

💡 Tips:
• More specific questions lead to more accurate readings
• Avoid yes/no questions, ask "how" and "why"
• Keep an open mind""",
            'ru': """🎴 {spread_name}

Пожалуйста, введите ваш вопрос для расклада или отправьте "пропустить" для общего расклада.

💡 Советы:
• Более конкретные вопросы дают более точные толкования
• Избегайте вопросов да/нет, спрашивайте "как" и "почему"
• Сохраняйте открытый ум"""
        },
        'skip_question': {
            'zh': '⏭️ 跳过问题',
            'en': '⏭️ Skip Question',
            'ru': '⏭️ Пропустить вопрос'
        },
        
        # 占卜进行中
        'reading_loading': {
            'zh': '🔮 正在为你抽取塔罗牌...',
            'en': '🔮 Drawing tarot cards for you...',
            'ru': '🔮 Вытягиваю карты Таро для вас...'
        },
        
        # 每日塔罗
        'daily_card_title': {
            'zh': '🌅 今日塔罗指导',
            'en': '🌅 Today\'s Tarot Guidance',
            'ru': '🌅 Сегодняшнее руководство Таро'
        },
        
        # 学习塔罗
        'learn_select': {
            'zh': '📚 选择学习内容：',
            'en': '📚 Choose learning content:',
            'ru': '📚 Выберите содержание для изучения:'
        },
        'learn_major': {
            'zh': '🌟 大阿卡纳',
            'en': '🌟 Major Arcana',
            'ru': '🌟 Старшие Арканы'
        },
        'learn_minor': {
            'zh': '🎴 小阿卡纳',
            'en': '🎴 Minor Arcana',
            'ru': '🎴 Младшие Арканы'
        },
        
        # 通用按钮
        'back_main': {
            'zh': '🔄 返回主菜单',
            'en': '🔄 Back to Main',
            'ru': '🔄 Назад в главное меню'
        },
        'back_spreads': {
            'zh': '🔙 返回选择',
            'en': '🔙 Back to Selection',
            'ru': '🔙 Назад к выбору'
        },
        'back_learning': {
            'zh': '🔙 返回学习',
            'en': '🔙 Back to Learning',
            'ru': '🔙 Назад к изучению'
        },
        
        # 帮助信息
        'help_text': {
            'zh': """🔮 塔罗预测机器人使用指南

📋 可用命令：
/start - 开始使用机器人
/daily - 获取每日塔罗指导
/reading - 开始塔罗占卜
/learn - 学习塔罗牌知识
/language - 切换语言
/help - 显示此帮助信息

🎴 占卜功能：
• 单张牌占卜 - 快速指导
• 三张牌占卜 - 过去现在未来
• 爱情占卜 - 感情关系指导
• 事业占卜 - 工作发展建议
• 决策占卜 - 重要选择帮助

💡 使用技巧：
• 在占卜前先明确你的问题
• 保持开放和诚实的心态
• 将解读作为参考和启发
• 最终决定权在你自己手中

如有问题，请随时联系管理员。""",
            'en': """🔮 Tarot Prediction Bot User Guide

📋 Available Commands:
/start - Start using the bot
/daily - Get daily tarot guidance
/reading - Start tarot reading
/learn - Learn tarot knowledge
/language - Switch language
/help - Show this help

🎴 Reading Features:
• Single Card - Quick guidance
• Three Cards - Past, present, future
• Love Reading - Relationship guidance
• Career Reading - Work development advice
• Decision Reading - Important choice help

💡 Usage Tips:
• Clarify your question before reading
• Keep an open and honest mindset
• Use interpretations as reference and inspiration
• Final decisions are in your hands

Contact admin if you have any questions.""",
            'ru': """🔮 Руководство пользователя бота предсказаний Таро

📋 Доступные команды:
/start - Начать использование бота
/daily - Получить ежедневное руководство Таро
/reading - Начать расклад Таро
/learn - Изучить знания Таро
/language - Переключить язык
/help - Показать эту справку

🎴 Функции расклада:
• Одна карта - Быстрое руководство
• Три карты - Прошлое, настоящее, будущее
• Любовный расклад - Руководство по отношениям
• Карьерный расклад - Советы по развитию работы
• Расклад решений - Помощь в важном выборе

💡 Советы по использованию:
• Уточните свой вопрос перед раскладом
• Сохраняйте открытый и честный настрой
• Используйте толкования как справку и вдохновение
• Окончательные решения в ваших руках

Обращайтесь к администратору, если у вас есть вопросы."""
        },
        
        # 错误消息
        'error_api': {
            'zh': '抱歉，AI服务暂时不可用，请稍后再试。',
            'en': 'Sorry, AI service is temporarily unavailable, please try again later.',
            'ru': 'Извините, сервис ИИ временно недоступен, попробуйте позже.'
        },
        'error_rate_limit': {
            'zh': '你的请求过于频繁，请稍后再试。',
            'en': 'Your requests are too frequent, please try again later.',
            'ru': 'Ваши запросы слишком частые, попробуйте позже.'
        },
        'error_invalid_question': {
            'zh': '请输入有效的问题，或发送"跳过"进行通用占卜。',
            'en': 'Please enter a valid question, or send "skip" for general reading.',
            'ru': 'Пожалуйста, введите действительный вопрос или отправьте "пропустить" для общего расклада.'
        },
        'error_general': {
            'zh': '发生了未知错误，请稍后重试。',
            'en': 'An unknown error occurred, please try again later.',
            'ru': 'Произошла неизвестная ошибка, попробуйте позже.'
        }
    }
    
    # 牌阵名称
    SPREAD_NAMES = {
        'single': {
            'zh': '单张牌占卜',
            'en': 'Single Card Reading',
            'ru': 'Расклад одной карты'
        },
        'three_card': {
            'zh': '三张牌占卜',
            'en': 'Three Card Reading',
            'ru': 'Расклад трех карт'
        },
        'love': {
            'zh': '爱情占卜',
            'en': 'Love Reading',
            'ru': 'Любовный расклад'
        },
        'career': {
            'zh': '事业占卜',
            'en': 'Career Reading',
            'ru': 'Карьерный расклад'
        },
        'decision': {
            'zh': '决策占卜',
            'en': 'Decision Reading',
            'ru': 'Расклад для решений'
        }
    }
    
    # 牌阵位置含义
    SPREAD_POSITIONS = {
        'single_positions': {
            'zh': ['当前状况/指导'],
            'en': ['Current situation/guidance'],
            'ru': ['Текущая ситуация/руководство']
        },
        'three_card_positions': {
            'zh': ['过去/根源', '现在/当前状况', '未来/结果'],
            'en': ['Past/roots', 'Present/current situation', 'Future/outcome'],
            'ru': ['Прошлое/корни', 'Настоящее/текущая ситуация', 'Будущее/результат']
        },
        'love_positions': {
            'zh': ['你的感受', '对方的感受', '关系的未来'],
            'en': ['Your feelings', 'Their feelings', 'Relationship future'],
            'ru': ['Ваши чувства', 'Их чувства', 'Будущее отношений']
        },
        'career_positions': {
            'zh': ['当前工作状况', '挑战和机遇', '建议和方向'],
            'en': ['Current work situation', 'Challenges and opportunities', 'Advice and direction'],
            'ru': ['Текущая рабочая ситуация', 'Вызовы и возможности', 'Советы и направление']
        },
        'general_positions': {
            'zh': ['当前状况', '挑战', '指导建议'],
            'en': ['Current situation', 'Challenge', 'Guidance'],
            'ru': ['Текущая ситуация', 'Вызов', 'Руководство']
        },
        'decision_positions': {
            'zh': ['选项A的结果', '选项B的结果', '最佳选择'],
            'en': ['Option A outcome', 'Option B outcome', 'Best choice'],
            'ru': ['Результат варианта А', 'Результат варианта Б', 'Лучший выбор']
        }
    }
    
    # AI 提示词模板（多语言）
    AI_PROMPTS = {
        'system_prompt': {
            'zh': '你是一位经验丰富的塔罗牌占卜师，擅长解读塔罗牌的含义并提供深刻的人生指导。你的解读应该富有洞察力、温暖且具有启发性。请用中文回答。',
            'en': 'You are an experienced tarot card reader, skilled at interpreting tarot meanings and providing profound life guidance. Your readings should be insightful, warm, and inspiring. Please respond in English.',
            'ru': 'Вы опытный читатель карт Таро, умеющий толковать значения Таро и давать глубокие жизненные советы. Ваши толкования должны быть проницательными, теплыми и вдохновляющими. Пожалуйста, отвечайте на русском языке.'
        },
        'reading_prompt': {
            'zh': '请为以下塔罗牌抽牌结果提供详细解读：',
            'en': 'Please provide a detailed reading for the following tarot card draw:',
            'ru': 'Пожалуйста, предоставьте подробное толкование для следующего расклада карт Таро:'
        },
        'question_label': {
            'zh': '问题',
            'en': 'Question',
            'ru': 'Вопрос'
        },
        'spread_label': {
            'zh': '牌阵类型',
            'en': 'Spread type',
            'ru': 'Тип расклада'
        },
        'cards_label': {
            'zh': '抽取的牌',
            'en': 'Drawn cards',
            'ru': 'Вытянутые карты'
        },
        'position_label': {
            'zh': '位置含义',
            'en': 'Position meaning',
            'ru': 'Значение позиции'
        },
        'reading_requirements': {
            'zh': '请提供：\n1. 整体解读和主要信息\n2. 每张牌在其位置上的具体含义\n3. 牌与牌之间的关联和互动\n4. 针对问题的具体建议和指导\n5. 总结和未来展望',
            'en': 'Please provide:\n1. Overall reading and main information\n2. Specific meaning of each card in its position\n3. Connections and interactions between cards\n4. Specific advice and guidance for the question\n5. Summary and future outlook',
            'ru': 'Пожалуйста, предоставьте:\n1. Общее толкование и основную информацию\n2. Конкретное значение каждой карты в её позиции\n3. Связи и взаимодействия между картами\n4. Конкретные советы и руководство по вопросу\n5. Резюме и перспективы на будущее'
        },
        'closing_instruction': {
            'zh': '请用温暖、富有洞察力的语调，提供深刻而实用的指导。',
            'en': 'Please use a warm, insightful tone to provide profound and practical guidance.',
            'ru': 'Пожалуйста, используйте теплый, проницательный тон для предоставления глубокого и практического руководства.'
        },
        'daily_prompt': {
            'zh': '请为今日塔罗牌 "{card_name}" 提供每日指导。\n\n牌的含义: {card_meaning}\n\n请提供:\n1. 今日的主要能量和主题\n2. 需要注意的事项\n3. 积极的行动建议\n4. 简短的鼓励话语\n\n请保持简洁而富有启发性，适合作为每日指导。',
            'en': 'Please provide daily guidance for today\'s tarot card "{card_name}".\n\nCard meaning: {card_meaning}\n\nPlease provide:\n1. Today\'s main energy and theme\n2. Things to pay attention to\n3. Positive action suggestions\n4. Brief encouraging words\n\nPlease keep it concise and inspiring, suitable as daily guidance.',
            'ru': 'Пожалуйста, предоставьте ежедневное руководство для сегодняшней карты Таро "{card_name}".\n\nЗначение карты: {card_meaning}\n\nПожалуйста, предоставьте:\n1. Основную энергию и тему сегодняшнего дня\n2. На что обратить внимание\n3. Позитивные предложения по действиям\n4. Краткие ободряющие слова\n\nПожалуйста, будьте лаконичны и вдохновляющи, подходящими в качестве ежедневного руководства.'
        },
        'daily_system': {
            'zh': '你是一位温暖的塔罗牌指导师，擅长提供简洁而深刻的每日指导。',
            'en': 'You are a warm tarot guide, skilled at providing concise yet profound daily guidance.',
            'ru': 'Вы теплый гид по Таро, умеющий давать краткие, но глубокие ежедневные советы.'
        },
        'explanation_prompt': {
            'zh': '请详细解释塔罗牌 "{card_name}" 的含义和象征。\n\n基本信息:\n{basic_info}\n\n请提供:\n1. 牌的核心象征意义\n2. 在不同生活领域的应用\n3. 正位和逆位的区别(如适用)\n4. 实际生活中的指导意义\n\n请用易懂的语言解释，帮助理解这张牌的深层含义。',
            'en': 'Please explain in detail the meaning and symbolism of the tarot card "{card_name}".\n\nBasic information:\n{basic_info}\n\nPlease provide:\n1. Core symbolic meaning of the card\n2. Applications in different life areas\n3. Differences between upright and reversed (if applicable)\n4. Practical life guidance meaning\n\nPlease explain in understandable language to help understand the deep meaning of this card.',
            'ru': 'Пожалуйста, подробно объясните значение и символизм карты Таро "{card_name}".\n\nОсновная информация:\n{basic_info}\n\nПожалуйста, предоставьте:\n1. Основное символическое значение карты\n2. Применение в различных сферах жизни\n3. Различия между прямым и обратным положением (если применимо)\n4. Практическое жизненное значение руководства\n\nПожалуйста, объясните понятным языком, чтобы помочь понять глубокий смысл этой карты.'
        },
        'explanation_system': {
            'zh': '你是一位塔罗牌专家，擅长用简单易懂的方式解释塔罗牌的含义。',
            'en': 'You are a tarot expert, skilled at explaining tarot card meanings in simple and understandable ways.',
            'ru': 'Вы эксперт по Таро, умеющий объяснять значения карт Таро простым и понятным способом.'
        },
        'major_arcana': {
            'zh': '大阿卡纳',
            'en': 'Major Arcana',
            'ru': 'Старшие Арканы'
        },
        'minor_arcana': {
            'zh': '小阿卡纳',
            'en': 'Minor Arcana',
            'ru': 'Младшие Арканы'
        },
        'card_name_label': {
            'zh': '牌名',
            'en': 'Card name',
            'ru': 'Название карты'
        },
        'card_type_label': {
            'zh': '类型',
            'en': 'Type',
            'ru': 'Тип'
        },
        'upright_meaning_label': {
            'zh': '正位含义',
            'en': 'Upright meaning',
            'ru': 'Прямое значение'
        },
        'reversed_meaning_label': {
            'zh': '逆位含义',
            'en': 'Reversed meaning',
            'ru': 'Обратное значение'
        },
        'description_label': {
            'zh': '描述',
            'en': 'Description',
            'ru': 'Описание'
        },
        'suit_label': {
            'zh': '花色',
            'en': 'Suit',
            'ru': 'Масть'
        },
        'element_label': {
            'zh': '元素',
            'en': 'Element',
            'ru': 'Элемент'
        },
        'meaning_label': {
            'zh': '含义',
            'en': 'Meaning',
            'ru': 'Значение'
        }
    }
    
    @classmethod
    def get_text(cls, key: str, language: str = None, **kwargs) -> str:
        """获取指定语言的文本"""
        if language is None:
            language = cls.DEFAULT_LANGUAGE
        
        if language not in cls.SUPPORTED_LANGUAGES:
            language = cls.DEFAULT_LANGUAGE
        
        text_dict = cls.TEXTS.get(key, {})
        text = text_dict.get(language, text_dict.get(cls.DEFAULT_LANGUAGE, key))
        
        # 格式化文本
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        return text
    
    @classmethod
    def get_spread_name(cls, spread_type: str, language: str = None) -> str:
        """获取牌阵名称"""
        if language is None:
            language = cls.DEFAULT_LANGUAGE
        
        spread_dict = cls.SPREAD_NAMES.get(spread_type, {})
        return spread_dict.get(language, spread_dict.get(cls.DEFAULT_LANGUAGE, spread_type))
    
    @classmethod
    def get_ai_prompt(cls, prompt_type: str, language: str = None) -> str:
        """获取AI提示词"""
        if language is None:
            language = cls.DEFAULT_LANGUAGE
        
        prompt_dict = cls.AI_PROMPTS.get(prompt_type, {})
        return prompt_dict.get(language, prompt_dict.get(cls.DEFAULT_LANGUAGE, ''))

# 创建全局实例
languages = Languages()