@echo off
chcp 65001 >nul
echo ============================================
echo Database Proxy Client
echo ============================================
echo.

if not exist ".env" (
    echo Creating config file...
    copy ".env.example" ".env"
    echo.
    echo [!] Please edit .env file to configure your database and relay service
    echo.
    pause
    exit /b 1
)

python client.py

pause
