# Portal Desktop

多系统智能门户 - 桌面版

## 技术栈

- **PyQt5** + **QWebEngineView** — 桌面窗口 + 内嵌浏览器引擎
- **FastAPI** + **Uvicorn** — 内嵌 HTTP 服务器
- **复用全部现有前端** — templates/ + static/，UI 完全一致

## 包含模块（13个）

1. 💕 情侣空间
2. 💼 秋招备战系统
3. 🔐 密码学论文系统
4. 🧠 GNN结构化匹配
5. 📈 投资理财
6. 💄 美妆系统
7. 👗 服装搭配
8. 🍳 美食厨房
9. ✈️ 出国规划
10. 📚 考公备考
11. 📝 CET考试
12. 🎭 漫剧创作
13. ⚙️ 系统设置

**不包含**：密钥协商论文库、数据搜集中心、知识库（这些是后加的论文系统）

## 启动方式

```bash
cd /root/portal
chmod +x desktop/run.sh
./desktop/run.sh
```

或者直接：

```bash
source venv/bin/activate
cd /root/portal
python3 desktop/app.py
```

## 打包为独立可执行文件

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Portal Desktop" desktop/app.py
```
