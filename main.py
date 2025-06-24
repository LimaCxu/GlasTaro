#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Глас Таро (Glas Taro) - AI塔罗预测机器人
主入口文件

这个文件解决了Python模块导入路径问题，
确保项目能够正确运行。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """主函数"""
    try:
        # 现在可以正确导入模块
        from src.bot import main as bot_main
        bot_main()
    except KeyboardInterrupt:
        print("\n\n👋 机器人已停止运行")
    except Exception as e:
        print(f"\n❌ 运行时错误：{e}")
        print("请检查配置和网络连接")
        sys.exit(1)

if __name__ == '__main__':
    main()