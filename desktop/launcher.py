"""
Portal Desktop Launcher
=======================
内嵌 FastAPI 服务器 + PyWebView 桌面窗口
启动后自动打开桌面端应用，UI 与 Web 版完全一致
"""
import os
import sys
import time
import socket
import threading
import webview

# ============================================================
# 配置
# ============================================================
PORTAL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(PORTAL_DIR, "templates")
STATIC_DIR = os.path.join(PORTAL_DIR, "static")
DATA_DIR = os.path.join(PORTAL_DIR, "data")

# 桌面端监听端口（避免与可能运行的 web 版冲突）
DESKTOP_PORT = 18080

# ============================================================
# 找空闲端口
# ============================================================
def find_free_port(port):
    """如果指定端口被占用，往后找"""
    for p in range(port, port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    return port

# ============================================================
# 启动 FastAPI 后端（后台线程）
# ============================================================
def start_server(port):
    """在后台线程中启动 uvicorn"""
    import uvicorn

    os.chdir(PORTAL_DIR)
    sys.path.insert(0, PORTAL_DIR)

    # 设置数据目录环境变量
    os.environ["PORTAL_DATA_DIR"] = DATA_DIR
    os.environ["PORTAL_DESKTOP"] = "1"

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=port,
        log_level="warning",
        access_log=False,
    )

def wait_for_server(port, timeout=15):
    """等待服务器就绪"""
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.3)
    return False

# ============================================================
# PyWebView 窗口配置
# ============================================================
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
MIN_WIDTH = 1024
MIN_HEIGHT = 700

# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 60)
    print("  ✨ Portal Desktop")
    print("  多系统智能门户 - 桌面版")
    print("=" * 60)

    # 1. 找端口
    port = find_free_port(DESKTOP_PORT)
    print(f"[1/4] 监听端口: {port}")

    # 2. 启动后端线程
    print("[2/4] 启动后端服务器...")
    server_thread = threading.Thread(
        target=start_server,
        args=(port,),
        daemon=True,
    )
    server_thread.start()

    # 3. 等待就绪
    print("[3/4] 等待服务器就绪...")
    if not wait_for_server(port):
        print("  ✗ 服务器启动失败，请检查端口是否被占用")
        sys.exit(1)
    print(f"  ✓ 服务器已就绪: http://127.0.0.1:{port}")

    base_url = f"http://127.0.0.1:{port}"

    # 4. 打开 PyWebView 窗口
    print("[4/4] 启动桌面窗口...")
    print(f"  URL: {base_url}")
    print("=" * 60)

    window = webview.create_window(
        title="✨ Portal - 多系统智能门户",
        url=f"{base_url}/",
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        min_size=(MIN_WIDTH, MIN_HEIGHT),
        frameless=False,
        easy_drag=True,
        text_select=True,
    )

    webview.start(
        debug=False,
        gui="qt",  # 使用 Qt 后端（Linux 兼容性最好）
    )

    print("\n  Portal Desktop 已关闭。再见！ 👋")


if __name__ == "__main__":
    main()
