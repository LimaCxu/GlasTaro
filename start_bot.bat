@echo off
echo 正在启动 Глас Таро 塔罗预测机器人...
echo =======================================

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请安装Python 3.8或更高版本
    pause
    exit /b 1
)

:: 检查虚拟环境
if exist venv (
    echo [信息] 使用虚拟环境...
    call venv\Scripts\activate
) else (
    echo [警告] 未检测到虚拟环境，使用系统Python
)

:: 启动机器人
echo [信息] 启动塔罗预测机器人...
python main.py

:: 如果机器人异常退出
if %errorlevel% neq 0 (
    echo [错误] 机器人异常退出，错误代码: %errorlevel%
    pause
)