# 多系统智能门户 v5.0

## 📱 Android 客户端

下载 APK: [portal-android-v1.0.0.apk](https://github.com/qi2834319625-sys/llmapp/raw/android-app/android/releases/portal-android-v1.0.0.apk)

安装方式:
1. 下载 APK 文件
2. 在手机设置中允许"未知来源"安装
3. 打开 APK 安装
4. 首次启动输入服务器地址: `http://192.168.31.156:8080`
5. 账号: `qmlaizyh` / `qwe123123`

源码: [android-app 分支](https://github.com/qi2834319625-sys/llmapp/tree/android-app/android)

## 快速部署

```bash
# 1. 解压文件
tar -xzf portal-v5.tar.gz
cd portal

# 2. 一键部署
bash deploy.sh

# 3. 访问
# 浏览器打开 http://localhost:8080
# 用户名: qmlaizyh  密码: qwe123123
```

## 系统架构

- **后端**: FastAPI + Jinja2 + SQLite
- **前端**: 原生 HTML/CSS/JS + Canvas 2D
- **端口**: 8080
- **数据库**: SQLite (data/portal.db)

## 18个功能模块

| 模块 | 路径 | 功能 |
|------|------|------|
| 控制台 | /dashboard | 系统监控+快捷入口+活动流 |
| 系统设置 | /settings | 8Tab完整设置中心 |
| 投资管理 | /investment | K线图+技术指标+量化回测 |
| 求职刷题 | /recruitment | 面试追踪+漏斗图+日历 |
| 密码学论文 | /crypto | 引用图谱+笔记系统 |
| 密钥协商论文 | /papers | 15分类+LLM总结+文献综述 |
| 数据搜集 | /crawler | 5源爬虫+智能分类 |
| 大模型知识库 | /knowledge | AI问答+每日更新+全局搜索 |
| 策略实验室 | /strategy-lab | Python沙箱+5模板+回测 |
| AI音乐生成 | /ai-music | 4引擎+钢琴+音乐库 |
| 情侣空间 | /couple | 9Tab+心情日记+纪念日 |
| 漫剧创作 | /manga | 角色+分镜+批量生成 |
| 美妆指南 | /makeup | 教程+肤质测试+色彩分析 |
| 时尚穿搭 | /fashion | 衣橱+搭配+趋势 |
| 烹饪食谱 | /cooking | 食谱+分类+搜索 |
| 出国留学 | /study-abroad | 院校+对比+时间线 |
| 公务员考试 | /civil-exam | 考点+模拟+评分 |
| CET考试 | /cet-exam | 单词+模拟+游戏 |

## 数据库表 (42张)

- 用户数据: users, user_notes, user_bookmarks, user_settings, user_activities, user_files
- 投资策略: strategy_strategies, strategy_backtests
- AI音乐: ai_music_tracks
- 论文系统: paper_categories, papers, paper_notes, paper_relations, literature_reviews, paper_download_queue
- 知识库: knowledge_categories, knowledge_items, knowledge_daily_updates, knowledge_search_log, knowledge_chat_history
- 爬虫: crawl_sources, crawl_logs, crawl_schedule, paper_fetch_queue
- 其他: cet_exam, civil_exam, recipes, fashion_items, makeup_tips, study_abroad, couple_*, gnn_*, crypto_papers, github_repos, youtube_resources

## API路由 (62+)

- 认证: POST /login, GET /logout
- 投资: POST /api/backtest, GET /api/market/*
- 知识库: GET/POST /api/knowledge/*, POST /api/knowledge/chat
- 全局搜索: GET /api/search
- 系统: GET /api/system/health, GET /api/user/stats
- 爬虫: GET/POST /api/crawler/*
- 论文: GET/POST /api/papers/*
- 策略: POST /api/strategy/run, POST /api/user/strategies
- 音乐: POST /api/ai-music/generate, GET /api/ai-music/library

## 目录结构

```
portal/
├── app.py              # 主程序 (1747行)
├── database.py         # 数据库操作 (295行)
├── crawler.py          # 爬虫引擎 (521行)
├── paper_api.py        # 论文API (436行)
├── crawler_api.py      # 爬虫API (185行)
├── knowledge_api.py    # 知识库API (239行)
├── seed_data.py        # 种子数据
├── seed_cet.py         # CET种子数据
├── templates/          # 20个HTML模板
│   ├── base.html       # 基础模板
│   ├── dashboard.html  # 控制台
│   ├── settings.html   # 系统设置
│   ├── knowledge.html  # 知识库
│   └── ...             # 其他16个模板
├── static/             # 静态文件
│   ├── css/cybertech.css   # 科技感CSS框架
│   ├── js/cybertech.js     # 粒子动画+Toast
│   ├── audio/              # 背景音乐
│   └── papers/             # 论文PDF
├── data/portal.db      # SQLite数据库
├── venv/               # 虚拟环境
├── requirements.txt    # Python依赖
├── deploy.sh           # 一键部署脚本
└── README.md           # 本文件
```

## 注意事项

1. 首次运行会自动创建数据库和种子数据
2. 外部API (HuggingFace/Stable Audio/Suno) 需要配置 API Key
3. 生产环境建议修改默认密码
4. 数据库文件 data/portal.db 需要定期备份
