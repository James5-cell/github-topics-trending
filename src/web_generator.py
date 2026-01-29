"""
Web Generator - GitHub Pages 静态网站生成器
生成 GitHub Topics Trending 的静态网站页面
"""
import os
import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path

from src.config import OUTPUT_DIR, TOPIC, SITE_META, get_theme, CATEGORIES, format_number


class WebGenerator:
    """GitHub Pages 静态网站生成器"""

    def __init__(self, output_dir: str = None, theme: str = "blue"):
        """
        初始化

        Args:
            output_dir: 输出目录
            theme: 主题名称
        """
        self.output_dir = Path(output_dir or OUTPUT_DIR)
        self.theme = get_theme(theme)
        self.topic = TOPIC
        self.meta = SITE_META

        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 创建子目录
        (self.output_dir / "trending").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "category").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "repo").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "assets" / "css").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "assets" / "js").mkdir(parents=True, exist_ok=True)

    def generate_all(self, trends: Dict, date: str, db) -> List[str]:
        """
        生成所有页面

        Args:
            trends: 趋势数据
            date: 日期
            db: 数据库实例

        Returns:
            生成的文件路径列表
        """
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
        """
        生成首页

        Args:
            trends: 趋势数据
            date: 日期

        Returns:
            生成的文件路径
        """
        top_20 = trends.get("top_20", [])[:20]

        content = self._get_base_html(f"{self.meta['title']} - 首页", """
        <div class="hero">
            <h1>{title}</h1>
            <p class="subtitle">{subtitle}</p>
            <p class="date">{date}</p>
        </div>

        <div class="container">
            <section class="section">
                <h2 class="section-title">Top 20 经典榜单</h2>
                <div class="repo-grid">
                    {repo_cards}
                </div>
            </section>

            <section class="section">
                <h2 class="section-title">按分类浏览</h2>
                <div class="category-grid">
                    {category_cards}
                </div>
            </section>
        </div>
        """.format(
            title=self.meta['title'],
            subtitle=self.meta['subtitle'],
            date=date,
            repo_cards="".join(self._format_repo_card_small(repo) for repo in top_20),
            category_cards="".join(self._format_category_card(cat) for cat in CATEGORIES.values())
        ))

        path = self.output_dir / "index.html"
        path.write_text(content, encoding="utf-8")
        return str(path)

    def generate_trending_page(self, trends: Dict, date: str) -> str:
        """
        生成趋势页

        Args:
            trends: 趋势数据
            date: 日期

        Returns:
            生成的文件路径
        """
        content = self._get_base_html(f"趋势 - {date}", f"""
        <div class="container">
            <h1 class="page-title">趋势报告 - {date}</h1>

            <section class="section">
                <h2 class="section-title">星标增长 Top 5</h2>
                <div class="repo-list">
                    {"".join(self._format_repo_card_medium(repo) for repo in trends.get("rising_top5", []))}
                </div>
            </section>

            <section class="section">
                <h2 class="section-title">新晋项目</h2>
                <div class="repo-list">
                    {"".join(self._format_repo_card_medium(repo) for repo in trends.get("new_entries", [])[:10])}
                </div>
            </section>

            <section class="section">
                <h2 class="section-title">活跃项目</h2>
                <div class="repo-list">
                    {"".join(self._format_repo_card_medium(repo) for repo in trends.get("active", []))}
                </div>
            </section>
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
        """
        生成分类页面

        Args:
            db: 数据库实例

        Returns:
            生成的文件路径列表
        """
        files = []

        for key, info in CATEGORIES.items():
            repos = db.get_repos_by_category(key, limit=50)

            content = self._get_base_html(
                f"{info['name']} - 分类",
                f"""
        <div class="container">
            <h1 class="page-title">{info['icon']} {info['name']}</h1>
            <p class="page-description">{info['description']}</p>

            <div class="repo-list">
                {"".join(self._format_repo_card_medium(repo) for repo in repos)}
            </div>
        </div>
        """
            )

            path = self.output_dir / "category" / f"{key}.html"
            path.write_text(content, encoding="utf-8")
            files.append(str(path))

        return files

    def generate_css(self) -> str:
        """
        生成 CSS 文件

        Returns:
            生成的文件路径
        """
        t = self.theme
        css = f"""
/* GitHub Topics Trending - 主题样式 */
:root {{
    --primary: {t['primary']};
    --secondary: {t['secondary']};
    --bg: {t['bg']};
    --card: {t['card']};
    --text: {t['text']};
    --text-secondary: {t['text_secondary']};
    --border: {t['border']};
    --success: {t['success']};
    --warning: {t['warning']};
    --danger: {t['danger']};
}}

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background-color: var(--bg);
    color: var(--text);
    line-height: 1.6;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}}

.hero {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    color: white;
    padding: 60px 20px;
    text-align: center;
}}

.hero h1 {{
    font-size: 2.5rem;
    margin-bottom: 10px;
}}

.hero .subtitle {{
    font-size: 1.2rem;
    opacity: 0.9;
}}

.hero .date {{
    margin-top: 20px;
    opacity: 0.8;
}}

.page-title {{
    font-size: 2rem;
    margin-bottom: 10px;
    padding: 20px 0;
}}

.page-description {{
    color: var(--text-secondary);
    margin-bottom: 30px;
}}

.section {{
    margin: 40px 0;
}}

.section-title {{
    font-size: 1.5rem;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--primary);
}}

.repo-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
}}

.repo-list {{
    display: flex;
    flex-direction: column;
    gap: 15px;
}}

