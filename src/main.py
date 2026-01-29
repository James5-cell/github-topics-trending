#!/usr/bin/env python3
"""
GitHub Topics Trending 主入口
自动获取 GitHub 话题下的热门仓库，AI 分析，生成趋势报告并发送邮件
"""
import sys
import os
from datetime import datetime, timezone

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.config import (
    NVIDIA_API_KEY,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    DEDUPLICATE_DAYS,
    DB_PATH,
    DB_RETENTION_DAYS,
    TOP_N_DETAILS,
    GITHUB_TOKEN,
    TOPIC,
    OUTPUT_DIR
)
from src.github_fetcher import GitHubFetcher
from src.readme_fetcher import ReadmeFetcher
from src.ai_summarizer import AISummarizer
from src.database import Database
from src.trend_analyzer import TrendAnalyzer
from src.email_reporter import EmailReporter
from src.telegram_sender import TelegramSender  # Changed from ResendSender
from src.web_generator import WebGenerator


def print_banner():
    """打印程序横幅"""
    banner = """
╔════════════════════════════════════════════════════════════╗
║                                                              ║
║   GitHub Topics Trending - 话题趋势追踪系统                   ║
║                                                              ║
║   GitHub API 数据采集 · AI (Nvidia NIM) 智能分析             ║
║   趋势计算 · Telegram 通知 · 静态网站生成                    ║
║                                                              ║
╚════════════════════════════════════════════════════════════╝
"""
    print(banner)


