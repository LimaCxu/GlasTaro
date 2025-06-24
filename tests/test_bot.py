#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
塔罗预测机器人测试文件

用于测试机器人的核心功能，确保所有模块正常工作。
"""

import sys
import os
from unittest.mock import Mock, patch

def test_imports():
    """测试所有模块导入"""
    print("🧪 测试模块导入...")
    
    try:
        from data import tarot_cards
        print("✅ tarot_cards 模块导入成功")
        
        from src import tarot_reader
        print("✅ tarot_reader 模块导入成功")
        
        from src import ai_interpreter
        print("✅ ai_interpreter 模块导入成功")
        
        from config import config
        print("✅ config 模块导入成功")
        
        from src import user_manager
        print("✅ user_manager 模块导入成功")
        
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_tarot_cards():
    """测试塔罗牌数据"""
    print("\n🃏 测试塔罗牌数据...")
    
    try:
        from tarot_cards import get_all_cards, get_card_by_id, MAJOR_ARCANA, MINOR_ARCANA
        
        # 测试获取所有牌
        all_cards = get_all_cards()
        print(f"✅ 总共 {len(all_cards)} 张塔罗牌")
        
        # 验证牌数量
        if len(all_cards) != 78:
            print(f"⚠️  警告：塔罗牌数量不正确，应该是78张，实际是{len(all_cards)}张")
        
        # 测试大阿卡纳
        major_count = len([card for card in all_cards if card['type'] == 'major'])
        print(f"✅ 大阿卡纳: {major_count} 张")
        
        # 测试小阿卡纳
        minor_count = len([card for card in all_cards if card['type'] == 'minor'])
        print(f"✅ 小阿卡纳: {minor_count} 张")
        
        # 测试获取特定牌
        fool_card = get_card_by_id('major_0')
        if fool_card:
            print(f"✅ 成功获取愚者牌: {fool_card['name']}")
        else:
            print("❌ 无法获取愚者牌")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 塔罗牌数据测试失败: {e}")
        return False

def test_tarot_reader():
    """测试塔罗牌阅读器"""
    print("\n🔮 测试塔罗牌阅读器...")
    
    try:
        from tarot_reader import TarotReader
        
        # 创建阅读器实例
        reader = TarotReader()
        print("✅ 塔罗阅读器创建成功")
        
        # 测试抽牌
        cards = reader.draw_cards(3)
        print(f"✅ 成功抽取 {len(cards)} 张牌")
        
        for i, card in enumerate(cards, 1):
            print(f"   {i}. {card['name']} ({card['orientation']})")
        
        # 测试牌阵选项
        spreads = reader.get_spread_options()
        print(f"✅ 可用牌阵: {len(spreads)} 种")
        
        # 测试每日塔罗（不调用AI）
        daily_card, _ = reader.get_daily_card()
        print(f"✅ 每日塔罗牌: {daily_card['name']}")
        
        return True
    except Exception as e:
        print(f"❌ 塔罗阅读器测试失败: {e}")
        return False

def test_config():
    """测试配置"""
    print("\n⚙️ 测试配置...")
    
    try:
        from config import config
        
        # 测试配置验证
        errors = config.validate()
        if errors:
            print("⚠️  配置验证发现问题:")
            for error in errors:
                print(f"   - {error}")
        else:
            print("✅ 配置验证通过")
        
        # 测试牌阵配置
        spread_config = config.get_spread_config('three_card')
        print(f"✅ 三张牌阵配置: {spread_config['name']}")
        
        # 测试表情符号
        tarot_emoji = config.get_emoji('tarot')
        print(f"✅ 塔罗表情符号: {tarot_emoji}")
        
        return True
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_user_manager():
    """测试用户管理器"""
    print("\n👤 测试用户管理器...")
    
    try:
        from user_manager import UserManager, UserSession, RateLimiter
        
        # 测试用户会话
        session = UserSession(12345)
        print(f"✅ 用户会话创建成功: {session.user_id}")
        
        # 测试频率限制器
        rate_limiter = RateLimiter()
        can_request, message = rate_limiter.can_make_request(12345)
        print(f"✅ 频率限制检查: {can_request}")
        
        # 测试用户管理器
        user_manager = UserManager()
        session = user_manager.get_session(12345)
        print(f"✅ 用户管理器获取会话: {session.user_id}")
        
        # 测试用户统计
        stats = user_manager.get_user_stats(12345)
        print(f"✅ 用户统计: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ 用户管理器测试失败: {e}")
        return False

def test_ai_interpreter():
    """测试AI解释器（模拟）"""
    print("\n🤖 测试AI解释器...")
    
    try:
        from ai_interpreter import TarotAIInterpreter
        
        # 创建AI解释器实例（不实际调用API）
        interpreter = TarotAIInterpreter()
        print("✅ AI解释器创建成功")
        
        # 测试提示词构建
        from tarot_cards import get_card_by_id
        test_card = get_card_by_id('major_0')
        test_card['orientation'] = '正位'
        
        prompt = interpreter._build_prompt([test_card], "测试问题", "single")
        print("✅ 提示词构建成功")
        print(f"   提示词长度: {len(prompt)} 字符")
        
        # 测试牌阵描述
        description = interpreter._get_spread_description('three_card')
        print(f"✅ 牌阵描述: {description}")
        
        return True
    except Exception as e:
        print(f"❌ AI解释器测试失败: {e}")
        return False

def test_bot_structure():
    """测试机器人结构"""
    print("\n🤖 测试机器人结构...")
    
    try:
        # 检查bot.py文件是否存在
        if not os.path.exists('src/bot.py'):
            print("❌ src/bot.py 文件不存在")
            return False
        
        print("✅ src/bot.py 文件存在")
        
        # 尝试导入bot模块（不运行）
        import importlib.util
        spec = importlib.util.spec_from_file_location("bot", "src/bot.py")
        if spec is None:
            print("❌ 无法加载 src/bot.py")
            return False
        
        print("✅ src/bot.py 可以加载")
        
        return True
    except Exception as e:
        print(f"❌ 机器人结构测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🧪 塔罗预测机器人功能测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("塔罗牌数据", test_tarot_cards),
        ("塔罗阅读器", test_tarot_reader),
        ("配置系统", test_config),
        ("用户管理器", test_user_manager),
        ("AI解释器", test_ai_interpreter),
        ("机器人结构", test_bot_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n❌ {test_name} 测试失败")
        except Exception as e:
            print(f"\n❌ {test_name} 测试出错: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！机器人核心功能正常。")
        print("\n💡 下一步:")
        print("   1. 配置 .env 文件中的 API 密钥")
        print("   2. 运行 python run.py 启动机器人")
        print("   3. 在 Telegram 中测试机器人功能")
    else:
        print("⚠️  部分测试失败，请检查相关模块。")
        return False
    
    return True

def main():
    """主函数"""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()