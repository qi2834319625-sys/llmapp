#!/bin/bash
# ============================================================
# Portal Desktop 启动脚本
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORTAL_DIR="$(dirname "$SCRIPT_DIR")"

# 激活虚拟环境
source "$PORTAL_DIR/venv/bin/activate"

# 切换到 portal 目录
cd "$PORTAL_DIR"

# 设置 Qt 平台插件路径（无显示器环境用 offscreen）
if [ -z "$DISPLAY" ]; then
    echo "⚠ 未检测到显示器，使用 offscreen 模式（仅用于测试）"
    export QT_QPA_PLATFORM=offscreen
fi

# 启动桌面应用
exec python3 "$SCRIPT_DIR/app.py" "$@"
