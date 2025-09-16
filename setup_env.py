#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境配置向导
帮助用户快速配置 .env 文件

作者: Lima
"""

import os
import secrets
from pathlib import Path

def generate_secret_key():
    """生成安全的密钥"""
    return secrets.token_urlsafe(32)

def create_env_file():
    """创建 .env 文件的交互式向导"""
    print("🔮 Глас Таро 配置向导")
    print("=" * 40)
    
    env_path = Path(".env")
    if env_path.exists():
        overwrite = input("⚠️  .env 文件已存在，是否覆盖？(y/N): ").lower()
        if overwrite != 'y':
            print("❌ 取消配置")
            return
    
    print("\n📝 请输入必要的配置信息：")
    
    # 收集配置信息
    config = {}
    
    # Telegram Bot Token
    print("\n🤖 Telegram机器人配置")
    print("请到 @BotFather 获取Bot Token")
    bot_token = input("Telegram Bot Token: ").strip()
    if not bot_token:
        print("❌ Bot Token是必须的！")
        return
    config['TELEGRAM_BOT_TOKEN'] = bot_token
    
    # AI模型选择
    print("\n🧠 AI模型配置")
    print("选择AI模型:")
    print("1. OpenAI GPT (需要OpenAI API Key)")
    print("2. DeepSeek (国产模型，更便宜)")
    
    while True:
        choice = input("请选择 (1/2): ").strip()
        if choice in ['1', '2']:
            break
        print("❌ 请输入 1 或 2")
    
    if choice == '1':
        # OpenAI配置
        print("\n请到 https://platform.openai.com/ 获取API Key")
        openai_key = input("OpenAI API Key: ").strip()
        if not openai_key:
            print("❌ OpenAI API Key是必须的！")
            return
        config['AI_MODEL'] = 'gpt-3.5-turbo'
        config['OPENAI_API_KEY'] = openai_key
        config['DEEPSEEK_API_KEY'] = ''
    else:
        # DeepSeek配置
        print("\n请到 https://platform.deepseek.com/ 获取API Key")
        deepseek_key = input("DeepSeek API Key: ").strip()
        if not deepseek_key:
            print("❌ DeepSeek API Key是必须的！")
            return
        config['AI_MODEL'] = 'deepseek-chat'
        config['OPENAI_API_KEY'] = ''
        config['DEEPSEEK_API_KEY'] = deepseek_key
    
    # 数据库配置
    print("\n🗄️  数据库配置")
    db_host = input("数据库主机 (默认: localhost): ").strip() or "localhost"
    db_port = input("数据库端口 (默认: 5432): ").strip() or "5432"
    db_name = input("数据库名称 (默认: tarot_bot): ").strip() or "tarot_bot"
    db_user = input("数据库用户名 (默认: postgres): ").strip() or "postgres"
    db_pass = input("数据库密码: ").strip()
    
    config['DATABASE_URL'] = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    
    # Redis配置
    print("\n🔄 Redis配置")
    redis_host = input("Redis主机 (默认: localhost): ").strip() or "localhost"
    redis_port = input("Redis端口 (默认: 6379): ").strip() or "6379"
    redis_password = input("Redis密码 (没有密码直接回车): ").strip()
    redis_db = input("Redis数据库编号 (默认: 0): ").strip() or "0"
    
    # 构建Redis URL
    if redis_password:
        config['REDIS_URL'] = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
    else:
        config['REDIS_URL'] = f"redis://{redis_host}:{redis_port}/{redis_db}"
    
    # 生成SECRET_KEY
    config['SECRET_KEY'] = generate_secret_key()
    
    # 其他默认配置
    config.update({
        'DEBUG': 'true',
        'HOST': '0.0.0.0',
        'PORT': '8000',
        'OPENAI_MODEL': 'gpt-3.5-turbo',
        'OPENAI_MAX_TOKENS': '1000',
        'OPENAI_TEMPERATURE': '0.7',
        'FREE_READINGS_PER_DAY': '3',
        'PREMIUM_READINGS_PER_DAY': '20',
        'ENABLE_RATE_LIMIT': 'true',
        'RATE_LIMIT_REQUESTS': '60',
        'RATE_LIMIT_WINDOW': '60',
        'DEFAULT_LANGUAGE': 'zh',
        'SUPPORTED_LANGUAGES': 'zh,en,ru',
        'ENABLE_METRICS': 'true',
        'LOG_LEVEL': 'INFO',
        'MAINTENANCE_MODE': 'false',
        'ALLOWED_HOSTS': '*',
        'ALLOWED_ORIGINS': '*'
    })
    
    # 写入.env文件
    print("\n💾 正在创建 .env 文件...")
    
    env_content = []
    env_content.append("# ========================================")
    env_content.append("# Глас Таро 环境配置文件")
    env_content.append("# 由配置向导自动生成")
    env_content.append("# 作者: Lima")
    env_content.append("# ========================================")
    env_content.append("")
    
    env_content.append("# 🤖 Telegram机器人配置")
    env_content.append(f"TELEGRAM_BOT_TOKEN={config['TELEGRAM_BOT_TOKEN']}")
    env_content.append("")
    
    env_content.append("# 🧠 AI模型配置")
    env_content.append(f"AI_MODEL={config['AI_MODEL']}")
    env_content.append("")
    env_content.append("# OpenAI配置")
    env_content.append(f"OPENAI_API_KEY={config['OPENAI_API_KEY']}")
    env_content.append(f"OPENAI_MODEL={config['OPENAI_MODEL']}")
    env_content.append(f"OPENAI_MAX_TOKENS={config['OPENAI_MAX_TOKENS']}")
    env_content.append(f"OPENAI_TEMPERATURE={config['OPENAI_TEMPERATURE']}")
    env_content.append("")
    env_content.append("# DeepSeek配置")
    env_content.append(f"DEEPSEEK_API_KEY={config['DEEPSEEK_API_KEY']}")
    env_content.append(f"DEEPSEEK_BASE_URL=https://api.deepseek.com")
    env_content.append(f"DEEPSEEK_MODEL=deepseek-chat")
    env_content.append(f"DEEPSEEK_MAX_TOKENS=1000")
    env_content.append(f"DEEPSEEK_TEMPERATURE=0.7")
    env_content.append("")
    
    env_content.append("# 🗄️ 数据库配置")
    env_content.append(f"DATABASE_URL={config['DATABASE_URL']}")
    env_content.append("")
    
    env_content.append("# 🔄 Redis配置")
    env_content.append(f"REDIS_URL={config['REDIS_URL']}")
    env_content.append("")
    
    env_content.append("# 🔐 安全配置")
    env_content.append(f"SECRET_KEY={config['SECRET_KEY']}")
    env_content.append("")
    
    env_content.append("# 🔧 应用配置")
    env_content.append(f"DEBUG={config['DEBUG']}")
    env_content.append(f"HOST={config['HOST']}")
    env_content.append(f"PORT={config['PORT']}")
    env_content.append("")
    
    env_content.append("# 🎴 业务配置")
    env_content.append(f"FREE_READINGS_PER_DAY={config['FREE_READINGS_PER_DAY']}")
    env_content.append(f"PREMIUM_READINGS_PER_DAY={config['PREMIUM_READINGS_PER_DAY']}")
    env_content.append("")
    
    env_content.append("# 🛡️ 安全防护")
    env_content.append(f"ENABLE_RATE_LIMIT={config['ENABLE_RATE_LIMIT']}")
    env_content.append(f"RATE_LIMIT_REQUESTS={config['RATE_LIMIT_REQUESTS']}")
    env_content.append(f"RATE_LIMIT_WINDOW={config['RATE_LIMIT_WINDOW']}")
    env_content.append("")
    
    env_content.append("# 🌍 多语言配置")
    env_content.append(f"DEFAULT_LANGUAGE={config['DEFAULT_LANGUAGE']}")
    env_content.append(f"SUPPORTED_LANGUAGES={config['SUPPORTED_LANGUAGES']}")
    env_content.append("")
    
    env_content.append("# 📊 监控配置")
    env_content.append(f"ENABLE_METRICS={config['ENABLE_METRICS']}")
    env_content.append(f"LOG_LEVEL={config['LOG_LEVEL']}")
    env_content.append("")
    
    env_content.append("# 🔧 其他配置")
    env_content.append(f"MAINTENANCE_MODE={config['MAINTENANCE_MODE']}")
    env_content.append(f"ALLOWED_HOSTS={config['ALLOWED_HOSTS']}")
    env_content.append(f"ALLOWED_ORIGINS={config['ALLOWED_ORIGINS']}")
    
    # 写入文件
    with open(".env", "w", encoding="utf-8") as f:
        f.write("\n".join(env_content))
    
    print("✅ .env 文件创建成功！")
    print("\n📋 配置摘要：")
    print(f"   🤖 机器人Token: {bot_token[:10]}...")
    
    if config['AI_MODEL'] == 'deepseek-chat':
        print(f"   🧠 AI模型: DeepSeek (更便宜)")
        print(f"   🔑 DeepSeek Key: {config['DEEPSEEK_API_KEY'][:10]}...")
    else:
        print(f"   🧠 AI模型: OpenAI GPT")
        print(f"   🔑 OpenAI Key: {config['OPENAI_API_KEY'][:10]}...")
    
    print(f"   🗄️  数据库: {db_host}:{db_port}/{db_name}")
    
    if redis_password:
        print(f"   🔄 Redis: {redis_host}:{redis_port}/{redis_db} (有密码)")
    else:
        print(f"   🔄 Redis: {redis_host}:{redis_port}/{redis_db} (无密码)")
        
    print(f"   🔐 密钥: 已自动生成")
    
    print("\n🚀 下一步：")
    print("   1. 确保PostgreSQL和Redis服务运行正常")
    print("   2. 运行 'python run.py' 启动服务")
    print("   3. 在Telegram中测试你的机器人")
    
    print("\n⚠️  安全提醒：")
    print("   - 不要将 .env 文件提交到版本控制")
    print("   - 定期更换API密钥")
    print("   - 生产环境记得修改相关配置")

def main():
    """主函数"""
    try:
        create_env_file()
    except KeyboardInterrupt:
        print("\n\n👋 配置已取消")
    except Exception as e:
        print(f"\n❌ 配置过程中出错: {e}")

if __name__ == "__main__":
    main()
