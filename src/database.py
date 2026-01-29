"""
SQLite 数据库操作模块
管理 GitHub 仓库趋势数据的存储和查询
"""
import os
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from src.config import DB_PATH, DB_RETENTION_DAYS


class Database:
    """SQLite 数据库操作类"""

    def __init__(self, db_path: str = None):
        """
        初始化数据库连接

        Args:
            db_path: 数据库文件路径，默认使用配置中的路径
        """
        self.db_path = db_path or DB_PATH
        self._ensure_db_dir()
        self.conn = None

    def _ensure_db_dir(self):
        """确保数据库目录存在"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def connect(self):
        """建立数据库连接"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # 返回字典格式

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def init_db(self) -> None:
        """初始化数据库表"""
        self.connect()
        cursor = self.conn.cursor()

        # 1. repos_daily - 每日快照表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repos_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                rank INTEGER NOT NULL,
                repo_name TEXT NOT NULL,
                owner TEXT NOT NULL,
                stars INTEGER NOT NULL,
                stars_delta INTEGER DEFAULT 0,
                forks INTEGER,
                issues INTEGER,
                language TEXT,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, repo_name)
            )
        """)

        # 2. repos_details - 仓库详情缓存表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repos_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_name TEXT UNIQUE NOT NULL,
                summary TEXT NOT NULL,
                description TEXT,
                use_case TEXT,
                solves TEXT,
                category TEXT NOT NULL,
                category_zh TEXT NOT NULL,
                topics TEXT,
                language TEXT,
                readme_summary TEXT,
                owner TEXT NOT NULL,
                url TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. repos_history - 历史趋势表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repos_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_name TEXT NOT NULL,
                date TEXT NOT NULL,
                rank INTEGER NOT NULL,
                stars INTEGER NOT NULL,
                forks INTEGER,
                UNIQUE(repo_name, date)
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_date ON repos_daily(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_repo ON repos_daily(repo_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_rank ON repos_daily(date, rank)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_details_category ON repos_details(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_details_owner ON repos_details(owner)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_details_language ON repos_details(language)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_repo ON repos_history(repo_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_date ON repos_history(date)")

        self.conn.commit()
        print(f"✅ 数据库初始化完成: {self.db_path}")

    def save_today_data(self, date: str, repos: List[Dict]) -> None:
        """
        保存今日数据

        Args:
            date: 日期 YYYY-MM-DD
            repos: 仓库列表
        """
        self.connect()
        cursor = self.conn.cursor()

        for repo in repos:
            cursor.execute("""
                INSERT OR REPLACE INTO repos_daily
                (date, rank, repo_name, owner, stars, stars_delta, forks, issues, language, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date,
                repo.get("rank"),
                repo.get("repo_name"),
                repo.get("owner"),
                repo.get("stars"),
                repo.get("stars_delta", 0),
                repo.get("forks"),
                repo.get("issues"),
                repo.get("language"),
                repo.get("url", "")
            ))

            # 同时写入历史表
            cursor.execute("""
                INSERT OR REPLACE INTO repos_history
                (repo_name, date, rank, stars, forks)
                VALUES (?, ?, ?, ?, ?)
            """, (
                repo.get("repo_name"),
                date,
                repo.get("rank"),
                repo.get("stars"),
                repo.get("forks")
            ))

        self.conn.commit()
        print(f"✅ 保存今日数据: {len(repos)} 条记录")

    def get_repos_by_date(self, date: str) -> List[Dict]:
        """
        获取指定日期的数据

        Args:
            date: 日期 YYYY-MM-DD

        Returns:
            仓库列表
        """
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT rank, repo_name, owner, stars, stars_delta, forks, issues, language, url
            FROM repos_daily
            WHERE date = ?
            ORDER BY rank
        """, (date,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_yesterday_data(self, date: str) -> List[Dict]:
        """
        获取昨日数据

        Args:
            date: 当前日期 YYYY-MM-DD

        Returns:
            昨日的仓库列表
        """
        yesterday = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        return self.get_repos_by_date(yesterday)

    def save_repo_details(self, details: List[Dict]) -> None:
        """
        保存/更新仓库详情

        Args:
            details: AI 分析的仓库详情列表
        """
        self.connect()
        cursor = self.conn.cursor()

        for detail in details:
            solves_json = json.dumps(detail.get("solves", []), ensure_ascii=False)
            topics_json = json.dumps(detail.get("topics", []), ensure_ascii=False)

            cursor.execute("""
                INSERT OR REPLACE INTO repos_details
                (repo_name, summary, description, use_case, solves, category, category_zh,
                 topics, language, readme_summary, owner, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                detail.get("repo_name"),
                detail.get("summary"),
                detail.get("description"),
                detail.get("use_case"),
                solves_json,
                detail.get("category"),
                detail.get("category_zh"),
                topics_json,
                detail.get("language"),
                detail.get("readme_summary"),
                detail.get("owner"),
                detail.get("url")
            ))

        self.conn.commit()
        print(f"✅ 保存仓库详情: {len(details)} 条记录")

    def get_repo_details(self, repo_name: str) -> Optional[Dict]:
        """
        获取仓库详情

        Args:
            repo_name: 仓库全名 (owner/repo)

        Returns:
            仓库详情字典，如果不存在返回 None
        """
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT repo_name, summary, description, use_case, solves, category, category_zh,
                   topics, language, readme_summary, owner, url
            FROM repos_details
            WHERE repo_name = ?
        """, (repo_name,))

        row = cursor.fetchone()
        if row:
            result = dict(row)
            # 解析 JSON 字段
            if result.get("solves"):
                result["solves"] = json.loads(result["solves"])
            if result.get("topics"):
                result["topics"] = json.loads(result["topics"])
            return result
        return None

    def get_all_repo_details(self) -> Dict[str, Dict]:
        """
        获取所有仓库详情

        Returns:
            {repo_name: detail_dict} 的字典
        """
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT repo_name, summary, description, use_case, solves, category, category_zh,
                   topics, language, readme_summary, owner, url
            FROM repos_details
        """)

        result = {}
        for row in cursor.fetchall():
            detail = dict(row)
            if detail.get("solves"):
                detail["solves"] = json.loads(detail["solves"])
            if detail.get("topics"):
                detail["topics"] = json.loads(detail["topics"])
            result[detail["repo_name"]] = detail

        return result

    def cleanup_old_data(self, days: int = None) -> int:
        """
        清理过期数据

        Args:
            days: 保留天数，默认使用配置中的值

        Returns:
            删除的记录数
        """
        retention_days = days or DB_RETENTION_DAYS
        cutoff_date = (datetime.now() - timedelta(days=retention_days)).strftime("%Y-%m-%d")

        self.connect()
        cursor = self.conn.cursor()

        # 清理每日快照
        cursor.execute("""
            DELETE FROM repos_daily
            WHERE date < ?
        """, (cutoff_date,))

        deleted_daily = cursor.rowcount

        # 清理历史数据
        cursor.execute("""
            DELETE FROM repos_history
            WHERE date < ?
        """, (cutoff_date,))

        deleted_history = cursor.rowcount

        self.conn.commit()
        total_deleted = deleted_daily + deleted_history

        if total_deleted > 0:
            print(f"🗑️ 清理过期数据: {total_deleted} 条记录 (早于 {cutoff_date})")

        return total_deleted

    def get_repo_history(self, repo_name: str, days: int = 30) -> List[Dict]:
        """
        获取仓库历史趋势

        Args:
            repo_name: 仓库全名
            days: 查询天数

        Returns:
            历史数据列表，按日期升序排列
        """
        self.connect()
        cursor = self.conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT date, rank, stars, forks
            FROM repos_history
            WHERE repo_name = ? AND date >= ?
            ORDER BY date ASC
        """, (repo_name, cutoff_date))

        return [dict(row) for row in cursor.fetchall()]

    def get_available_dates(self, limit: int = 30) -> List[str]:
        """
        获取可用的日期列表

        Args:
            limit: 返回的最大日期数

        Returns:
            日期列表，按降序排列（最新的在前）
        """
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT DISTINCT date
            FROM repos_daily
            ORDER BY date DESC
            LIMIT ?
        """, (limit,))

        return [row["date"] for row in cursor.fetchall()]

    def get_category_stats(self, date: str) -> List[Dict]:
        """
        获取指定日期的分类统计

        Args:
            date: 日期 YYYY-MM-DD

        Returns:
            分类统计列表
        """
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT d.category, d.category_zh, COUNT(*) as count
            FROM repos_daily r
            LEFT JOIN repos_details d ON r.repo_name = d.repo_name
            WHERE r.date = ?
            GROUP BY d.category
            ORDER BY count DESC
        """, (date,))

        return [dict(row) for row in cursor.fetchall()]

    def get_repos_by_category(self, category: str, limit: int = 50) -> List[Dict]:
        """
        获取指定分类的仓库

        Args:
            category: 分类名称
            limit: 返回数量

        Returns:
            仓库列表
        """
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT r.repo_name, r.owner, r.stars, r.forks, r.language, r.url,
                   d.summary, d.description, d.category, d.category_zh
            FROM repos_details d
            JOIN repos_daily r ON d.repo_name = r.repo_name
            WHERE d.category = ?
            ORDER BY r.stars DESC
            LIMIT ?
        """, (category, limit))

        return [dict(row) for row in cursor.fetchall()]

    def get_top_movers(self, date: str, limit: int = 5) -> Dict[str, List[Dict]]:
        """
        获取排名变化最大的仓库

        Args:
            date: 日期 YYYY-MM-DD
            limit: 返回数量

        Returns:
            {"rising": [...], "falling": [...]}
        """
        self.connect()
        cursor = self.conn.cursor()

        # 上升最多
        cursor.execute("""
            SELECT r.repo_name, r.rank, r.stars_delta, d.summary, d.category
            FROM repos_daily r
            LEFT JOIN repos_details d ON r.repo_name = d.repo_name
            WHERE r.date = ? AND r.stars_delta > 0
            ORDER BY r.stars_delta DESC, r.rank ASC
            LIMIT ?
        """, (date, limit))

        rising = [dict(row) for row in cursor.fetchall()]

        # 下降最多
        cursor.execute("""
            SELECT r.repo_name, r.rank, r.stars_delta, d.summary, d.category
            FROM repos_daily r
            LEFT JOIN repos_details d ON r.repo_name = d.repo_name
            WHERE r.date = ? AND r.stars_delta < 0
            ORDER BY r.stars_delta ASC, r.rank ASC
            LIMIT ?
        """, (date, limit))

        falling = [dict(row) for row in cursor.fetchall()]

        return {"rising": rising, "falling": falling}

    def get_language_stats(self, date: str = None, limit: int = 20) -> List[Dict]:
        """
        获取语言统计

        Args:
            date: 日期 YYYY-MM-DD，None 表示使用最新数据
            limit: 返回数量

        Returns:
            语言统计列表
        """
        self.connect()
        cursor = self.conn.cursor()

        if date:
            cursor.execute("""
                SELECT language, COUNT(*) as count, AVG(stars) as avg_stars
                FROM repos_daily
                WHERE date = ? AND language IS NOT NULL AND language != ''
                GROUP BY language
                ORDER BY count DESC
                LIMIT ?
            """, (date, limit))
        else:
            cursor.execute("""
                SELECT language, COUNT(*) as count, AVG(stars) as avg_stars
                FROM repos_details
                WHERE language IS NOT NULL AND language != ''
                GROUP BY language
                ORDER BY count DESC
                LIMIT ?
            """, (limit,))

        return [dict(row) for row in cursor.fetchall()]


def get_database() -> Database:
    """获取数据库实例（便捷函数）"""
    return Database()
