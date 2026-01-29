# GitHub Topics Trending

> 追踪 GitHub 话题下的热门项目，AI 智能分析，每日趋势报告邮件

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [GitHub Actions](#github-actions)
- [数据模型](#数据模型)
- [开发指南](#开发指南)
- [常见问题](#常见问题)

---

## 项目简介

**GitHub Topics Trending** 是一个自动化仓库趋势追踪系统。它每天通过 GitHub API 获取指定话题下的热门仓库，使用 Nvidia NIM AI (Llama 3等) 对仓库进行智能分析和分类，计算星标变化趋势，并通过 Resend 发送专业的 HTML 邮件报告，同时生成 GitHub Pages 静态网站。

### 为什么需要这个项目？

1. **开发者视角** - 快速了解特定话题下的热门项目
2. **趋势洞察** - 捕捉新兴项目和工具的崛起
3. **智能总结** - AI 帮你理解每个项目解决什么问题
4. **自动化** - 无需手动查看网站，每天自动推送

---

## 功能特性

### 核心功能

| 功能 | 说明 |
|-----|------|
| **GitHub API 采集** | 按话题获取热门仓库，支持自定义排序 |
| **README 获取** | 自动获取仓库 README 摘要 |
| **AI 分析** | Claude AI 自动总结、分类、提取价值 |
| **趋势计算** | 星标变化、新晋/掉榜、活跃项目检测 |
| **邮件报告** | 专业 HTML 邮件，每个仓库可点击跳转 |
| **静态网站** | 生成 GitHub Pages 可视化页面 |
| **数据存储** | SQLite 存储历史数据，支持趋势分析 |

### 邮件报告内容

```
GitHub Topics Daily - 2026-01-27
├── Top 20 经典榜单（含 AI 总结）
│   ├── 仓库名称（可点击跳转）、排名、星标数
│   ├── AI 一句话摘要
│   ├── 详细说明
│   └── 解决的问题标签
├── 星标增长 Top 5
├── 新晋项目
├── 活跃项目
└── 趋势统计
```

### 仓库分类

| 分类 | 说明 |
|-----|------|
| **插件** | Claude Code / VS Code 插件 |
| **工具** | 开发工具、CLI 工具 |
| **模板** | 项目模板、脚手架 |
| **文档** | 教程、文档、书籍 |
| **示例** | Demo 项目、示例代码 |
| **集成** | 集成工具、包装器 |
| **库** | Python/JS/其他库 |
| **应用** | 完整应用 |

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Topics Trending                      │
└─────────────────────────────────────────────────────────────────┘

  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
  │   GitHub     │      │   GitHub     │      │    Claude    │
  │   Actions    │ ──▶ │   Fetcher    │ ──▶ │  Summarizer │
  │  (Cron Daily)│      │  (API)       │      │     AI       │
  └──────────────┘      └──────┬───────┘      └──────┬───────┘
                               │                     │
                               ▼                     │
                        ┌──────────────┐              │
                        │   README     │              │
                        │  Fetcher     │              │
                        └──────┬───────┘              │
                               │                       │
                               └───────┬───────────────┘
                                       │
                                       ▼
                               ┌──────────────┐
                               │  Database    │
                               │  (SQLite)    │
                               └──────┬───────┘
                                      │
                                      ▼
                               ┌──────────────┐
                               │   Trend      │
                               │  Analyzer    │
                               └──────┬───────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
             ┌──────────────┐                   ┌──────────────┐
             │   Email      │                   │    Web       │
             │  Reporter    │                   │  Generator   │
             └──────┬───────┘                   └──────┬───────┘
                    │                                   │
                    ▼                                   ▼
             ┌──────────────┐                   ┌──────────────┐
             │   Resend     │                   │  GitHub      │
             │   Sender     │                   │   Pages      │
             └──────┬───────┘                   └──────────────┘
                    │
                    ▼
                   ──────► 您的邮箱
```

---

## 快速开始

### 环境要求

- Python 3.11+
- GitHub Personal Access Token
- Nvidia API Key (支持 NIM)
- Resend API Key

### 安装

```bash
# 克隆仓库
git clone https://github.com/geekjourneyx/github-topics-trending.git
cd github-topics-trending

# 安装依赖
pip install -r requirements.txt
```

### 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Keys
nano .env
```

### 运行

```bash
# 设置环境变量
export GH_TOKEN="your_github_token"
export ZHIPU_API_KEY="your_api_key"
export RESEND_API_KEY="your_resend_key"
export EMAIL_TO="your_email@example.com"

# 运行（完整流程）
python -m src.main

# 仅获取数据，不发送邮件
python -m src.main --fetch-only
```

**注意**: 环境变量已配置为使用 `GH_TOKEN` 和 `TOPIC`，避免以 `GITHUB_` 开头的 Secret 名称。

```bash
# 设置环境变量
export GH_TOKEN="your_github_token"
export TOPIC="claude-code"

---

## 配置说明

### 环境变量

| 变量 | 必需 | 说明 | 默认值 |
|-----|------|------|--------|
| `GH_TOKEN` | Yes | GitHub Personal Access Token | - |
| `TOPIC` | No | 要追踪的 GitHub Topic | `claude-code` |
| `NVIDIA_API_KEY` | Yes | Nvidia API Key | - |
| `NVIDIA_BASE_URL` | No | Nvidia API Base URL | `https://integrate.api.nvidia.com/v1` |
| `NVIDIA_MODEL` | No | 使用的模型 | `meta/llama3-70b-instruct` |
| `RESEND_API_KEY` | Yes | Resend API Key | - |
| `EMAIL_TO` | Yes | 收件人邮箱 | - |
| `RESEND_FROM_EMAIL` | No | 发件人邮箱 | `onboarding@resend.dev` |
| `DB_PATH` | No | 数据库路径 | `data/github-trending.db` |
| `DB_RETENTION_DAYS` | No | 数据保留天数 | `90` |
| `SURGE_THRESHOLD` | No | 暴涨阈值（比例） | `0.3` |

### GitHub Token 配置

#### 申请 Personal Access Token (PAT)

1. 登录 GitHub
2. 点击头像 → **Settings**
3. 左侧菜单最下方 → **Developer settings**
4. **Personal access tokens** → **Tokens (classic)**
5. **Generate new token** → **Generate new token (classic)**
6. 配置 Token：
   - **Note**: 输入 `GitHub Topics Bot`
   - **Expiration**: 选择有效期（建议 `90 days` 或 `No expiration`）
   - **勾选权限**:
     - ☑️ `public_repo` (访问公共仓库)
   - 点击 **Generate token**
7. 复制 token（只显示一次！请妥善保存）

#### 在 GitHub Actions 中配置

1. 进入 GitHub 仓库页面
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret**
4. 配置:
   - **Name**: `GITHUB_TOKEN`
   - **Value**: 粘贴你的 token
5. 点击 **Add secret**

### Resend 配置

1. 注册 [Resend](https://resend.com)
2. 创建 API Key
3. 配置发件人域名（或使用默认的 `onboarding@resend.dev`）

---

## 使用方法

### 命令行运行

```bash
# 完整流程（获取数据 + AI 分析 + 发送邮件 + 生成网站）
python -m src.main

# 仅获取数据
python -m src.main --fetch-only
```

### 数据库查询

```bash
# 查看最新数据日期
sqlite3 data/github-trending.db "SELECT date FROM repos_daily ORDER BY date DESC LIMIT 1;"

# 查看今日排行榜 Top 10
sqlite3 data/github-trending.db "SELECT rank, repo_name, stars FROM repos_daily WHERE date = '2026-01-27' ORDER BY rank LIMIT 10;"

# 查看仓库详情
sqlite3 data/github-trending.db "SELECT repo_name, summary, category FROM repos_details WHERE repo_name = 'anthropics/claude-code';"
```

---

## GitHub Pages 配置

### 启用 GitHub Pages

#### 第一步：配置 Pages

1. 进入仓库 **Settings** → **Pages**

2. **Build and deployment** 配置：
   - **Source**: **Deploy from a branch**
   - **Branch**: **gh-pages** 分支
   - **Folder**: **/ (root)**
   - 点击 **Save**

#### 第二步：确保仓库为 Public

1. 仓库 **Settings** → **General**
2. 滚动到底部 **Danger Zone**
3. **Change repository visibility** → 选择 **Public**
4. 确认更改

#### 第三步：访问网站

```
https://geekjourneyx.github.io/github-topics-trending/
```

⚠️ **注意**：首次部署后需要等待 **5-10 分钟**才能访问。

---

## GitHub Actions 配置

### Secrets 配置

1. **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

2. 添加以下 Secrets：

| Name | 必需 | Value |
|------|------|-------|
| `GH_TOKEN` | ✅ | 你的 GitHub PAT |
| `TOPIC` | - | `claude-code`（追踪的话题） |
| `ZHIPU_API_KEY` | ✅ | 智谱 API Key |
| `RESEND_API_KEY` | ✅ | Resend API Key |
| `EMAIL_TO` | ✅ | 接收日报的邮箱 |

### Actions 权限配置

1. **Settings** → **Actions** → **General**
2. **Workflow permissions** → 选择 **Read and write permissions**
3. 点击 **Save**

### 手动触发

1. 点击 **Actions** 标签
2. 选择 **GitHub Topics Trending** workflow
3. 点击 **Run workflow** → **Run workflow**

### 定时执行

默认每天 **UTC 02:00**（北京时间 10:00）自动运行。

---

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| 404 错误 | 确保仓库为 Public，等待 5-10 分钟让 GitHub Pages 生效 |
| 403 Permission denied | 检查 Workflow permissions 是否为 Read and write |
| Actions 失败 | 查看 Actions 日志，检查 Secrets 是否配置正确 |
| 网站内容不是最新 | GitHub Pages 有缓存，强制刷新 `Ctrl+Shift+R` 或加 `?v=123` |

---

## 数据模型

### repos_daily - 每日快照

| 字段 | 类型 | 说明 |
|-----|------|------|
| `id` | INTEGER | 主键 |
| `date` | TEXT | 日期 (YYYY-MM-DD) |
| `rank` | INTEGER | 当日排名 |
| `repo_name` | TEXT | 仓库名称 (owner/repo) |
| `owner` | TEXT | 拥有者 |
| `stars` | INTEGER | 星标数 |
| `stars_delta` | INTEGER | 星标变化 |
| `forks` | INTEGER | Fork 数 |
| `issues` | INTEGER | Issue 数 |
| `language` | TEXT | 主要语言 |
| `url` | TEXT | 仓库链接 |

### repos_details - 仓库详情

| 字段 | 类型 | 说明 |
|-----|------|------|
| `id` | INTEGER | 主键 |
| `repo_name` | TEXT | 仓库名称（唯一） |
| `summary` | TEXT | AI 一句话摘要 |
| `description` | TEXT | 详细描述 |
| `use_case` | TEXT | 使用场景 |
| `solves` | TEXT | JSON：解决的问题列表 |
| `category` | TEXT | 分类（英文） |
| `category_zh` | TEXT | 分类（中文） |
| `topics` | TEXT | JSON：GitHub topics |
| `language` | TEXT | 主要语言 |
| `readme_summary` | TEXT | README 摘要 |
| `owner` | TEXT | 拥有者 |
| `url` | TEXT | 仓库链接 |

### repos_history - 历史趋势

| 字段 | 类型 | 说明 |
|-----|------|------|
| `id` | INTEGER | 主键 |
| `repo_name` | TEXT | 仓库名称 |
| `date` | TEXT | 日期 |
| `rank` | INTEGER | 当日排名 |
| `stars` | INTEGER | 星标数 |
| `forks` | INTEGER | Fork 数 |

---

## 开发指南

### 项目结构

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

### 核心模块说明

| 模块 | 功能 |
|-----|------|
| `github_fetcher.py` | 使用 GitHub API 按话题获取仓库 |
| `readme_fetcher.py` | 获取仓库 README 内容 |
| `claude_summarizer.py` | 调用 Claude API 分析仓库 |
| `trend_analyzer.py` | 计算星标变化、新晋/掉榜、活跃检测 |
| `email_reporter.py` | 生成专业 HTML 邮件 |
| `web_generator.py` | 生成 GitHub Pages 静态网站 |
| `database.py` | SQLite 数据库操作 |

### 扩展开发

**新增话题**
```bash
# 修改 .env 或环境变量
export GITHUB_TOPIC="python"
```

**新增分析维度**
```python
# 修改 trend_analyzer.py
def calculate_trends(self, today_repos, date, ai_summary_map):
    # 添加新的分析逻辑
    pass
```

**自定义邮件样式**
```python
# 修改 email_reporter.py
def _get_header(self, date: str) -> str:
    # 修改样式和布局
    pass
```

---

## 常见问题

### 邮件没有收到？

1. 检查 Resend API Key 是否正确
2. 确认收件人邮箱地址
3. 查看垃圾邮件箱
4. 检查 GitHub Actions 日志

### GitHub API 速率限制？

- 认证用户：5000 requests/hour
- 未认证用户：60 requests/hour
- 使用 `GITHUB_TOKEN` 环境变量可提高限制

### 数据库文件在哪里？

默认位置：`data/github-trending.db`

### 如何查看历史数据？

```bash
sqlite3 data/github-trending.db
.tables
SELECT * FROM repos_daily ORDER BY date DESC LIMIT 10;
```

### 如何更改运行时间？

编辑 `.github/workflows/github-trending.yml`：
```yaml
schedule:
  - cron: '0 2 * * *'  # UTC 时间，每天 02:00
```

### 如何更换追踪的话题？

修改环境变量 `TOPIC`：
```bash
export TOPIC="your-topic"
```

---

## 打赏 Buy Me A Coffee

如果该项目帮助了您，请作者喝杯咖啡吧

### WeChat

<img src="https://raw.githubusercontent.com/geekjourneyx/awesome-developer-go-sail/main/docs/assets/wechat-reward-code.jpg" alt="微信打赏码" width="200" />

---

## 作者

- **作者**: `geekjourneyx`
- **X (Twitter)**: https://x.com/seekjourney
- **公众号**: 极客杰尼

关注公众号，获取更多 AI 编程、AI 工具与 AI 出海建站的实战分享：

<p>
<img src="https://raw.githubusercontent.com/geekjourneyx/awesome-developer-go-sail/main/docs/assets/qrcode.jpg" alt="公众号：极客杰尼" width="180" />
</p>

---

## License

[MIT](LICENSE)

---

## 致谢

- [GitHub](https://github.com) - 数据来源
- [Anthropic](https://anthropic.com) - Claude AI
- [Resend](https://resend.com) - 邮件服务
