# 🚀 Глас Таро 快速启动指南

## 📋 启动前检查清单

- [ ] Python 3.8+ 已安装
- [ ] 已获取 Telegram Bot Token
- [ ] 已获取 OpenAI API Key
- [ ] 已安装项目依赖

## ⚡ 3分钟快速启动

### 1️⃣ 安装依赖
```bash
pip install -r requirements.txt
```

### 2️⃣ 配置环境变量
```bash
# 复制配置模板
cp config/.env.example .env

# 编辑 .env 文件，填入以下信息：
# TELEGRAM_BOT_TOKEN=你的机器人Token
# OPENAI_API_KEY=你的OpenAI密钥
```

### 3️⃣ 启动机器人
```bash
# 方法1: 使用run.py启动脚本
python run.py

# 方法2: 直接使用main.py入口文件
python main.py
```

## 🧪 测试功能
```bash
python -m tests.test_bot
```

## 📁 新目录结构说明

- `src/` - 所有核心代码
- `config/` - 配置文件和环境变量
- `data/` - 塔罗牌数据
- `tests/` - 测试文件
- `docs/` - 详细文档

## 🔧 常见问题

**Q: 导入错误怎么办？**
A: 确保在项目根目录运行，使用 `python -m` 方式导入模块

**Q: 机器人无响应？**
A: 检查 `.env` 文件中的 Token 是否正确

**Q: AI解读失败？**
A: 检查 OpenAI API Key 是否有效且有余额

---

🎯 **目标**: 让 Глас Таро 成为最智能的塔罗预测机器人！