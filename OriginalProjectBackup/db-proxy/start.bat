@echo off
chcp 65001 >nul
echo ========================================
echo 数据库代理服务启动脚本 (Windows)
echo ========================================
echo.

if not exist ".env" (
    echo [错误] 未找到 .env 文件！
    echo 请先复制 .env.example 为 .env 并配置数据库信息
    echo.
    pause
    exit /b 1
)

echo [信息] 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    echo.
    pause
    exit /b 1
)

echo [信息] 正在检查依赖...
if not exist "venv" (
    echo [信息] 正在创建虚拟环境...
    python -m venv venv
)

echo [信息] 正在激活虚拟环境...
call venv\Scripts\activate.bat

echo [信息] 正在安装依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ========================================
echo 数据库代理服务启动中...
echo ========================================
echo API文档: http://localhost:8001/docs
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python main.py

pause
