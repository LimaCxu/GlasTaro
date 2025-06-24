# 🔮 塔罗预测 Telegram 机器人

一个基于 Python 和 OpenAI 的智能塔罗牌占卜 Telegram 机器人，提供个性化的塔罗牌解读和人生指导。

## ✨ 功能特色

### 🎴 塔罗占卜
- **多种牌阵选择**：单张牌、三张牌、爱情、事业、决策牌阵
- **AI 智能解读**：结合 OpenAI GPT 提供深度个性化解读
- **正逆位支持**：完整的塔罗牌正逆位含义解释
- **互动式体验**：友好的用户界面和流畅的交互流程

### 🌅 每日指导
- **每日塔罗牌**：获取今日的塔罗指导和建议
- **个性化解读**：基于抽取的牌提供专属的每日指导
- **积极引导**：温暖正面的人生建议和鼓励

### 📚 学习中心
- **完整牌库**：包含 78 张塔罗牌的详细信息
- **大阿卡纳**：22 张主要奥秘牌的深度解释
- **小阿卡纳**：56 张日常生活牌的实用指导
- **基础知识**：塔罗牌的历史、原理和使用方法

## 🛠️ 技术栈

- **Python 3.8+**
- **python-telegram-bot**：Telegram Bot API 封装
- **OpenAI API**：AI 智能解读生成
- **python-dotenv**：环境变量管理
- **其他依赖**：详见 `requirements.txt`

## 📦 安装指南

### 1. 克隆项目
```bash
git clone <repository-url>
cd TG
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
复制 `.env.example` 为 `.env` 并填入必要信息：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Bot Configuration
BOT_USERNAME=your_bot_username
DEBUG=False

# Tarot Configuration
MAX_CARDS_PER_READING=3
READING_TIMEOUT=300
```

### 4. 获取必要的 API 密钥

#### Telegram Bot Token
1. 在 Telegram 中找到 [@BotFather](https://t.me/botfather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 获取 Bot Token 并填入 `.env` 文件

#### OpenAI API Key
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册账户并登录
3. 在 API Keys 页面创建新的 API 密钥
4. 将密钥填入 `.env` 文件

### 5. 运行机器人
```bash
python bot.py
```

## 🎯 使用方法

### 基本命令
- `/start` - 开始使用机器人
- `/daily` - 获取每日塔罗指导
- `/reading` - 开始塔罗占卜
- `/learn` - 学习塔罗牌知识
- `/help` - 显示帮助信息

### 占卜流程
1. 发送 `/reading` 或点击"开始占卜"按钮
2. 选择占卜类型（单张牌、三张牌、爱情、事业、决策）
3. 输入你的问题（可选）
4. 等待机器人抽牌并生成 AI 解读
5. 查看详细的塔罗牌解读和建议

### 学习功能
1. 发送 `/learn` 或点击"学习塔罗"按钮
2. 选择学习内容：
   - 大阿卡纳：22 张主要奥秘牌
   - 小阿卡纳：56 张日常生活牌
   - 基础知识：塔罗牌原理和使用方法
3. 浏览牌库并查看详细解释

## 📁 项目结构

```
TG/
├── bot.py                 # 主程序文件
├── tarot_reader.py        # 塔罗牌抽取和解读核心逻辑
├── tarot_cards.py         # 塔罗牌数据库
├── ai_interpreter.py      # AI 解读生成模块
├── requirements.txt       # 项目依赖
├── .env.example          # 环境变量模板
├── .env                  # 环境变量配置（需要创建）
└── README.md             # 项目说明文档
```

## 🔧 配置选项

### 环境变量说明

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | - | ✅ |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - | ✅ |
| `OPENAI_MODEL` | OpenAI 模型名称 | `gpt-3.5-turbo` | ❌ |
| `BOT_USERNAME` | 机器人用户名 | - | ❌ |
| `DEBUG` | 调试模式 | `False` | ❌ |
| `MAX_CARDS_PER_READING` | 每次占卜最大牌数 | `3` | ❌ |
| `READING_TIMEOUT` | 占卜超时时间（秒） | `300` | ❌ |

## 🎴 塔罗牌数据

### 大阿卡纳（22张）
包含从愚者（0）到世界（21）的完整大阿卡纳牌组，每张牌都有：
- 中文名称和英文名称
- 正位和逆位含义
- 详细描述和象征意义

### 小阿卡纳（56张）
包含四个花色的完整小阿卡纳：
- **权杖**（火元素）：创造力、激情、能量
- **圣杯**（水元素）：情感、关系、直觉
- **宝剑**（风元素）：思想、沟通、冲突
- **金币**（土元素）：物质、金钱、实用性

每个花色包含：Ace、2-10、侍从、骑士、皇后、国王

## 🤖 AI 解读功能

### 解读类型
1. **塔罗占卜解读**：基于抽取的牌和用户问题生成个性化解读
2. **每日指导**：提供简洁而深刻的每日塔罗指导
3. **牌义解释**：详细解释单张塔罗牌的含义和象征

### AI 提示词优化
- 专业的塔罗牌占卜师角色设定
- 温暖、富有洞察力的解读风格
- 结合牌阵位置和牌义的综合分析
- 实用的人生建议和指导

## 🚀 部署建议

### 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 运行机器人
python bot.py
```

### 生产环境
1. **服务器部署**：使用 systemd 或 supervisor 管理进程
2. **容器化**：使用 Docker 进行容器化部署
3. **云平台**：部署到 Heroku、AWS、阿里云等云平台
4. **监控日志**：配置日志记录和错误监控

### Docker 部署（可选）
```dockerfile
# Dockerfile 示例
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "bot.py"]
```

## 🔒 安全注意事项

1. **API 密钥安全**：
   - 不要将 API 密钥提交到版本控制系统
   - 使用环境变量存储敏感信息
   - 定期轮换 API 密钥

2. **用户隐私**：
   - 不记录用户的个人问题
   - 不存储用户的占卜历史
   - 遵守数据保护法规

3. **访问控制**：
   - 可以添加用户白名单功能
   - 实现使用频率限制
   - 监控异常使用行为

## 🐛 故障排除

### 常见问题

1. **机器人无响应**
   - 检查 Telegram Bot Token 是否正确
   - 确认网络连接正常
   - 查看控制台错误日志

2. **AI 解读失败**
   - 检查 OpenAI API 密钥是否有效
   - 确认 API 配额是否充足
   - 检查网络是否能访问 OpenAI API

3. **依赖安装失败**
   - 升级 pip：`pip install --upgrade pip`
   - 使用虚拟环境：`python -m venv venv`
   - 检查 Python 版本是否兼容

### 日志调试
```python
# 在 bot.py 中启用详细日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # 改为 DEBUG 级别
)
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发流程
1. Fork 项目
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 提交 Pull Request

### 代码规范
- 遵循 PEP 8 Python 代码规范
- 添加适当的注释和文档字符串
- 编写单元测试（如适用）

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API 封装
- [OpenAI](https://openai.com/) - AI 解读能力支持
- 塔罗牌社区 - 提供丰富的塔罗牌知识和智慧

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件至：[your-email@example.com]
- Telegram：[@your-telegram-username]

---

✨ **愿塔罗的智慧为你指引人生方向！** ✨