def get_today_date() -> str:
    """获取今日日期 YYYY-MM-DD"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def check_environment() -> bool:
    """
    检查环境变量配置

    Returns:
        是否配置完整
    """
    errors = []

    if not GITHUB_TOKEN:
        errors.append("GITHUB_TOKEN 环境变量未设置 (请提供 GitHub Personal Access Token)")

    if not NVIDIA_API_KEY:
        errors.append("NVIDIA_API_KEY 环境变量未设置 (请提供 Nvidia API Key)")
        
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN 环境变量未设置")
        
    if not TELEGRAM_CHAT_ID:
        errors.append("TELEGRAM_CHAT_ID 环境变量未设置")

    if errors:
        print("❌ 环境变量配置错误:")
        for error in errors:
            print(f"   - {error}")
        return False

    return True


def main():
    """主函数"""
    print_banner()

    # 检查环境变量
    if not check_environment():
        sys.exit(1)

    # 获取今日日期
    today = get_today_date()
    print(f"[目标日期] {today}")
    print(f"[话题标签] #{TOPIC}")
    print(f"   (北京时间: {datetime.now(timezone.utc)} + 8h)")
    
    if DEDUPLICATE_DAYS > 0:
        print(f"   (去重模式: 过滤 {DEDUPLICATE_DAYS} 天内已推送的项目)")
    
    print()

    # 初始化数据库
    db = Database(DB_PATH)
    db.init_db()

    try:
        # 1. 获取今日仓库榜单
        print(f"[步骤 1/9] 获取仓库排行榜...")
        fetcher = GitHubFetcher()
        today_repos = fetcher.fetch(sort_by="stars", limit=100)
        print(f"   成功获取 {len(today_repos)} 个仓库")
        print()

        # 2. 获取 Top N 详情（README）
        print(f"[步骤 2/9] 获取 Top {TOP_N_DETAILS} README...")
        readme_fetcher = ReadmeFetcher()
        top_repos = today_repos[:TOP_N_DETAILS]
        readme_summaries = readme_fetcher.batch_fetch_readmes(top_repos, delay=0.5)

        # 将 README 摘要合并到仓库数据
        for repo in top_repos:
            repo_name = repo.get("repo_name")
            if repo_name in readme_summaries:
                repo["readme_summary"] = readme_summaries[repo_name]

        print(f"   成功获取 {len(readme_summaries)} 个 README 摘要")
        print()

        # 3. AI 总结和分类
        print(f"[步骤 3/9] AI 分析和分类...")
        summarizer = AISummarizer()
        ai_summaries = summarizer.summarize_and_classify(top_repos)

        # 构建 AI 摘要映射
        ai_summary_map = {s["repo_name"]: s for s in ai_summaries}
        print(f"   成功分析 {len(ai_summaries)} 个仓库")
        print()

        # 4. 保存到数据库
        print(f"[步骤 4/9] 保存到数据库...")
        db.save_repo_details(ai_summaries)
        print()

        # 5. 计算趋势 (含去重逻辑)
        print(f"[步骤 5/9] 计算趋势 (去重天数: {DEDUPLICATE_DAYS})...")
        analyzer = TrendAnalyzer(db)
        trends = analyzer.calculate_trends(today_repos, today, ai_summary_map, deduplicate_days=DEDUPLICATE_DAYS)

        # 输出趋势摘要
        top_20_count = len(trends.get('top_20', []))
        print(f"   Top 20 (新发现): {top_20_count} 个")
        print(f"   上升: {len(trends['rising_top5'])} 个")
        print(f"   新晋: {len(trends['new_entries'])} 个")
        print(f"   跌出: {len(trends['dropped_entries'])} 个")
        print(f"   暴涨: {len(trends['surging'])} 个")
        print(f"   活跃: {len(trends['active'])} 个")
        print()

        # 6. 生成 HTML 报告 (仅用于网站生成，不再发送邮件)
        print(f"[步骤 6/9] 生成 HTML 报告...")
        email_reporter = EmailReporter()
        # 注意: 这里传入的 trends 已经是去重后的 top_20，但网站生成可能希望展示全部 Top 20?
        # 暂时保持一致，网站展示的内容与推送一致
        html_content = email_reporter.generate_email_html(trends, today)
        print(f"   HTML 生成完成")
        print()

        # 7. 发送 Telegram 通知
        print(f"[步骤 7/9] 发送 Telegram 通知...")
        sender = TelegramSender(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        result = sender.send_report(trends, today)

        if result["success"]:
            print(f"   ✅ Telegram 发送成功!")
            
            # 记录已推送的仓库，用于后续去重
            notified_repos = [r["repo_name"] for r in trends.get("top_20", [])]
            if notified_repos:
                db.record_notification(notified_repos)
        else:
            print(f"   ❌ Telegram 发送失败: {result.get('message')}")
        print()

        # 8. 生成 GitHub Pages 网站
        print(f"[步骤 8/9] 生成 GitHub Pages 网站...")
        web_gen = WebGenerator(OUTPUT_DIR)
        web_files = web_gen.generate_all(trends, today, db)
        print(f"   生成 {len(web_files)} 个文件")
        print()

        # 9. 清理过期数据
        print(f"[步骤 9/9] 清理 {DB_RETENTION_DAYS} 天前的数据...")
        deleted = db.cleanup_old_data(DB_RETENTION_DAYS)
        print()

        # 完成
        print("╔════════════════════════════════════════════════════════════╗")
        print("║                                                              ║")
        print("║   ✅ 任务完成!                                              ║")
        print("║                                                              ║")
        print(f"║   日期: {today}                                            ║")
        print(f"║   话题: #{TOPIC}                                            ║")
        print(f"║   推送: {top_20_count} 个新项目                                 ║")
        print("║                                                              ║")
        print("╚════════════════════════════════════════════════════════════╝")


    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        sys.exit(130)

    except Exception as e:
        print(f"\n[错误] 执行过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


def main_fetch_only():
    """仅获取数据，不发送邮件"""
    print_banner()

    today = get_today_date()
    print(f"[目标日期] {today}")
    print(f"[话题标签] #{TOPIC}")
    print()

    db = Database(DB_PATH)
    db.init_db()

    try:
        # 获取仓库
        print(f"[步骤 1/3] 获取仓库列表...")
        fetcher = GitHubFetcher()
        repos = fetcher.fetch(sort_by="stars", limit=100)
        print(f"   成功获取 {len(repos)} 个仓库")
        print()

        # 获取 README
        print(f"[步骤 2/3] 获取 README...")
        readme_fetcher = ReadmeFetcher()
        readme_summaries = readme_fetcher.batch_fetch_readmes(repos[:50], delay=0.5)
        print(f"   成功获取 {len(readme_summaries)} 个 README")
        print()

        # 保存数据
        print(f"[步骤 3/3] 保存数据...")
        for repo in repos[:50]:
            repo_name = repo.get("repo_name")
            if repo_name in readme_summaries:
                repo["readme_summary"] = readme_summaries[repo_name]

        ai_summaries = AISummarizer().summarize_and_classify(repos[:50])
        db.save_repo_details(ai_summaries)
        db.save_today_data(today, repos)
        print()

        print(f"✅ 完成! 获取 {len(repos)} 个仓库，分析 {len(ai_summaries)} 个")

    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    # 支持命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--fetch-only":
        main_fetch_only()
    else:
        main()
