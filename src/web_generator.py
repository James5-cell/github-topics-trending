"""
Web Generator - GitHub Pages 静态网站生成器
生成 GitHub Topics Trending 的静态网站页面 (Minimalist Design)
"""
import os
import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path

from src.config import OUTPUT_DIR, TOPIC, SITE_META, get_theme, CATEGORIES, format_number, BASE_URL


class WebGenerator:
    """GitHub Pages 静态网站生成器"""

    def __init__(self, output_dir: str = None, theme: str = "blue"):
        """
        初始化
        """
        self.output_dir = Path(output_dir or OUTPUT_DIR)
        # 忽略传入的主题，强制使用极简风格
        self.topic = TOPIC
        self.meta = SITE_META
        
        # 确保 url_prefix 不以 / 结尾，但以 / 开头（除非为空）
        self.url_prefix = BASE_URL.rstrip('/')
        if self.url_prefix and not self.url_prefix.startswith('/'):
            self.url_prefix = '/' + self.url_prefix

        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 创建子目录
        (self.output_dir / "trending").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "category").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "repo").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "assets" / "css").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "assets" / "js").mkdir(parents=True, exist_ok=True)

    def generate_all(self, trends: Dict, date: str, db) -> List[str]:
        """生成所有页面"""
        files = []

        # 首页
        index_path = self.generate_index(trends, date)
        files.append(index_path)

        # 趋势页
        trending_path = self.generate_trending_page(trends, date)
        files.append(trending_path)

        # 分类页
        category_files = self.generate_category_pages(db)
        files.extend(category_files)

        # 静态资源
        css_path = self.generate_css()
        files.append(css_path)

        print(f"✅ 生成网站文件: {len(files)} 个")

        return files

    def generate_index(self, trends: Dict, date: str) -> str:
        """生成首页"""
        top_20 = trends.get("top_20", [])[:20]

        content = self._get_base_html(f"Home", """
        <header class="hero">
            <div class="hero-content">
                <span class="hero-label">Daily Trending</span>
                <h1 class="hero-title">{title}</h1>
                <p class="hero-subtitle">{subtitle}</p>
                <div class="hero-meta">
                    <span class="date-badge">{date}</span>
                    <span class="topic-badge">#{topic}</span>
                </div>
            </div>
        </header>

        <div class="container">
            <section class="section">
                <div class="section-header">
                    <h2 class="section-title">Top 20 Selection</h2>
                    <p class="section-desc">AI-curated essentials for today.</p>
                </div>
                <div class="repo-grid">
                    {repo_cards}
                </div>
            </section>

            <section class="section">
                <div class="section-header">
                    <h2 class="section-title">Browse by Category</h2>
                </div>
                <div class="category-grid">
                    {category_cards}
                </div>
            </section>
        </div>
        """.format(
            title=self.meta['title'],
            subtitle=self.meta['subtitle'],
            date=date,
            topic=self.topic,
            repo_cards="".join(self._format_repo_card(repo) for repo in top_20),
            category_cards="".join(self._format_category_card(cat) for cat in CATEGORIES.values())
        ))

        path = self.output_dir / "index.html"
        path.write_text(content, encoding="utf-8")
        return str(path)

    def generate_trending_page(self, trends: Dict, date: str) -> str:
        """生成趋势页"""
        content = self._get_base_html(f"Trending - {date}", f"""
        <header class="page-header container">
            <h1 class="page-title">Trends Report</h1>
            <p class="page-subtitle">{date}</p>
        </header>

        <div class="container">
            <div class="trend-grid">
                <div class="trend-column">
                    <h2 class="column-title">🔥 Rising Stars</h2>
                    <div class="repo-list">
                        {"".join(self._format_repo_list_item(repo) for repo in trends.get("rising_top5", []))}
                    </div>
                </div>

                <div class="trend-column">
                    <h2 class="column-title">✨ New Arrivals</h2>
                    <div class="repo-list">
                        {"".join(self._format_repo_list_item(repo) for repo in trends.get("new_entries", [])[:10])}
                    </div>
                </div>
                
                <div class="trend-column">
                    <h2 class="column-title">⚡ Active Today</h2>
                    <div class="repo-list">
                        {"".join(self._format_repo_list_item(repo) for repo in trends.get("active", []))}
                    </div>
                </div>
            </div>
        </div>
        """)

        filename = f"{date}.html"
        path = self.output_dir / "trending" / filename
        path.write_text(content, encoding="utf-8")

        # 同时创建最新的链接
        latest_path = self.output_dir / "trending" / "latest.html"
        latest_path.write_text(content, encoding="utf-8")

        return str(path)

    def generate_category_pages(self, db) -> List[str]:
        """生成分类页面"""
        files = []

        for key, info in CATEGORIES.items():
            repos = db.get_repos_by_category(key, limit=50)

            content = self._get_base_html(
                f"{info['name']}",
                f"""
        <header class="page-header container">
            <div class="category-icon-large">{info['icon']}</div>
            <h1 class="page-title">{info['name']}</h1>
            <p class="page-subtitle">{info['description']}</p>
        </header>

        <div class="container">
            <div class="repo-grid">
                {"".join(self._format_repo_card(repo) for repo in repos)}
            </div>
        </div>
        """
            )

            path = self.output_dir / "category" / f"{key}.html"
            path.write_text(content, encoding="utf-8")
            files.append(str(path))

        return files

    def generate_css(self) -> str:
        """生成 minimalist css"""
        css = """
/* Minimalist Design System */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #ffffff;
    --text-primary: #111111;
    --text-secondary: #666666;
    --text-tertiary: #999999;
    --accent: #111111;
    --border: #eaeaea;
    --card-bg: #ffffff;
    --card-hover: #fafafa;
    --nav-height: 64px;
    --radius: 8px;
}

@media (prefers-color-scheme: dark) {
    :root {
        --bg: #0a0a0a;
        --text-primary: #ededed;
        --text-secondary: #a1a1a1;
        --text-tertiary: #666666;
        --accent: #ededed;
        --border: #2a2a2a;
        --card-bg: #0a0a0a;
        --card-hover: #111111;
    }
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: var(--bg);
    color: var(--text-primary);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
}

/* Layout */
.container {
    max-width: 1024px;
    margin: 0 auto;
    padding: 0 24px;
}

/* Navigation */
.nav {
    height: var(--nav-height);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    background: var(--bg);
    z-index: 100;
    backdrop-filter: blur(10px);
    background-color: rgba(255, 255, 255, 0.8);
}

@media (prefers-color-scheme: dark) {
    .nav { background-color: rgba(10, 10, 10, 0.8); }
}

.nav-content {
    height: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-logo {
    font-weight: 700;
    font-size: 1.1rem;
    color: var(--text-primary);
    text-decoration: none;
    letter-spacing: -0.02em;
}

.nav-links {
    display: flex;
    gap: 24px;
}

.link {
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.95rem;
    font-weight: 500;
    transition: color 0.2s;
}

.link:hover, .link.active {
    color: var(--text-primary);
}

/* Hero Section */
.hero {
    padding: 100px 0 80px;
    text-align: center;
}

.hero-label {
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    color: var(--text-secondary);
    font-weight: 600;
    margin-bottom: 16px;
    display: block;
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 16px;
    letter-spacing: -0.03em;
    background: linear-gradient(to right, var(--text-primary), var(--text-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 1.25rem;
    color: var(--text-secondary);
    max-width: 600px;
    margin: 0 auto 32px;
}

.hero-meta {
    display: flex;
    justify-content: center;
    gap: 12px;
}

.date-badge, .topic-badge {
    padding: 6px 14px;
    background: var(--card-hover);
    border: 1px solid var(--border);
    border-radius: 99px;
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--text-secondary);
}

/* Page Headers */
.page-header {
    padding: 80px 0 40px;
    text-align: left;
}
.page-header.container { text-align: left; }
.page-title {
    font-size: 2.5rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
}
.page-subtitle {
    color: var(--text-secondary);
    font-size: 1.1rem;
}

/* Sections */
.section { margin-bottom: 80px; }
.section-header { margin-bottom: 32px; }
.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}
.section-desc { color: var(--text-secondary); }

/* Repo Cards */
.repo-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 24px;
}

.repo-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    display: flex;
    flex-direction: column;
    transition: all 0.2s ease;
    height: 100%;
    position: relative;
    top: 0;
}

.repo-card:hover {
    border-color: var(--text-primary);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px -10px rgba(0,0,0,0.05);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
}

.repo-name {
    font-size: 1.1rem;
    font-weight: 600;
}

.repo-name a {
    color: var(--text-primary);
    text-decoration: none;
}
.repo-name a:hover { text-decoration: underline; }

.repo-stats {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-secondary);
    background: var(--card-hover);
    padding: 4px 8px;
    border-radius: 4px;
}

.repo-desc {
    font-size: 0.95rem;
    color: var(--text-secondary);
    margin-bottom: 20px;
    flex-grow: 1;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.card-footer {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.tag {
    font-size: 0.75rem;
    padding: 4px 10px;
    border-radius: 99px;
    border: 1px solid var(--border);
    color: var(--text-secondary);
    font-weight: 500;
}

/* Category Grid */
.category-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
}

.category-card {
    padding: 24px;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    text-decoration: none;
    color: var(--text-primary);
    transition: all 0.2s;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.category-card:hover {
    background: var(--card-hover);
    border-color: var(--text-secondary);
}

.cat-icon { font-size: 2rem; margin-bottom: 12px; }
.cat-name { font-weight: 600; font-size: 1rem; }

/* Lists */
.trend-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 40px;
}

.column-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
}

.repo-list { display: flex; flex-direction: column; gap: 16px; }

.list-item {
    display: block;
    text-decoration: none;
    padding: 16px;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    transition: all 0.2s;
}

.list-item:hover {
    border-color: var(--text-primary);
    background: var(--card-hover);
}

.li-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
}

.li-name { color: var(--text-primary); font-weight: 600; }
.li-stars { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--text-secondary); }
.li-desc { font-size: 0.85rem; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Footer */
.footer {
    border-top: 1px solid var(--border);
    padding: 40px 0;
    margin-top: 80px;
    color: var(--text-tertiary);
    font-size: 0.9rem;
    text-align: center;
}

.footer a { color: var(--text-secondary); text-decoration: none; }
.footer a:hover { color: var(--text-primary); }

@media (max-width: 768px) {
    .hero-title { font-size: 2.5rem; }
}
"""
        path = self.output_dir / "assets" / "css" / "style.css"
        path.write_text(css, encoding="utf-8")
        return str(path)

    def _get_base_html(self, title: str, body_content: str) -> str:
        """生成基础 HTML 结构"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {self.meta['title']}</title>
    <meta name="description" content="{self.meta['description']}">
    <link rel="stylesheet" href="{self.url_prefix}/assets/css/style.css">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📈</text></svg>">
</head>
<body>
    <nav class="nav">
        <div class="container nav-content">
            <a href="{self.url_prefix}/" class="nav-logo">{self.meta['title']}</a>
            <div class="nav-links">
                <a href="{self.url_prefix}/" class="link">Home</a>
                <a href="{self.url_prefix}/trending/latest.html" class="link">Trends</a>
                <a href="{self.url_prefix}/category/plugin.html" class="link">Categories</a>
            </div>
        </div>
    </nav>

    <main>
        {body_content}
    </main>

    <footer class="footer container">
        <p>© {datetime.now().year} {self.meta['title']}. Curated by AI.</p>
        <p style="margin-top: 8px;">
            <a href="https://github.com/topics/{self.topic}">#{self.topic}</a> &bull; 
            <a href="https://github.com/geekjourneyx/github-topics-trending">GitHub</a>
        </p>
    </footer>
</body>
</html>"""

    def _format_repo_card(self, repo: Dict) -> str:
        """格式化通用仓库卡片"""
        repo_name = repo.get("repo_name", "")
        url = repo.get("url", f"https://github.com/{repo_name}")
        stars = repo.get("stars", 0)
        summary = repo.get("summary", "") or repo.get("description", "")
        category = repo.get("category_zh", "")

        return f"""
        <div class="repo-card">
            <div class="card-header">
                <div class="repo-name"><a href="{url}" target="_blank">{repo_name.replace('/', ' / ')}</a></div>
                <div class="repo-stats">★ {format_number(stars)}</div>
            </div>
            <p class="repo-desc">{summary}</p>
            <div class="card-footer">
                {f'<span class="tag">{category}</span>' if category else ''}
            </div>
        </div>
        """

    def _format_repo_list_item(self, repo: Dict) -> str:
        """格式化列表项 (小卡片)"""
        repo_name = repo.get("repo_name", "")
        url = repo.get("url", f"https://github.com/{repo_name}")
        stars_delta = repo.get("stars_delta", 0)
        summary = repo.get("summary", "") or repo.get("description", "")

        stars_display = f"+{format_number(stars_delta)}" if stars_delta > 0 else str(stars_delta)

        return f"""
        <a href="{url}" target="_blank" class="list-item">
            <div class="li-header">
                <span class="li-name">{repo_name.split('/')[-1]}</span>
                <span class="li-stars">{stars_display} ★</span>
            </div>
            <p class="li-desc">{summary}</p>
        </a>
        """

    def _format_category_card(self, category: Dict) -> str:
        """格式化分类卡片"""
        key = [k for k, v in CATEGORIES.items() if v == category][0]

        return f"""
        <a href="{self.url_prefix}/category/{key}.html" class="category-card">
            <div class="cat-icon">{category['icon']}</div>
            <div class="cat-name">{category['name']}</div>
        </a>
        """


def generate_website(trends: Dict, date: str, db, output_dir: str = None) -> List[str]:
    """便捷函数：生成网站"""
    generator = WebGenerator(output_dir)
    return generator.generate_all(trends, date, db)
