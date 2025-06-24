#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多语言功能测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.language_manager import language_manager
from config.languages import languages

def test_language_manager():
    """测试语言管理器功能"""
    print("=== 测试语言管理器功能 ===")
    
    # 测试支持的语言
    supported_langs = language_manager.get_supported_languages()
    print(f"支持的语言: {supported_langs}")
    
    # 测试设置用户语言
    test_user_id = "test_user_123"
    
    # 测试中文
    language_manager.set_user_language(test_user_id, 'zh')
    user_lang = language_manager.get_user_language(test_user_id)
    print(f"用户语言设置为中文: {user_lang}")
    
    # 测试获取文本
    welcome_text = language_manager.get_text('welcome', test_user_id)
    print(f"中文欢迎文本: {welcome_text}")
    
    # 测试英文
    language_manager.set_user_language(test_user_id, 'en')
    user_lang = language_manager.get_user_language(test_user_id)
    print(f"用户语言设置为英文: {user_lang}")
    
    welcome_text = language_manager.get_text('welcome', test_user_id)
    print(f"英文欢迎文本: {welcome_text}")
    
    # 测试俄文
    language_manager.set_user_language(test_user_id, 'ru')
    user_lang = language_manager.get_user_language(test_user_id)
    print(f"用户语言设置为俄文: {user_lang}")
    
    welcome_text = language_manager.get_text('welcome', test_user_id)
    print(f"俄文欢迎文本: {welcome_text}")

def test_spread_names():
    """测试牌阵名称"""
    print("\n=== 测试牌阵名称 ===")
    
    spreads = ['single', 'three_card', 'love', 'career', 'decision']
    languages_list = ['zh', 'en', 'ru']
    
    for spread in spreads:
        print(f"\n牌阵类型: {spread}")
        for lang in languages_list:
            name = language_manager.get_spread_name(spread, lang)
            print(f"  {lang}: {name}")

def test_ai_prompts():
    """测试AI提示词"""
    print("\n=== 测试AI提示词 ===")
    
    prompts = ['system_prompt', 'reading_prompt', 'daily_prompt']
    languages_list = ['zh', 'en', 'ru']
    
    for prompt in prompts:
        print(f"\n提示词类型: {prompt}")
        for lang in languages_list:
            text = language_manager.get_ai_prompt(prompt, lang)
            print(f"  {lang}: {text[:100]}..." if len(text) > 100 else f"  {lang}: {text}")

def test_position_meanings():
    """测试牌阵位置含义"""
    print("\n=== 测试牌阵位置含义 ===")
    
    positions = ['single_positions', 'three_card_positions', 'love_positions']
    languages_list = ['zh', 'en', 'ru']
    
    for position in positions:
        print(f"\n位置类型: {position}")
        for lang in languages_list:
            meanings = languages.SPREAD_POSITIONS.get(position, {}).get(lang, [])
            print(f"  {lang}: {meanings}")

def test_menu_texts():
    """测试菜单文本"""
    print("\n=== 测试菜单文本 ===")
    
    menu_keys = ['main_menu_reading', 'main_menu_daily', 'main_menu_learning', 'main_menu_help']
    languages_list = ['zh', 'en', 'ru']
    
    for key in menu_keys:
        print(f"\n菜单项: {key}")
        for lang in languages_list:
            text = languages.get_text(key, lang)
            print(f"  {lang}: {text}")

if __name__ == "__main__":
    try:
        test_language_manager()
        test_spread_names()
        test_ai_prompts()
        test_position_meanings()
        test_menu_texts()
        print("\n=== 所有测试完成 ===")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()