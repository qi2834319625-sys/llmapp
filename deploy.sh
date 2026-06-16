#!/bin/bash
# ============================================
# 多系统智能门户 - 一键部署脚本
# 使用方法: bash deploy.sh
# ============================================

set -e

echo "🚀 开始部署多系统智能门户..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt -q

# 创建必要目录
mkdir -p data static/audio/generated static/papers static/css static/js uploads

# 初始化数据库
echo "💾 初始化数据库..."
python3 -c "from app import init_db; init_db(); print('✅ 数据库初始化完成')"

# 启动服务器
echo ""
echo "============================================"
echo "🎉 部署完成！"
echo "============================================"
echo "🌐 访问地址: http://localhost:8080"
echo "👤 用户名: qmlaizyh"
echo "🔑 密码: qwe123123"
echo "============================================"
echo ""

# 启动
python3 -c "from app import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8080)"
