"""
Portal Desktop Application
============================
PyQt5 + QWebEngineView + 内嵌 FastAPI
桌面端应用，UI 与 Web 版完全一致
"""
import os
import sys
import time
import socket
import threading
import subprocess

# ============================================================
# 路径配置
# ============================================================
PORTAL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESKTOP_PORT = 18080

# ============================================================
# 找空闲端口
# ============================================================
def find_free_port(port):
    for p in range(port, port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    return port

# ============================================================
# 启动 FastAPI 后端
# ============================================================
def start_server(port):
    import uvicorn
    os.chdir(PORTAL_DIR)
    sys.path.insert(0, PORTAL_DIR)
    os.environ["PORTAL_DESKTOP"] = "1"
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=port,
        log_level="warning",
        access_log=False,
    )

def wait_for_server(port, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.3)
    return False

# ============================================================
# PyQt5 桌面窗口
# ============================================================
def create_window(port):
    from PyQt5.QtCore import QUrl, Qt
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QToolBar, QAction,
        QLineEdit, QStatusBar, QMessageBox, QVBoxLayout,
        QWidget
    )
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

    app = QApplication(sys.argv)
    app.setApplicationName("Portal Desktop")
    app.setApplicationVersion("1.0")

    # ---- 主窗口 ----
    window = QMainWindow()
    window.setWindowTitle("✨ Portal - 多系统智能门户")
    window.resize(1400, 900)
    window.setMinimumSize(1024, 700)

    # ---- 工具栏 ----
    toolbar = QToolBar("导航栏")
    toolbar.setMovable(False)
    toolbar.setStyleSheet("""
        QToolBar {
            background: #0a0a1a;
            border-bottom: 1px solid rgba(0,245,255,0.2);
            padding: 4px 8px;
            spacing: 4px;
        }
        QToolButton {
            color: #e0e0ff;
            background: transparent;
            border: 1px solid transparent;
            border-radius: 6px;
            padding: 4px 12px;
            font-size: 13px;
        }
        QToolButton:hover {
            background: rgba(0,245,255,0.1);
            border-color: rgba(0,245,255,0.3);
        }
    """)
    window.addToolBar(toolbar)

    # ---- WebView ----
    webview = QWebEngineView()
    window.setCentralWidget(webview)

    # ---- 地址栏 ----
    url_bar = QLineEdit()
    url_bar.setReadOnly(True)
    url_bar.setStyleSheet("""
        QLineEdit {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(0,245,255,0.2);
            border-radius: 8px;
            color: #e0e0ff;
            padding: 4px 12px;
            font-size: 12px;
        }
    """)
    url_bar.setMaximumWidth(400)

    # ---- 导航按钮 ----
    def go_home():
        webview.load(QUrl(f"http://127.0.0.1:{port}/dashboard"))

    def go_back():
        webview.back()

    def go_forward():
        webview.forward()

    def reload_page():
        webview.reload()

    # 添加导航动作
    actions = [
        ("⬅ 后退", go_back),
        ("➡ 前进", go_forward),
        ("🔄 刷新", reload_page),
        ("🏠 主页", go_home),
    ]
    for label, callback in actions:
        action = QAction(label, window)
        action.triggered.connect(callback)
        toolbar.addAction(action)

    toolbar.addWidget(url_bar)

    # 状态栏
    status = QStatusBar()
    status.setStyleSheet("""
        QStatusBar {
            background: #0a0a1a;
            color: rgba(200,200,255,0.5);
            border-top: 1px solid rgba(0,245,255,0.1);
            font-size: 11px;
        }
    """)
    window.setStatusBar(status)
    status.showMessage("✓ 系统就绪 | Portal Desktop v1.0")

    # URL 更新
    def on_url_changed(qurl):
        url_bar.setText(qurl.toString())

    webview.urlChanged.connect(on_url_changed)

    # 加载首页
    base_url = f"http://127.0.0.1:{port}"
    webview.load(QUrl(base_url + "/"))

    # 关闭事件
    def close_event(event):
        reply = QMessageBox.question(
            window, "退出", "确定要退出 Portal Desktop 吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    window.closeEvent = close_event

    # 显示窗口
    window.show()

    # 运行
    sys.exit(app.exec_())

# ============================================================
# 主入口
# ============================================================
def main():
    print("=" * 60)
    print("  ✨ Portal Desktop")
    print("  多系统智能门户 - 桌面版")
    print("=" * 60)

    port = find_free_port(DESKTOP_PORT)
    print(f"[1/3] 端口: {port}")

    print("[2/3] 启动后端服务器...")
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()

    print("[3/3] 等待服务器就绪...")
    if not wait_for_server(port):
        print("  ✗ 服务器启动失败")
        sys.exit(1)
    print(f"  ✓ 服务器就绪: http://127.0.0.1:{port}")
    print("=" * 60)

    create_window(port)


if __name__ == "__main__":
    main()
