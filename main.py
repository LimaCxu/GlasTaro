#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Глас Таро Telegram机器人启动器
纯粹的机器人启动文件，不带环境检查

作者: Lima
用途: 直接启动Telegram机器人（适合生产环境）
"""

import sys
import os
from pathlib import Path

# 确保项目根目录在Python路径中
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def main():
    """启动Telegram机器人"""
    print("🤖 启动Глас Таро机器人...")
    
    try:
        from src.bot import main as bot_main
        bot_main()
    except KeyboardInterrupt:
        print("\n👋 机器人已停止")
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 提示: 请确保在项目根目录运行，或使用 'python run.py'")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        print("💡 建议: 使用 'python run.py' 进行环境检查")
        sys.exit(1)

if __name__ == '__main__':
    main()