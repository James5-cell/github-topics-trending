# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-01-27

### 首次发布

**GitHub Topics Trending** - 追踪 GitHub 话题下的热门项目，AI 智能分析，每日趋势报告邮件

### 核心功能

- **GitHub API 数据采集**
  - 使用 GitHub Search API 按话题获取热门仓库
  - 支持自定义话题（默认：claude-code）
  - 可配置排序方式（stars/forks/updated）
  - 分页获取，支持最多 1000 个仓库
  - API 速率限制处理

- **README 内容获取**
  - 自动获取仓库 README 摘要
  - 支持 Markdown 纯文本提取
  - 批量获取，智能限流

- **Claude AI 智能分析**
  - 批量总结和分类热门仓库
  - 提取摘要、描述、使用场景
  - 智能分类（plugin/tool/template/docs/demo/integration/library/app/other）
  - 提取解决的问题标签
  - 技术栈识别

- **趋势计算引擎**
  - 星标变化计算（增长/下降）
  - 星标变化率计算
  - 新晋榜单检测
  - 跌出榜单检测
  - 活跃项目检测（最近更新）
  - 暴涨告警（可配置阈值）

- **SQLite 数据存储**
  - 3 张表：repos_daily、repos_details、repos_history
  - 可配置数据保留天数（默认 90 天）
  - 支持趋势查询和统计
  - 分类统计、语言统计

- **专业 HTML 邮件报告**
  - 简洁专业的设计风格
  - 每个仓库可点击跳转到 GitHub
  - Top 20 榜单（含 AI 总结）
  - 星标增长 Top 5
  - 新晋项目展示
  - 活跃项目展示
  - 趋势统计概览

- **GitHub Pages 静态网站**
  - 响应式设计
  - 首页展示 Top 20
  - 趋势页面（按日期归档）
  - 分类浏览页面
  - 仓库详情页面
  - 主题配色支持

- **Resend 邮件发送**
  - 可靠的邮件发送服务
  - 支持自定义发件人

### 技术栈

- Python 3.11+
- GitHub API（数据采集）
- SQLite（数据存储）
- Claude API（AI 分析）
- Resend（邮件服务）

### GitHub Actions

- 每天 UTC 02:00（北京时间 10:00）自动运行
- 支持手动触发
- 自动部署到 GitHub Pages
- 数据库自动备份（保留 30 天）

### 文件结构

```
github-topics-trending/
├── .github/workflows/
│   └── github-trending.yml     # GitHub Actions 配置
├── src/
│   ├── config.py               # 配置管理
│   ├── database.py             # SQLite 操作
│   ├── github_fetcher.py       # GitHub API 采集
│   ├── readme_fetcher.py       # README 获取
│   ├── claude_summarizer.py    # AI 分析
│   ├── trend_analyzer.py       # 趋势计算
│   ├── email_reporter.py       # 邮件生成
│   ├── web_generator.py        # 网站生成
│   ├── resend_sender.py        # 邮件发送
│   └── main.py                 # 主入口
├── plugins/
│   └── github-topics/          # Claude Code Skill
├── docs/                       # GitHub Pages 输出
├── data/
│   └── github-trending.db      # 数据库（运行时生成）
├── requirements.txt
├── .env.example
├── CHANGELOG.md
└── README.md
```

### 环境变量

```bash
# GitHub API
GITHUB_TOKEN=ghp_xxx
GITHUB_TOPIC=claude-code

# Claude API
ZHIPU_API_KEY=xxx
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic

# Resend 邮件
RESEND_API_KEY=re_xxx
EMAIL_TO=your@email.com
RESEND_FROM_EMAIL=onboarding@resend.dev

# 数据库
DB_PATH=data/github-trending.db
DB_RETENTION_DAYS=90

# 告警阈值
SURGE_THRESHOLD=0.3
```

### 仓库分类

| 分类 | 说明 |
|-----|------|
| plugin | Claude Code / VS Code 插件 |
| tool | 开发工具、CLI 工具 |
| template | 项目模板、脚手架 |
| docs | 教程、文档、书籍 |
| demo | Demo 项目、示例代码 |
| integration | 集成工具、包装器 |
| library | Python/JS/其他库 |
| app | 完整应用 |
| other | 无法分类 |

### 重构说明

本项目是从 **Skills Trending Daily** 完全重构而来：

- **数据源变更**: skills.sh → GitHub Topics API
- **指标变更**: 安装量 → 星标数
- **新增功能**: GitHub Pages 静态网站生成
- **删除依赖**: Playwright、BeautifulSoup
- **新增配置**: 话题可配置

---

[1.0.0]: https://github.com/geekjourneyx/github-topics-trending/releases/tag/v1.0.0
