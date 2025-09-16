# 🔮 Глас Таро (Glas Taro) - AI塔罗占卜机器人

一个智能塔罗占卜Telegram机器人，结合了AI技术提供专业的塔罗牌解读和每日指导。

## ✨ 核心功能

- 🎴 **多种牌阵占卜** - 单张牌、三张牌、爱情牌阵、事业牌阵等
- 🤖 **AI智能解读** - 基于OpenAI GPT模型的专业塔罗解释
- 📅 **每日塔罗** - 每天一张塔罗牌指导和建议
- 📚 **塔罗学习** - 完整的78张塔罗牌详细介绍
- 👥 **用户管理** - 会话管理和请求频率限制
- 🌍 **多语言支持** - 中文、英文、俄文界面
- 🚀 **FastAPI后端** - 现代化的API服务架构

## 📁 项目架构

```
GlasTaro/
├── app.py                 # FastAPI主应用入口
├── main.py               # Telegram机器人入口
├── run.py                # 启动脚本（带环境检查）
├── requirements.txt      # Python依赖包
├── .env                  # 环境配置（需要自己创建）
├── .env.example         # 环境配置示例
├── 
├── api/                  # FastAPI路由
│   └── v1/              # API v1版本
│       ├── auth.py      # 认证相关
│       ├── users.py     # 用户管理
│       ├── divination.py # 占卜功能
│       └── ...
├── 
├── src/                 # Telegram机器人核心代码
│   ├── bot.py          # 机器人主逻辑
│   ├── tarot_reader.py # 塔罗牌读取器
│   ├── ai_interpreter.py # AI解读器
│   └── language_manager.py # 多语言管理
├── 
├── core/               # 核心组件
│   ├── config.py      # 配置管理
│   ├── middleware.py  # 中间件
│   └── dependencies.py # 依赖注入
├── 
├── config/            # 配置文件
│   ├── database.py   # 数据库配置
│   ├── redis_config.py # Redis配置
│   └── languages.py  # 语言配置
├── 
├── models/           # 数据库模型
│   ├── user.py      # 用户模型
│   ├── divination.py # 占卜模型
│   └── ...
├── 
├── services/         # 业务服务层
│   ├── user_service.py
│   ├── divination_service.py
│   └── ...
├── 
├── utils/           # 工具函数
│   ├── exceptions.py # 异常定义
│   ├── security.py  # 安全工具
│   └── validators.py # 验证器
├── 
└── data/           # 数据文件
    ├── tarot_cards.py # 塔罗牌数据
    └── user_languages.json # 用户语言设置
```

## 🚀 快速开始

### 1. 准备工作

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd GlasTaro

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt
```

### 2. 获取必要的API密钥

#### 🤖 Telegram Bot Token
1. 在Telegram中找到 [@BotFather](https://t.me/botfather)
2. 发送 `/newbot` 命令
3. 按提示设置机器人名称和用户名
4. 获得Bot Token（格式：`123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`）

#### 🧠 AI API密钥（二选一）

**选择1: OpenAI API Key**
1. 访问 [OpenAI官网](https://platform.openai.com/)
2. 注册账号并充值
3. 在API Keys页面创建新的密钥

**选择2: DeepSeek API Key（推荐，更便宜）**
1. 访问 [DeepSeek官网](https://platform.deepseek.com/)
2. 注册账号并充值（价格比OpenAI便宜很多）
3. 在API Keys页面创建新的密钥

### 3. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
nano .env  # 或者用你喜欢的编辑器
```

**⚠️ 重要：在 `.env` 文件中至少要配置这些：**
```env
# 必须配置
TELEGRAM_BOT_TOKEN=你的机器人Token
DATABASE_URL=postgresql+asyncpg://用户名:密码@localhost:5432/数据库名
REDIS_URL=redis://localhost:6379/0  # 无密码
# REDIS_URL=redis://:密码@localhost:6379/5  # 有密码示例
SECRET_KEY=至少32位的随机字符串

# AI模型配置（二选一）
AI_MODEL=deepseek-chat  # 或者 gpt-3.5-turbo

# 如果使用DeepSeek（推荐，便宜）
DEEPSEEK_API_KEY=你的DeepSeek密钥

# 如果使用OpenAI
OPENAI_API_KEY=你的OpenAI密钥

# 可选配置
DEBUG=true
```

### 4. 启动服务

#### 🔰 新手推荐（有环境检查）
```bash
python run.py
```
智能启动器，会检查环境并让你选择启动模式。

#### 🚀 快速启动（生产环境）
```bash
# 启动Telegram机器人
python main.py

# 启动API服务器
python app.py
```

#### 📋 启动文件说明

| 文件 | 用途 | 特点 |
|------|------|------|
| `run.py` | 智能启动器 | 环境检查、选择模式 |
| `main.py` | 机器人启动 | 纯粹、快速 |
| `app.py` | API服务器 | FastAPI后端 |

### 5. 验证运行

