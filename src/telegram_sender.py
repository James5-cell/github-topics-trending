"""
Telegram Sender - Telegram 消息发送
使用 Telegram Bot API 发送 Markdown 消息
"""
import requests
from typing import Dict, Optional


class TelegramSender:
    """Telegram 消息发送器"""

    def __init__(self, token: str, chat_id: str):
        """
        初始化

        Args:
            token: Bot Token
            chat_id: 目标 Chat ID
        """
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}/sendMessage"

    def send_message(self, text: str, parse_mode: str = "Markdown") -> Dict:
        """
        发送消息

        Args:
            text: 消息内容
            parse_mode: 解析模式 (Markdown/HTML)

        Returns:
            API 响应结果
        """
        if not self.token or not self.chat_id:
            print("⚠️ Telegram 配置缺失，跳过发送")
            return {"success": False, "message": "配置缺失"}

        try:
            print(f"📤 正在发送 Telegram 消息 (长度: {len(text)})...")
            
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }

            response = requests.post(self.api_url, json=data, timeout=10)
            result = response.json()

            if result.get("ok"):
                print("✅ Telegram 消息发送成功!")
                return {"success": True, "result": result}
            else:
                print(f"❌ Telegram 发送失败: {result.get('description')}")
                return {"success": False, "message": result.get("description")}

        except Exception as e:
            print(f"❌ Telegram 请求出错: {e}")
            return {"success": False, "message": str(e)}

    def send_report(self, trends: Dict, date: str) -> Dict:
        """
        发送趋势报告

        Args:
            trends: 趋势数据
            date: 日期

        Returns:
            发送结果
        """
        message = self._format_report(trends, date)
        
        # Telegram 消息长度限制 4096，如果过长可能需要切分，这里先简化处理
        # 实际情况中，Top 20 + 简介通常不会超过限制，除非简介非常长
        return self.send_message(message)

    def _format_report(self, trends: Dict, date: str) -> str:
        """格式化 Markdown 报告"""
        lines = []
        lines.append(f"🔥 *GitHub Topics Trending* `#{trends.get('topic', 'unknown')}`")
        lines.append(f"📅 *{date}*")
        lines.append("")

        # 1. Rising Top 5 (星标增长)
        rising = trends.get("rising_top5", [])
        if rising:
            lines.append("🚀 *今日飙升*")
            for repo in rising:
                lines.append(self._format_repo_line(repo))
            lines.append("")

        # 2. New Entries (新晋)
        new_entries = trends.get("new_entries", [])[:5]  # 只取前5个避免太长
        if new_entries:
            lines.append("✨ *新晋项目*")
            for repo in new_entries:
                lines.append(self._format_repo_line(repo))
            lines.append("")

        # 3. Top Picks (精选 Top 10)
        # 这里使用传入的 top_20，但只展示前 10 以免刷屏
        top_list = trends.get("top_20", [])[:10]
        if top_list:
            lines.append("🏆 *热门精选*")
            for i, repo in enumerate(top_list, 1):
                lines.append(self._format_repo_item(i, repo))
        
        lines.append("")
        lines.append(f"[查看完整报告及更多分类](https://james5-cell.github.io/github-topics-trending/)")

        return "\n".join(lines)

    def _format_repo_line(self, repo: Dict) -> str:
        """格式化单行简单展示"""
        name = repo.get("repo_name")
        url = repo.get("url")
        stars = repo.get("stars", 0)
        delta = repo.get("stars_delta", 0)
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        
        return f"• [{name}]({url}) ⭐{stars} ({delta_str})"

    def _format_repo_item(self, index: int, repo: Dict) -> str:
        """格式化详细展示"""
        name = repo.get("repo_name")
        url = repo.get("url")
        # stars = repo.get("stars", 0)
        summary = repo.get("summary", "") or repo.get("description", "")
        category = repo.get("category_zh", "")
        
        # 限制摘要长度
        if len(summary) > 60:
            summary = summary[:57] + "..."

        icon = "🔹"
        if index <= 3:
            icon = ["🥇", "🥈", "🥉"][index-1]
        
        line = f"{icon} *[{name}]({url})*"
        if category:
            line += f" `[{category}]`"
        line += f"\n  _{summary}_"
        return line
