#!/usr/bin/env python3
"""
测试AI模型切换功能

这个脚本用于测试不同AI模型的配置和切换功能。
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import Config
from src.ai_interpreter import TarotAIInterpreter

def test_model_configuration():
    """测试模型配置"""
    print("🔧 测试AI模型配置...")
    print(f"当前配置的AI模型: {Config.AI_MODEL}")
    
    if Config.AI_MODEL.startswith('gpt'):
        print(f"OpenAI模型: {Config.OPENAI_MODEL}")
        print(f"OpenAI API Key: {'已配置' if Config.OPENAI_API_KEY else '未配置'}")
        print(f"最大Token数: {Config.OPENAI_MAX_TOKENS}")
        print(f"温度参数: {Config.OPENAI_TEMPERATURE}")
    elif Config.AI_MODEL == 'deepseek-chat':
        print(f"DeepSeek模型: {Config.DEEPSEEK_MODEL}")
        print(f"DeepSeek API Key: {'已配置' if Config.DEEPSEEK_API_KEY else '未配置'}")
        print(f"DeepSeek Base URL: {Config.DEEPSEEK_BASE_URL}")
        print(f"最大Token数: {Config.DEEPSEEK_MAX_TOKENS}")
        print(f"温度参数: {Config.DEEPSEEK_TEMPERATURE}")
    
    print()

def test_ai_interpreter_initialization():
    """测试AI解释器初始化"""
    print("🤖 测试AI解释器初始化...")
    
    try:
        interpreter = TarotAIInterpreter()
        print(f"✅ AI解释器初始化成功")
        print(f"使用模型: {interpreter.model}")
        print(f"最大Token数: {interpreter.max_tokens}")
        print(f"温度参数: {interpreter.temperature}")
        return interpreter
    except Exception as e:
        print(f"❌ AI解释器初始化失败: {e}")
        return None

def test_simple_generation(interpreter):
    """测试简单的文本生成"""
    if not interpreter:
        print("⚠️ 跳过文本生成测试（解释器未初始化）")
        return
    
    print("📝 测试简单文本生成...")
    
    # 创建一个简单的测试卡牌
    test_card = {
        'name': '愚者',
        'type': 'major',
        'orientation': '正位',
        'upright_meaning': '新的开始，冒险精神，纯真',
        'description': '愚者代表新的开始和无限的可能性'
    }
    
    try:
        # 测试每日指导生成
        guidance = interpreter.generate_daily_guidance(test_card)
        print(f"✅ 每日指导生成成功")
        print(f"生成内容长度: {len(guidance)} 字符")
        print(f"内容预览: {guidance[:100]}...")
    except Exception as e:
        print(f"❌ 每日指导生成失败: {e}")

def main():
    """主函数"""
    print("🔮 塔罗机器人 - AI模型切换测试")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    
    # 验证配置
    errors = Config.validate()
    if errors:
        print("❌ 配置验证失败:")
        for error in errors:
            print(f"   - {error}")
        print("\n请检查 .env 文件配置")
        return
    
    print("✅ 配置验证通过")
    print()
    
    # 测试配置
    test_model_configuration()
    
    # 测试初始化
    interpreter = test_ai_interpreter_initialization()
    print()
    
    # 测试文本生成（如果有有效的API密钥）
    if interpreter:
        test_simple_generation(interpreter)
    
    print("\n🎉 测试完成！")
    print("\n💡 提示:")
    print("   - 要切换模型，请修改 .env 文件中的 AI_MODEL 参数")
    print("   - 支持的模型: gpt-3.5-turbo, gpt-4, deepseek-chat")
    print("   - 确保相应的API密钥已正确配置")

if __name__ == "__main__":
    main()