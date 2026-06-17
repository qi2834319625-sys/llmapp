# Portal Android App 📱

多系统智能门户 - 安卓客户端

## 功能模块 (13个)

1. 💕 情侣空间 - 照片、视频、故事、时间线、情书、心愿单
2. 💼 秋招备战 - LeetCode题库、GitHub仓库、YouTube资源
3. 🔐 密码学论文 - 论文搜索、分类筛选
4. 🧠 GNN结构化匹配 - 实体关系图管理
5. 📈 投资理财 - 投资记录、收益追踪
6. 💄 美妆系统 - 美妆技巧、分类浏览
7. 👗 服装搭配 - 服装管理、季节风格筛选
8. 🍳 美食厨房 - 菜谱搜索、菜系难度筛选
9. ✈️ 出国规划 - 留学项目、国家筛选
10. 📚 考公备考 - 考点管理、科目筛选
11. 📝 CET考试 - CET-4/6 题库、章节筛选
12. 🎭 漫剧创作 - 项目管理、AI生图/视频
13. ⚙️ 系统设置 - 服务器配置、账号管理

## 技术栈

- **语言**: Kotlin
- **架构**: MVVM + Repository模式
- **网络**: OkHttp + Gson
- **图片**: Glide
- **UI**: Material Design 3 + ViewBinding
- **最低SDK**: 26 (Android 8.0)

## 安装

1. 下载 APK: `app-debug.apk`
2. 安装到手机 (允许"未知来源"安装)
3. 首次启动输入服务器地址和账号密码

## 服务器配置

默认服务器地址: `http://192.168.31.156:8080`
默认账号: `qmlaizyh` / `qwe123123`

## 构建

```bash
export ANDROID_HOME=/opt/android-sdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
./gradlew assembleDebug
```

输出: `app/build/outputs/apk/debug/app-debug.apk`