- 在Telegram中找到你的机器人
- 发送 `/start` 命令
- 如果收到欢迎消息，说明配置成功！

## 🛠️ 技术栈

### 后端架构
- **FastAPI** - 现代化的Web API框架
- **SQLAlchemy** - 数据库ORM
- **PostgreSQL** - 主数据库
- **Redis** - 缓存和会话存储
- **Alembic** - 数据库迁移工具

### 机器人框架
- **python-telegram-bot** - Telegram Bot API
- **asyncio** - 异步编程支持

### AI集成
- **OpenAI API** - GPT模型调用
- **python-openai** - OpenAI官方客户端

### 工具库
- **pydantic** - 数据验证
- **python-dotenv** - 环境变量管理
- **prometheus-client** - 监控指标
- **loguru** - 日志管理

## 🤖 AI模型支持

| 模型 | 提供商 | 适用场景 | 成本 | 推荐指数 |
|------|--------|----------|------|----------|
| **deepseek-chat** | DeepSeek | 日常占卜 | 超低 | ⭐⭐⭐⭐⭐ |
| **gpt-3.5-turbo** | OpenAI | 日常占卜 | 低 | ⭐⭐⭐⭐ |
| **gpt-4** | OpenAI | 深度解读 | 高 | ⭐⭐⭐⭐ |
| **gpt-4-turbo** | OpenAI | 平衡选择 | 中 | ⭐⭐⭐⭐ |

**💡 推荐使用DeepSeek：**
- 🔥 **成本超低** - 比OpenAI便宜10倍以上
- 🚀 **效果优秀** - 中文理解能力强
- ⚡ **响应快速** - 国内访问速度快
- 🛡️ **稳定可靠** - 大模型公司，服务稳定

在 `.env` 文件中设置 `AI_MODEL=deepseek-chat` 即可使用。

## 📖 使用指南

### 🎯 Telegram机器人命令

| 命令 | 功能描述 |
|------|----------|
| `/start` | 启动机器人，显示主菜单 |
| `/help` | 查看帮助信息和使用说明 |
| `/daily` | 获取今日塔罗牌指导 |
| `/reading` | 开始塔罗占卜（选择牌阵） |
| `/learn` | 学习塔罗牌知识 |

### 🔮 占卜流程

1. **选择牌阵** - 单张牌、三张牌、爱情牌阵等
2. **输入问题** - 描述你想了解的问题（可跳过）
3. **AI解读** - 获得基于GPT的专业塔罗解读
4. **保存记录** - 系统自动保存占卜历史

### ⚙️ 配置说明

主要配置文件：
- `core/config.py` - 应用主配置
- `.env` - 环境变量配置
- `config/database.py` - 数据库配置
- `config/redis_config.py` - Redis缓存配置

关键配置项：
```python
# 占卜限制
FREE_READINGS_PER_DAY = 3      # 免费用户每日占卜次数
PREMIUM_READINGS_PER_DAY = 20  # 付费用户每日占卜次数

# AI配置
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MAX_TOKENS = 1000
OPENAI_TEMPERATURE = 0.7

# 安全配置
ENABLE_RATE_LIMIT = True
RATE_LIMIT_REQUESTS = 60  # 每分钟请求限制
```

## 🔧 开发相关

### 数据库迁移
```bash
# 创建迁移文件
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

### API文档
启动服务后访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 监控指标
- Prometheus指标: `http://localhost:8000/metrics`
- 健康检查: `http://localhost:8000/health`

## 🔒 安全建议

- ✅ 使用强密码和复杂的SECRET_KEY
- ✅ 定期轮换API密钥
- ✅ 启用速率限制防止滥用
- ✅ 监控API使用量和成本
- ✅ 不要将`.env`文件提交到版本控制
- ✅ 生产环境关闭DEBUG模式

## 🐛 常见问题

**Q: 启动时出现"bad escape (end of pattern)"错误？**
A: 这是正则表达式转义字符的问题，已在最新版本修复。确保使用最新的代码。

**Q: 机器人无响应？**
A: 检查TELEGRAM_BOT_TOKEN是否正确，网络是否正常

**Q: AI解读失败？**
A: 检查OPENAI_API_KEY是否有效，账户是否有余额

**Q: 数据库连接失败？**
A: 确认PostgreSQL服务运行正常，DATABASE_URL配置正确

**Q: Redis连接失败？**
A: 确认Redis服务运行正常，REDIS_URL配置正确
   - 无密码：`redis://localhost:6379/0`
   - 有密码：`redis://:密码@localhost:6379/0`
   - 示例：`redis://:mypassword@localhost:6379/5`

## 📄 开源协议

MIT License - 详见 LICENSE 文件

## 💝 支持项目

如果这个项目对你有帮助，欢迎：
- ⭐ 给项目点个Star
- 🐛 报告Bug和建议
- 🔧 提交Pull Request

## 📜 许可证

本项目基于 [MIT License](LICENSE) 开源协议。

---