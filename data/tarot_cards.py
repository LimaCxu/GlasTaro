# -*- coding: utf-8 -*-
"""
塔罗牌数据文件
包含78张塔罗牌的基本信息和含义

作者: Lima
"""

# 大阿卡纳牌 (22张)
MAJOR_ARCANA = {
    0: {
        'id': 'major_0',
        'name': '愚者',
        'name_en': 'The Fool',
        'name_ru': 'Дурак',
        'type': 'major',
        'number': 0,
        'upright_meaning': '新开始、冒险、天真、自由',
        'reversed_meaning': '鲁莽、缺乏计划、愚蠢决定',
        'description': '代表新的开始和无限可能',
        'keywords': ['新开始', '冒险', '天真', '潜力']
    },
    1: {
        'id': 'major_1',
        'name': '魔术师',
        'name_en': 'The Magician',
        'name_ru': 'Маг',
        'type': 'major',
        'number': 1,
        'upright_meaning': '意志力、技能、专注、创造',
        'reversed_meaning': '缺乏专注、操控、欺骗',
        'description': '代表意志力和创造能力',
        'keywords': ['意志力', '技能', '专注', '创造']
    },
    2: {
        'id': 'major_2',
        'name': '女祭司',
        'name_en': 'The High Priestess',
        'name_ru': 'Верховная Жрица',
        'type': 'major',
        'number': 2,
        'upright_meaning': '直觉、神秘、内在智慧、潜意识',
        'reversed_meaning': '缺乏直觉、秘密、隐瞒',
        'description': '代表直觉和内在智慧',
        'keywords': ['直觉', '神秘', '智慧', '潜意识']
    },
    3: {
        'id': 'major_3',
        'name': '女皇',
        'name_en': 'The Empress',
        'name_ru': 'Императрица',
        'type': 'major',
        'number': 3,
        'upright_meaning': '丰饶、母性、创造力、自然',
        'reversed_meaning': '依赖、缺乏成长、创造力受阻',
        'description': '代表丰饶和母性能量',
        'keywords': ['丰饶', '母性', '创造力', '自然']
    },
    4: {
        'id': 'major_4',
        'name': '皇帝',
        'name_en': 'The Emperor',
        'name_ru': 'Император',
        'type': 'major',
        'number': 4,
        'upright_meaning': '权威、结构、控制、父性',
        'reversed_meaning': '专制、缺乏纪律、不负责任',
        'description': '代表权威和领导力',
        'keywords': ['权威', '结构', '控制', '领导']
    },
    5: {
        'id': 'major_5',
        'name': '教皇',
        'name_en': 'The Hierophant',
        'name_ru': 'Иерофант',
        'type': 'major',
        'number': 5,
        'upright_meaning': '传统、精神指导、宗教、教育',
        'reversed_meaning': '叛逆、非传统、灵性探索',
        'description': '代表传统和精神指导',
        'keywords': ['传统', '指导', '宗教', '教育']
    },
    6: {
        'id': 'major_6',
        'name': '恋人',
        'name_en': 'The Lovers',
        'name_ru': 'Влюбленные',
        'type': 'major',
        'number': 6,
        'upright_meaning': '爱情、关系、选择、和谐',
        'reversed_meaning': '关系问题、错误选择、不和谐',
        'description': '代表爱情和重要选择',
        'keywords': ['爱情', '关系', '选择', '和谐']
    },
    7: {
        'id': 'major_7',
        'name': '战车',
        'name_en': 'The Chariot',
        'name_ru': 'Колесница',
        'type': 'major',
        'number': 7,
        'upright_meaning': '胜利、意志力、控制、决心',
        'reversed_meaning': '缺乏控制、失败、缺乏方向',
        'description': '代表胜利和意志力',
        'keywords': ['胜利', '意志力', '控制', '决心']
    },
    8: {
        'id': 'major_8',
        'name': '力量',
        'name_en': 'Strength',
        'name_ru': 'Сила',
        'type': 'major',
        'number': 8,
        'upright_meaning': '内在力量、勇气、耐心、控制',
        'reversed_meaning': '缺乏信心、自我怀疑、缺乏控制',
        'description': '代表内在力量和勇气',
        'keywords': ['力量', '勇气', '耐心', '控制']
    },
    9: {
        'id': 'major_9',
        'name': '隐者',
        'name_en': 'The Hermit',
        'name_ru': 'Отшельник',
        'type': 'major',
        'number': 9,
        'upright_meaning': '内省、寻找、指导、智慧',
        'reversed_meaning': '孤立、迷失、拒绝指导',
        'description': '代表内省和寻找智慧',
        'keywords': ['内省', '寻找', '指导', '智慧']
    },
    10: {
        'id': 'major_10',
        'name': '命运之轮',
        'name_en': 'Wheel of Fortune',
        'name_ru': 'Колесо Фортуны',
        'type': 'major',
        'number': 10,
        'upright_meaning': '命运、机会、变化、循环',
        'reversed_meaning': '厄运、缺乏控制、破坏性变化',
        'description': '代表命运和变化',
        'keywords': ['命运', '机会', '变化', '循环']
    }
    # 这里可以继续添加其他大阿卡纳牌...
}

