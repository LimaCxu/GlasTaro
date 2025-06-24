#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
塔罗预测机器人启动脚本

这个脚本提供了一个简单的方式来启动塔罗机器人，
包含基本的错误检查和环境验证。
"""

import os
import sys
from pathlib import Path

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查 Python 版本
    if sys.version_info < (3, 8):
        print("❌ 错误：需要 Python 3.8 或更高版本")
        print(f"   当前版本：{sys.version}")
        return False
    
    print(f"✅ Python 版本：{sys.version.split()[0]}")
    
    # 检查必要文件
    required_files = [
        'src/bot.py', 
        'src/tarot_reader.py', 
        'data/tarot_cards.py', 
        'src/ai_interpreter.py',
        'config/config.py'
    ]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ 错误：缺少必要文件 {file}")
            return False
    
    print("✅ 所有必要文件存在")
    
    # 检查 .env 文件
    if not Path('.env').exists():
        print("⚠️  警告：未找到 .env 文件")
        print("   请复制 config/.env.example 为 .env 并配置必要的环境变量")
        return False
    
    print("✅ 环境配置文件存在")
    
    return True

def check_dependencies():
    """检查依赖包"""
    print("\n📦 检查依赖包...")
    
    required_packages = [
        'telegram',
        'openai',
        'python-dotenv',
        'requests',
        'aiohttp'
    ]
    
    missing_packages = []

    
    return True

def check_env_variables():
    """检查环境变量"""
    print("\n🔑 检查环境变量...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'TELEGRAM_BOT_TOKEN': 'Telegram Bot Token',
        'OPENAI_API_KEY': 'OpenAI API Key'
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"❌ {description} ({var})")
            missing_vars.append(var)
        else:
            # 只显示前几个字符，保护隐私
            masked_value = value[:8] + '...' if len(value) > 8 else value
            print(f"✅ {description}: {masked_value}")
    
    if missing_vars:
        print(f"\n❌ 缺少以下环境变量：{', '.join(missing_vars)}")
        print("请在 .env 文件中配置这些变量")
        return False
    
    return True

def main():
    """主函数"""
    print("🔮 塔罗预测机器人启动器")
    print("=" * 40)
    
    # 环境检查
    if not check_environment():
        print("\n❌ 环境检查失败，请修复上述问题后重试")
        sys.exit(1)
    
    # 依赖检查
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请安装缺少的包")
        sys.exit(1)
    
    # 环境变量检查
    if not check_env_variables():
        print("\n❌ 环境变量检查失败，请配置必要的变量")
        sys.exit(1)
    
    print("\n✅ 所有检查通过！")
    print("🚀 启动塔罗预测机器人...")
    print("=" * 40)
    
    try:
        # 使用main.py作为入口点
        import main
        main.main()
    except KeyboardInterrupt:
        print("\n\n👋 机器人已停止运行")
    except Exception as e:
        print(f"\n❌ 运行时错误：{e}")
        print("请检查配置和网络连接")
        sys.exit(1)

if __name__ == '__main__':
    main()