#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Глас Таро 智能启动脚本
带完整环境检查的启动器，推荐新手使用

作者: Lima
用途: 环境检查 + 智能启动（推荐开发和首次使用）
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    
    if sys.version_info < (3, 8):
        print(f"❌ Python版本过低: {sys.version.split()[0]}")
        print("   需要Python 3.8+")
        return False
    
    print(f"✅ Python版本: {sys.version.split()[0]}")
    return True

def check_project_files():
    """检查项目文件完整性"""
    print("\n📁 检查项目文件...")
    
    required_files = [
        'src/bot.py',
        'src/tarot_reader.py', 
        'src/ai_interpreter.py',
        'core/config.py',
        'app.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少关键文件:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ 项目文件完整")
    return True

def check_env_file():
    """检查环境配置文件"""
    print("\n🔧 检查环境配置...")
    
    if not Path('.env').exists():
        print("❌ 未找到 .env 配置文件")
        print("💡 解决方案:")
        print("   1. 运行 'python setup_env.py' 创建配置")
        print("   2. 或手动创建 .env 文件")
        return False
    
    print("✅ 环境配置文件存在")
    return True

def check_dependencies():
    """检查关键依赖包"""
    print("\n📦 检查依赖包...")
    
    critical_packages = {
        'telegram': 'python-telegram-bot',
        'openai': 'openai',
        'fastapi': 'fastapi',
        'dotenv': 'python-dotenv'
    }
    
    missing_packages = []
    
    for module, package in critical_packages.items():
        try:
            __import__(module)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少关键依赖包:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n💡 解决方案: pip install -r requirements.txt")
        return False
    
    print("✅ 关键依赖包已安装")
    return True

def check_env_variables():
    """检查环境变量配置"""
    print("\n🔑 检查环境变量...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("❌ 无法加载环境变量（缺少python-dotenv）")
        return False
    
    # 必须的基础配置
    required_vars = ['TELEGRAM_BOT_TOKEN']
    
    # AI配置（二选一）
    ai_vars = ['OPENAI_API_KEY', 'DEEPSEEK_API_KEY']
    
    missing_vars = []
    
    # 检查必须变量
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            masked = value[:10] + '...' if len(value) > 10 else value
            print(f"✅ {var}: {masked}")
    
    # 检查AI配置
    has_ai_key = any(os.getenv(var) for var in ai_vars)
    if not has_ai_key:
        print("❌ 需要配置AI服务密钥（OpenAI或DeepSeek）")
        missing_vars.extend(ai_vars)
    else:
        for var in ai_vars:
            value = os.getenv(var)
            if value:
                masked = value[:10] + '...'
                print(f"✅ {var}: {masked}")
    
    if missing_vars:
        print(f"\n❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("💡 解决方案: 运行 'python setup_env.py'")
        return False
    
    return True

def choose_startup_mode():
    """选择启动模式"""
    print("\n🎯 选择启动模式:")
    print("1. Telegram机器人 (默认)")
    print("2. FastAPI服务器")
    print("3. 同时启动两者")
    
    while True:
        choice = input("\n请选择 (1/2/3，默认1): ").strip() or "1"
        if choice in ['1', '2', '3']:
            return choice
        print("❌ 请输入 1、2 或 3")

def test_imports():
    """测试关键模块导入"""
    print("\n🧪 测试模块导入...")
    
    # 确保路径正确
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    try:
        from data.tarot_cards import get_all_cards
        cards = get_all_cards()
        print(f"✅ 塔罗牌数据: {len(cards)}张")
    except Exception as e:
        print(f"❌ 塔罗牌数据导入失败: {e}")
        return False
    
    try:
        from src.tarot_reader import TarotReader
        print("✅ 塔罗读取器导入成功")
    except Exception as e:
        print(f"❌ 塔罗读取器导入失败: {e}")
        return False
    
    try:
        from src.ai_interpreter import TarotAIInterpreter
        print("✅ AI解释器导入成功")
    except Exception as e:
        print(f"❌ AI解释器导入失败: {e}")
        return False
    
    return True

def start_bot():
    """启动Telegram机器人"""
    print("\n🤖 启动Telegram机器人...")
    try:
        from src.bot import main as bot_main
        bot_main()
    except ImportError as e:
        print(f"❌ 机器人模块导入失败: {e}")
        print("💡 提示: 运行 'python test_imports.py' 检查导入问题")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 机器人启动失败: {e}")
        sys.exit(1)

def start_api():
    """启动FastAPI服务器"""
    print("\n🚀 启动FastAPI服务器...")
    try:
        from app import run_server
        run_server()
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        sys.exit(1)

def main():
    """主启动函数"""
    print("🔮 Глас Таро 智能启动器")
    print("=" * 50)
    
    # 执行所有检查
    checks = [
        ("Python版本", check_python_version),
        ("项目文件", check_project_files), 
        ("环境配置", check_env_file),
        ("依赖包", check_dependencies),
        ("环境变量", check_env_variables),
        ("模块导入", test_imports)
    ]
    
    for name, check_func in checks:
        if not check_func():
            print(f"\n💥 {name}检查失败！")
            print("请修复上述问题后重试")
            sys.exit(1)
    
    print("\n🎉 所有检查通过！")
    
    # 选择启动模式
    mode = choose_startup_mode()
    
    try:
        if mode == "1":
            start_bot()
        elif mode == "2":
            start_api()
        elif mode == "3":
            print("\n🚀 同时启动模式")
            print("💡 建议：分别在不同终端运行")
            print("   终端1: python main.py")
            print("   终端2: python app.py")
            
            choice = input("\n是否启动机器人？(y/N): ").lower()
            if choice == 'y':
                start_bot()
            else:
                print("👋 启动已取消")
                
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"\n❌ 运行错误: {e}")
        print("💡 提示: 检查配置和网络连接")
        sys.exit(1)

if __name__ == '__main__':
    main()