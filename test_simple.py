#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.language_manager import language_manager
from config.languages import languages

def test_spread_names():
    print("=== 测试牌阵名称 ===")
    test_user_id = 123456789
    spreads = ['single', 'three_card', 'love']
    languages_list = ['zh', 'en', 'ru']
    
    for spread in spreads:
        print(f"\n牌阵类型: {spread}")
        for lang in languages_list:
            language_manager.set_user_language(test_user_id, lang)
            name = language_manager.get_spread_name(spread, test_user_id)
            print(f"  {lang}: {name}")

def test_ai_prompts():
    print("\n=== 测试AI提示词 ===")
    test_user_id = 123456789
    prompts = ['system_prompt', 'reading_prompt']
    languages_list = ['zh', 'en', 'ru']
    
    for prompt in prompts:
        print(f"\n提示词类型: {prompt}")
        for lang in languages_list:
            language_manager.set_user_language(test_user_id, lang)
            text = language_manager.get_ai_prompt(prompt, test_user_id)
            print(f"  {lang}: {text[:50]}..." if len(text) > 50 else f"  {lang}: {text}")

if __name__ == "__main__":
    test_spread_names()
    test_ai_prompts()
    print("\n=== 测试完成 ===")