# 多系统智能门户 v5.0

## 📱 移动端下载

### Android APK
直接下载: [portal-android-v1.0.0.apk](https://github.com/qi2834319625-sys/llmapp/raw/android-app/android/releases/portal-android-v1.0.0.apk)

安装步骤:
1. 下载 APK 到手机
2. 设置 → 安全 → 允许"未知来源"安装
3. 安装后打开，输入用户名密码登录
4. 服务器地址已内置，无需填写

### iOS
源码: `ios/` 目录，需要用 Xcode 编译安装
1. 安装 Xcode (Mac App Store)
2. 打开 `ios/PortalApp.xcodeproj`
3. 连接手机，选择设备，点击 Run
4. 首次运行需要在 设置 → 通用 → 设备管理 中信任开发者

## 🔐 登录说明

- 服务器地址已内置（`http://192.168.31.156:8080`），用户无需填写
- 只需输入用户名和密码
- App 会记住用户名，不记住密码（安全考虑）

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
├── android/         # Kotlin Android 客户端  
│   └── releases/    # APK 下载
└── ios/             # SwiftUI iOS 客户端
```

## 功能模块 (13个)

| 模块 | Android | iOS |
|------|---------|-----|
| 💕 情侣空间 | ✅ | 🔲 |
| 💼 秋招备战 | ✅ | 🔲 |
| 🔐 密码学论文 | ✅ | 🔲 |
| 🧠 GNN匹配 | ✅ | 🔲 |
| 📈 投资理财 | ✅ | 🔲 |
| 💄 美妆系统 | ✅ | 🔲 |
| 👗 服装搭配 | ✅ | 🔲 |
| 🍳 美食厨房 | ✅ | 🔲 |
| ✈️ 出国规划 | ✅ | 🔲 |
| 📚 考公备考 | ✅ | 🔲 |
| 📝 CET考试 | ✅ | 🔲 |
| 🎭 漫剧创作 | ✅ | 🔲 |
| ⚙️ 系统设置 | ✅ | ✅ |

✅ 已完成  🔲 待开发
