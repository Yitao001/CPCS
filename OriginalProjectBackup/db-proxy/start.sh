#!/bin/bash

echo "========================================"
echo "数据库代理服务启动脚本 (Linux/Mac)"
echo "========================================"
echo ""

if [ ! -f ".env" ]; then
    echo "[错误] 未找到 .env 文件！"
    echo "请先复制 .env.example 为 .env 并配置数据库信息"
    echo ""
    exit 1
fi

echo "[信息] 正在检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装Python 3.8+"
    echo ""
    exit 1
fi

echo "[信息] 正在检查依赖..."
if [ ! -d "venv" ]; then
    echo "[信息] 正在创建虚拟环境..."
    python3 -m venv venv
fi

echo "[信息] 正在激活虚拟环境..."
source venv/bin/activate

echo "[信息] 正在安装依赖..."
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo ""
echo "========================================"
echo "数据库代理服务启动中..."
echo "========================================"
echo "API文档: http://localhost:8001/docs"
echo "按 Ctrl+C 停止服务"
echo "========================================"
echo ""

python3 main.py