# 小阿卡纳牌 (56张) - 简化版
MINOR_ARCANA = {
    'wands': {
        'name': '权杖',
        'name_en': 'Wands',
        'name_ru': 'Жезлы',
        'element': '火',
        'cards': {
            'ace': {
                'id': 'wands_ace',
                'name': '权杖王牌',
                'name_en': 'Ace of Wands',
                'name_ru': 'Туз Жезлов',
                'type': 'minor',
                'meaning': '新开始、创意、灵感、潜力',
                'keywords': ['新开始', '创意', '灵感']
            },
            'two': {
                'id': 'wands_two',
                'name': '权杖二',
                'name_en': 'Two of Wands',
                'name_ru': 'Двойка Жезлов',
                'type': 'minor',
                'meaning': '规划、远见、个人力量',
                'keywords': ['规划', '远见', '力量']
            },
            'three': {
                'id': 'wands_three',
                'name': '权杖三',
                'name_en': 'Three of Wands',
                'name_ru': 'Тройка Жезлов',
                'type': 'minor',
                'meaning': '扩张、远见、领导力',
                'keywords': ['扩张', '远见', '领导']
            }
            # 可以继续添加更多权杖牌...
        }
    },
    'cups': {
        'name': '圣杯',
        'name_en': 'Cups',
        'name_ru': 'Кубки',
        'element': '水',
        'cards': {
            'ace': {
                'id': 'cups_ace',
                'name': '圣杯王牌',
                'name_en': 'Ace of Cups',
                'name_ru': 'Туз Кубков',
                'type': 'minor',
                'meaning': '新的感情、直觉、灵性',
                'keywords': ['感情', '直觉', '灵性']
            }
            # 可以继续添加更多圣杯牌...
        }
    },
    'swords': {
        'name': '宝剑',
        'name_en': 'Swords',
        'name_ru': 'Мечи',
        'element': '风',
        'cards': {
            'ace': {
                'id': 'swords_ace',
                'name': '宝剑王牌',
                'name_en': 'Ace of Swords',
                'name_ru': 'Туз Мечей',
                'type': 'minor',
                'meaning': '新思想、清晰、真理',
                'keywords': ['思想', '清晰', '真理']
            }
            # 可以继续添加更多宝剑牌...
        }
    },
    'pentacles': {
        'name': '星币',
        'name_en': 'Pentacles',
        'name_ru': 'Пентакли',
        'element': '土',
        'cards': {
            'ace': {
                'id': 'pentacles_ace',
                'name': '星币王牌',
                'name_en': 'Ace of Pentacles',
                'name_ru': 'Туз Пентаклей',
                'type': 'minor',
                'meaning': '新机会、物质成功、繁荣',
                'keywords': ['机会', '成功', '繁荣']
            }
            # 可以继续添加更多星币牌...
        }
    }
}

def get_all_cards():
    """
    获取所有塔罗牌的列表
    
    Returns:
        List[Dict]: 所有塔罗牌的列表
    """
    all_cards = []
    
    # 添加大阿卡纳牌
    for card_data in MAJOR_ARCANA.values():
        all_cards.append(card_data)
    
    # 添加小阿卡纳牌
    for suit_data in MINOR_ARCANA.values():
        for card_data in suit_data['cards'].values():
            card_data['suit'] = suit_data['name']
            card_data['element'] = suit_data['element']
            all_cards.append(card_data)
    
    return all_cards

def get_card_by_id(card_id: str):
    """
    根据ID获取特定的塔罗牌
    
    Args:
        card_id: 塔罗牌ID
        
    Returns:
        Dict: 塔罗牌数据，如果未找到返回None
    """
    # 搜索大阿卡纳
    for card in MAJOR_ARCANA.values():
        if card['id'] == card_id:
            return card
    
    # 搜索小阿卡纳
    for suit_data in MINOR_ARCANA.values():
        for card in suit_data['cards'].values():
            if card['id'] == card_id:
                card_copy = card.copy()
                card_copy['suit'] = suit_data['name']
                card_copy['element'] = suit_data['element']
                return card_copy
    
    return None

def get_major_arcana():
    """获取所有大阿卡纳牌"""
    return list(MAJOR_ARCANA.values())

def get_minor_arcana():
    """获取所有小阿卡纳牌"""
    minor_cards = []
    for suit_data in MINOR_ARCANA.values():
        for card_data in suit_data['cards'].values():
            card_copy = card_data.copy()
            card_copy['suit'] = suit_data['name']
            card_copy['element'] = suit_data['element']
            minor_cards.append(card_copy)
    return minor_cards

def get_cards_by_suit(suit_name: str):
    """
    根据花色获取牌
    
    Args:
        suit_name: 花色名称 (wands, cups, swords, pentacles)
        
    Returns:
        List[Dict]: 该花色的所有牌
    """
    if suit_name in MINOR_ARCANA:
        suit_data = MINOR_ARCANA[suit_name]
        cards = []
        for card_data in suit_data['cards'].values():
            card_copy = card_data.copy()
            card_copy['suit'] = suit_data['name']
            card_copy['element'] = suit_data['element']
            cards.append(card_copy)
        return cards
    return []

# 为了兼容性，提供一些常用的数据结构
def get_card_count():
    """获取塔罗牌总数"""
    return len(MAJOR_ARCANA) + sum(len(suit['cards']) for suit in MINOR_ARCANA.values())

# 简单的测试函数
if __name__ == "__main__":
    print(f"🎴 塔罗牌数据加载测试")
    print(f"📊 大阿卡纳: {len(MAJOR_ARCANA)}张")
    print(f"📊 小阿卡纳: {sum(len(suit['cards']) for suit in MINOR_ARCANA.values())}张")
    print(f"📊 总计: {get_card_count()}张")
    
    # 测试获取所有牌
    all_cards = get_all_cards()
    print(f"✅ 成功加载 {len(all_cards)} 张塔罗牌")
    
    # 测试获取单张牌
    fool_card = get_card_by_id('major_0')
    if fool_card:
        print(f"✅ 测试获取单张牌: {fool_card['name']}")
    else:
        print("❌ 获取单张牌失败")