.repo-card {{
    background-color: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    transition: transform 0.2s, box-shadow 0.2s;
}}

.repo-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}}

.repo-card h3 {{
    font-size: 1.2rem;
    margin-bottom: 8px;
}}

.repo-card h3 a {{
    color: var(--primary);
    text-decoration: none;
}}

.repo-card h3 a:hover {{
    text-decoration: underline;
}}

.repo-card .stats {{
    display: flex;
    gap: 15px;
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin: 10px 0;
}}

.repo-card .summary {{
    color: var(--text-secondary);
    font-size: 0.95rem;
    margin-top: 10px;
}}

.repo-card .badges {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
}}

.badge {{
    display: inline-block;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 500;
}}

.badge-category {{
    background-color: var(--primary);
    color: white;
}}

.badge-language {{
    background-color: var(--border);
    color: var(--text);
}}

.category-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
}}

.category-card {{
    background-color: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    transition: transform 0.2s;
}}

.category-card:hover {{
    transform: scale(1.05);
}}

.category-card a {{
    color: var(--text);
    text-decoration: none;
}}

.category-icon {{
    font-size: 2rem;
    margin-bottom: 10px;
}}

.category-name {{
    font-size: 1.1rem;
    font-weight: 600;
}}

.category-desc {{
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-top: 5px;
}}

.footer {{
    text-align: center;
    padding: 30px;
    color: var(--text-secondary);
    border-top: 1px solid var(--border);
    margin-top: 40px;
}}

.footer a {{
    color: var(--primary);
    text-decoration: none;
}}

/* 导航栏样式 */
.nav {{
    background-color: var(--card);
    border-bottom: 1px solid var(--border);
    padding: 15px 0;
    position: sticky;
    top: 0;
    z-index: 100;
}}

.nav-content {{
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.nav-logo {{
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--primary);
    text-decoration: none;
}}

.nav-links {{
    display: flex;
    gap: 20px;
}}

.nav-links a {{
    color: var(--text);
    text-decoration: none;
    font-size: 0.95rem;
    transition: color 0.2s;
}}

.nav-links a:hover {{
    color: var(--primary);
}}

@media (max-width: 768px) {{
    .nav-content {{
        flex-direction: column;
        gap: 10px;
    }}

    .repo-grid {{
        grid-template-columns: 1fr;
    }}

    .hero h1 {{
        font-size: 1.8rem;
    }}
}}
"""

        path = self.output_dir / "assets" / "css" / "style.css"
        path.write_text(css, encoding="utf-8")
        return str(path)

    def _get_base_html(self, title: str, body_content: str) -> str:
        """生成基础 HTML 结构"""
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {self.meta['title']}</title>
    <meta name="description" content="{self.meta['description']}">
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <nav class="nav">
        <div class="container nav-content">
            <a href="/" class="nav-logo">{self.meta['title']}</a>
            <div class="nav-links">
                <a href="/">首页</a>
                <a href="/trending/latest.html">趋势</a>
                <a href="/category/plugin.html">分类</a>
            </div>
        </div>
    </nav>

    {body_content}

    <footer class="footer">
        <p>{self.meta['title']} - {self.meta['description']}</p>
        <p style="margin-top: 10px;">
            <a href="https://github.com/topics/{self.topic}">GitHub Topic: {self.topic}</a>
        </p>
    </footer>
</body>
</html>"""

    def _format_repo_card_small(self, repo: Dict) -> str:
        """格式化小型仓库卡片"""
        repo_name = repo.get("repo_name", "")
        stars = repo.get("stars", 0)
        summary = repo.get("summary", "") or repo.get("description", "")

        return f"""
        <div class="repo-card">
            <h3><a href="/repo/{repo_name.replace('/', '-')}.html">{repo_name}</a></h3>
            <div class="stats">
                <span>⭐ {format_number(stars)}</span>
            </div>
            <p class="summary">{summary[:80]}...</p>
        </div>
        """

    def _format_repo_card_medium(self, repo: Dict) -> str:
        """格式化中型仓库卡片"""
        repo_name = repo.get("repo_name", "")
        url = repo.get("url", f"https://github.com/{repo_name}")
        stars = repo.get("stars", 0)
        forks = repo.get("forks", 0)
        language = repo.get("language", "")
        category_zh = repo.get("category_zh", "")
        summary = repo.get("summary", "") or repo.get("description", "")

        badges = ""
        if category_zh:
            badges += f'<span class="badge badge-category">{category_zh}</span>'
        if language:
            badges += f'<span class="badge badge-language">{language}</span>'

        return f"""
        <div class="repo-card">
            <h3><a href="{url}">{repo_name}</a></h3>
            <div class="stats">
                <span>⭐ {format_number(stars)}</span>
                <span>🔱 {format_number(forks)}</span>
            </div>
            <p class="summary">{summary[:150]}</p>
            <div class="badges">{badges}</div>
        </div>
        """

    def _format_category_card(self, category: Dict) -> str:
        """格式化分类卡片"""
        key = [k for k, v in CATEGORIES.items() if v == category][0]

        return f"""
        <div class="category-card">
            <a href="/category/{key}.html">
                <div class="category-icon">{category['icon']}</div>
                <div class="category-name">{category['name']}</div>
                <div class="category-desc">{category['description']}</div>
            </a>
        </div>
        """


def generate_website(trends: Dict, date: str, db, output_dir: str = None) -> List[str]:
    """便捷函数：生成网站"""
    generator = WebGenerator(output_dir)
    return generator.generate_all(trends, date, db)
