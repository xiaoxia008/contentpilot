"""每日内容简报 - 创作者的晨间仪表盘

从第一性原理: 创作者每天醒来需要知道"今天做什么"
- 哪些选题值得写
- 哪些内容需要跟进
- 数据表现怎么样
- 有什么优化建议
"""

import os
from datetime import datetime, timedelta

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns

from contentpilot.utils.ai import call_ai
from contentpilot.utils.config import get_api_config
from contentpilot.commands.track import _load as load_tracker

console = Console()


@click.command("brief")
@click.option("--refresh-topics", is_flag=True, help="刷新选题建议 (需要API)")
def brief(refresh_topics):
    """每日内容简报 - 一键看今天该做什么。

    显示:
    • 📅 今日概览 (日期、待办)
    • 📊 昨日数据 (如有追踪记录)
    • 💡 选题建议 (缓存或刷新)
    • 📝 待完善内容 (缺标题/未检测的草稿)
    • 🎯 优化建议 (基于历史数据)

    \b
    示例:
        contentpilot brief
        contentpilot brief --refresh-topics
    """
    today = datetime.now()
    console.print(f"\n[cyan]📅 {today.strftime('%Y年%m月%d日 %A')}[/cyan] 内容简报\n")

    # 1. 数据概览
    _show_data_overview()

    # 2. 待完善内容
    _show_pending_content()

    # 3. 选题建议
    _show_topic_suggestions(refresh_topics)

    # 4. 优化建议
    _show_quick_tips()

    console.print("[dim]💡 使用 contentpilot topic hot '领域' 获取新选题[/dim]")
    console.print("[dim]💡 使用 contentpilot track insights 查看详细分析[/dim]\n")


def _show_data_overview():
    """显示数据概览"""
    data = load_tracker()
    posts = data.get("posts", [])

    if not posts:
        console.print(Panel(
            "[yellow]还没有追踪数据[/yellow]\n\n"
            "发布内容后使用以下命令追踪:\n"
            "  contentpilot track add '标题' -p 平台\n"
            "  contentpilot track update ID --views 1000",
            title="📊 数据追踪",
            border_style="yellow"
        ))
        return

    # 最近7天的数据
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    recent = [p for p in posts if p.get("date", "") >= week_ago]

    total_views = sum(p["metrics"]["views"] for p in recent)
    total_posts = len(recent)

    # 找出最佳内容
    best = max(posts, key=lambda p: p["metrics"]["views"])

    # 互动率
    if recent:
        avg_eng = sum(
            (m["likes"] + m["comments"] + m["shares"] + m["saves"]) / max(m["views"], 1) * 100
            for p in recent
            for m in [p["metrics"]]
        ) / len(recent)
    else:
        avg_eng = 0

    table = Table(title=f"📊 近7天表现 ({total_posts}篇)")
    table.add_column("指标", style="cyan")
    table.add_column("数值", justify="right")

    table.add_row("总浏览", f"{total_views:,}")
    table.add_row("平均互动率", f"{avg_eng:.1f}%")
    table.add_row("总内容数", str(len(posts)))

    console.print(table)
    console.print(f"🏆 最佳: 「{best['title'][:25]}」({best['metrics']['views']:,} 浏览)\n")


def _show_pending_content():
    """显示待完善内容"""
    pending = []

    # 检查当前目录的草稿文件
    for f in os.listdir("."):
        if f.startswith("draft_") and f.endswith(".md"):
            # 检查是否有对应的标题文件
            title_file = f.replace("draft_", "title_").replace(".md", ".txt")
            has_title = os.path.exists(title_file)
            # 检查是否检测过违禁词
            check_file = f.replace("draft_", "check_").replace(".md", ".txt")
            has_check = os.path.exists(check_file)

            status = []
            if not has_title:
                status.append("缺标题")
            if not has_check:
                status.append("未检测")

            if status:
                pending.append({"file": f, "status": ", ".join(status)})

    if pending:
        table = Table(title="📝 待完善内容")
        table.add_column("文件", style="cyan")
        table.add_column("待办", style="yellow")

        for p in pending:
            table.add_row(p["file"], p["status"])

        console.print(table)
        console.print()
    else:
        console.print("[green]✅ 没有待完善的草稿[/green]\n")


def _show_topic_suggestions(refresh):
    """显示选题建议"""
    topic_files = [f for f in os.listdir(".") if f.startswith("topics_") and f.endswith(".txt")]

    if topic_files and not refresh:
        # 显示最近的选题文件
        latest = max(topic_files, key=lambda f: os.path.getmtime(f))
        console.print(Panel(
            f"[cyan]缓存选题:[/cyan] {latest}\n"
            f"[dim]修改时间: {datetime.fromtimestamp(os.path.getmtime(latest)).strftime('%m-%d %H:%M')}[/dim]\n\n"
            f"使用 [bold]contentpilot brief --refresh-topics[/bold] 刷新\n"
            f"使用 [bold]contentpilot topic hot '领域'[/bold] 获取新选题",
            title="💡 选题建议",
            border_style="cyan"
        ))
    elif refresh:
        api_key, base_url, model = get_api_config()
        if not api_key:
            console.print("[yellow]⚠️ 刷新选题需要 OPENAI_API_KEY[/yellow]")
            return

        console.print("[green]AI 正在获取今日选题建议...[/green]")
        prompt = """作为内容策略专家，提供今天值得关注的3个内容创作方向。
要求：
1. 结合当前热点趋势
2. 适合个人创作者（不需要团队资源）
3. 简要说明切入角度

输出格式:
方向N: [主题]
- 切入角度: [怎么写]
- 为什么今天适合写: [理由]
---"""

        result = call_ai(prompt, api_key, base_url, model)
        if result:
            console.print(Panel(result, title="💡 今日选题建议", border_style="cyan"))
            # 缓存
            with open("topics_brief_today.txt", "w", encoding="utf-8") as f:
                f.write(result)
    else:
        console.print(Panel(
            "[yellow]还没有选题文件[/yellow]\n\n"
            "快速开始:\n"
            "  contentpilot topic hot '你的领域'\n"
            "  contentpilot topic pain '你的领域'\n"
            "  contentpilot brief --refresh-topics",
            title="💡 选题建议",
            border_style="yellow"
        ))

    console.print()


def _show_quick_tips():
    """显示快速提示"""
    tips = [
        "🎯 发布前用 check 检测违禁词，避免限流",
        "📌 好标题决定80%的点击率，用 title 优化",
        "📊 发布后记得 track add 记录数据",
        "💡 用 inspire angles 从一个主题找多个角度",
    ]

    import random
    tip = random.choice(tips)
    console.print(f"[dim]{tip}[/dim]\n")
