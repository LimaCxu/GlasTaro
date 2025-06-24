# Глас Таро (Glas Taro) - AI塔罗预测机器人

一个结合人工智能的Telegram塔罗牌占卜机器人，提供专业的塔罗牌解读和每日指导。

## 🔮 功能特色

- **多种牌阵占卜**：支持单张牌、三张牌、凯尔特十字等多种牌阵
- **AI智能解读**：基于OpenAI GPT模型的专业塔罗牌解释
- **每日塔罗**：每日一张塔罗牌指导
- **塔罗学习**：78张塔罗牌的详细介绍和含义
- **用户管理**：会话管理和请求频率限制
- **多语言支持**：支持中文和俄文界面

## 📁 项目结构

```
Глас Таро/
├── src/                    # 核心源代码
│   ├── __init__.py
│   ├── bot.py             # 主机器人程序
│   ├── tarot_reader.py    # 塔罗牌阅读器
│   ├── ai_interpreter.py  # AI解释器
│   └── user_manager.py    # 用户管理
├── config/                 # 配置文件
│   ├── __init__.py
│   ├── config.py          # 主配置文件
│   └── .env.example       # 环境变量示例
├── data/                   # 数据文件
│   ├── __init__.py
│   └── tarot_cards.py     # 塔罗牌数据
├── tests/                  # 测试文件
│   ├── __init__.py
│   └── test_bot.py        # 机器人测试
├── docs/                   # 文档
│   └── README.md          # 详细文档
├── requirements.txt        # Python依赖
├── run.py                 # 启动脚本
└── .gitignore             # Git忽略文件
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd TG

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的API密钥和选择AI模型
# TELEGRAM_BOT_TOKEN=你的Telegram机器人Token
# AI_MODEL=gpt-3.5-turbo  # 可选: gpt-3.5-turbo, gpt-4, deepseek-chat
# OPENAI_API_KEY=你的OpenAI API密钥 (使用GPT模型时)
# DEEPSEEK_API_KEY=你的DeepSeek API密钥 (使用DeepSeek模型时)
```

### 3. 运行机器人

```bash
# 方法1: 使用启动脚本（推荐）
python run.py

# 方法2: 直接使用主入口文件
python main.py
```

### 4. 测试功能

```bash
# 运行测试
python -m tests.test_bot
```

## 🛠️ 技术栈

- **Python 3.8+**
- **python-telegram-bot**: Telegram Bot API
- **OpenAI API / DeepSeek API**: AI文本生成（支持多种模型切换）
- **python-dotenv**: 环境变量管理
- **aiohttp**: 异步HTTP客户端

## 🤖 支持的AI模型

- **GPT-3.5 Turbo**: OpenAI的高效模型，适合日常使用
- **GPT-4**: OpenAI的最强模型，提供更深入的解读
- **DeepSeek Chat**: 国产优秀模型，性价比高

通过修改 `.env` 文件中的 `AI_MODEL` 参数即可切换模型。

## 📖 使用方法

### Telegram命令

- `/start` - 开始使用机器人
- `/help` - 查看帮助信息
- `/daily` - 获取每日塔罗牌
- `/reading` - 开始塔罗占卜
- `/learn` - 学习塔罗牌知识

### 占卜流程

1. 发送 `/reading` 命令
2. 选择牌阵类型
3. 输入你的问题
4. 获得AI解读结果

## ⚙️ 配置选项

详细配置请查看 `config/config.py` 文件，包括：

- API设置
- 机器人功能参数
- 用户请求限制
- 牌阵配置
- AI提示词模板

## 🔒 安全注意事项

- 不要将 `.env` 文件提交到版本控制
- 定期更换API密钥
- 设置合理的请求频率限制
- 监控API使用量

## 📝 许可证

MIT License

## 🙏 致谢

感谢所有为塔罗牌文化传承做出贡献的人们。