# 多系统智能门户 v5.0

## 📱 移动端下载

### 方式一：Web App（推荐，iOS 和 Android 通用）

直接在浏览器打开服务器地址，然后添加到主屏幕：

**iOS (Safari)**:
1. 打开 `http://192.168.31.156:8080`
2. 点击底部 **分享按钮** (⬆️)
3. 滑到 **"添加到主屏幕"**
4. 点击添加

**Android (Chrome)**:
1. 打开 `http://192.168.31.156:8080`
2. 点击右上角 **⋮** 菜单
3. 选择 **"添加到主屏幕"** 或 **"安装应用"**

添加到主屏幕后，会像原生 App 一样全屏运行，支持离线缓存。

### 方式二：Android APK 直接安装

下载: [portal-android-v1.0.0.apk](https://github.com/qi2834319625-sys/llmapp/raw/android-app/android/releases/portal-android-v1.0.0.apk)

安装步骤:
1. 下载 APK 到手机
2. 设置 → 安全 → 允许"未知来源"安装
3. 安装后打开，输入用户名密码登录

### 方式三：iOS 源码编译

`ios/` 目录包含完整 SwiftUI 项目，需要 Mac + Xcode 编译安装。

## 🔐 登录说明

- 服务器地址已内置，用户无需填写
- 只需输入用户名和密码
- App 会记住用户名，**不记住密码**（安全考虑）
- 默认账号: `qmlaizyh` / `qwe123123`

## 🖥️ 服务端部署

```bash
cd portal
bash deploy.sh
# 访问 http://localhost:8080
```

## 📂 代码结构

```
llmapp/
├── portal/          # Python FastAPI 服务端
│   ├── static/      # 静态文件 + PWA manifest + icons
│   └── templates/   # HTML 模板 (含 PWA meta 标签)
├── android/         # Kotlin Android 客户端
│   └── releases/    # APK 下载
└── ios/             # SwiftUI iOS 客户端
```

## 功能模块 (13个)

💕 情侣空间 | 💼 秋招备战 | 🔐 密码学论文 | 🧠 GNN匹配 | 📈 投资理财
💄 美妆系统 | 👗 服装搭配 | 🍳 美食厨房 | ✈️ 出国规划 | 📚 考公备考
📝 CET考试 | 🎭 漫剧创作 | ⚙️ 系统设置
