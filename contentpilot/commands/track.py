"""内容追踪模块 - 第一性原理推导的核心功能

本质洞见: 没有反馈的创作是盲目的
- 追踪每篇内容的发布和表现
- 记录数据反馈，指导后续优化
- 找到最佳发布时间和内容类型
"""

import os
import json
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table

console = Console()

TRACKER_FILE = os.path.expanduser("~/.contentpilot/tracker.json")


def _load():
    """加载追踪数据"""
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"posts": [], "stats": {}}


def _save(data):
    """保存追踪数据"""
    os.makedirs(os.path.dirname(TRACKER_FILE), exist_ok=True)
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@click.group()
def track():
    """内容追踪 - 记录发布和数据，用数据指导优化。

    \b
    示例:
        contentpilot track add "Python教程" -p xiaohongshu -d 2026-03-13
        contentpilot track update 1 --views 5000 --likes 200 --comments 30
        contentpilot track report
        contentpilot track best-time -p xiaohongshu
    """
    pass


@track.command("add")
@click.argument("title")
@click.option("-p", "--platform", required=True, help="发布平台")
@click.option("-d", "--date", default=None, help="发布日期 (YYYY-MM-DD，默认今天)")
@click.option("-t", "--time", "pub_time", default=None, help="发布时间 (HH:MM)")
@click.option("--topic", default=None, help="选题类型 (hot/pain/evergreen/series)")
@click.option("--tags", default=None, help="话题标签，逗号分隔")
def add_post(title, platform, date, pub_time, topic, tags):
    """添加发布记录。"""
    data = _load()

    now = datetime.now()
    date = date or now.strftime("%Y-%m-%d")
    pub_time = pub_time or now.strftime("%H:%M")

    post = {
        "id": len(data["posts"]) + 1,
        "title": title,
        "platform": platform,
        "date": date,
        "time": pub_time,
        "topic_type": topic,
        "tags": tags.split(",") if tags else [],
        "metrics": {
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "saves": 0,
        },
        "created": now.isoformat(),
    }

    data["posts"].append(post)
    _save(data)

    console.print(f"[green]✓[/green] 已记录发布")
    console.print(f"  📝 {title}")
    console.print(f"  📱 {platform} | 📅 {date} {pub_time}")


@track.command("update")
@click.argument("post_id", type=int)
@click.option("--views", type=int, help="浏览量")
@click.option("--likes", type=int, help="点赞数")
@click.option("--comments", type=int, help="评论数")
@click.option("--shares", type=int, help="分享数")
@click.option("--saves", type=int, help="收藏数")
def update_metrics(post_id, views, likes, comments, shares, saves):
    """更新内容数据。"""
    data = _load()

    for post in data["posts"]:
        if post["id"] == post_id:
            if views is not None:
                post["metrics"]["views"] = views
            if likes is not None:
                post["metrics"]["likes"] = likes
            if comments is not None:
                post["metrics"]["comments"] = comments
            if shares is not None:
                post["metrics"]["shares"] = shares
            if saves is not None:
                post["metrics"]["saves"] = saves

            _save(data)
            console.print(f"[green]✓[/green] 已更新: {post['title']}")
            _show_metrics(post["metrics"])
            return

    console.print(f"[red]✗[/red] 未找到 ID {post_id}")


def _show_metrics(m):
    """显示数据"""
    engagement = (m["likes"] + m["comments"] + m["shares"] + m["saves"]) / max(m["views"], 1) * 100
    console.print(f"  👀 {m['views']:,} | ❤️ {m['likes']:,} | 💬 {m['comments']:,} | 🔄 {m['shares']:,} | 💾 {m['saves']:,}")
    console.print(f"  📊 互动率: {engagement:.1f}%")


@track.command("report")
@click.option("-p", "--platform", default=None, help="筛选平台")
@click.option("-n", "--last", default=10, help="最近N篇")
def report(platform, last):
    """内容表现报告。"""
    data = _load()
    posts = data["posts"]

    if platform:
        posts = [p for p in posts if p["platform"] == platform]

    posts = posts[-last:]

    if not posts:
        console.print("[yellow]暂无数据[/yellow]")
        return

    table = Table(title=f"📊 内容表现报告 (最近{len(posts)}篇)")
    table.add_column("ID", width=4)
    table.add_column("标题", width=20)
    table.add_column("平台", width=8)
    table.add_column("日期", width=10)
    table.add_column("👀浏览", width=8, justify="right")
    table.add_column("❤️点赞", width=6, justify="right")
    table.add_column("💬评论", width=6, justify="right")
    table.add_column("📊互动率", width=8, justify="right")

    total_views = 0
    total_engagement = 0

    for p in posts:
        m = p["metrics"]
        engagement = (m["likes"] + m["comments"] + m["shares"] + m["saves"]) / max(m["views"], 1) * 100
        total_views += m["views"]
        total_engagement += engagement

        table.add_row(
            str(p["id"]),
            p["title"][:20],
            p["platform"],
            p["date"],
            f"{m['views']:,}",
            str(m["likes"]),
            str(m["comments"]),
            f"{engagement:.1f}%",
        )

    console.print(table)

    if posts:
        avg_views = total_views / len(posts)
        avg_engagement = total_engagement / len(posts)
        console.print(f"\n📈 平均浏览: {avg_views:,.0f} | 平均互动率: {avg_engagement:.1f}%")

        # 找出表现最好的
        best = max(posts, key=lambda p: p["metrics"]["views"])
        console.print(f"🏆 最佳: [{best['id']}] {best['title'][:30]} ({best['platform']})")


@track.command("best-time")
@click.option("-p", "--platform", default=None, help="筛选平台")
def best_time(platform):
    """分析最佳发布时间。"""
    data = _load()
    posts = data["posts"]

    if platform:
        posts = [p for p in posts if p["platform"] == platform]

    if not posts:
        console.print("[yellow]暂无数据，需要更多发布记录[/yellow]")
        return

    # 按小时统计
    hour_stats = {}
    for p in posts:
        hour = int(p["time"].split(":")[0])
        if hour not in hour_stats:
            hour_stats[hour] = {"count": 0, "total_views": 0}
        hour_stats[hour]["count"] += 1
        hour_stats[hour]["total_views"] += p["metrics"]["views"]

    table = Table(title=f"⏰ 最佳发布时间 ({platform or '全部平台'})")
    table.add_column("时段", width=8)
    table.add_column("发布数", width=8, justify="right")
    table.add_column("总浏览", width=10, justify="right")
    table.add_column("平均浏览", width=10, justify="right")
    table.add_column("热度", width=15)

    for hour in sorted(hour_stats.keys()):
        stats = hour_stats[hour]
        avg = stats["total_views"] / stats["count"]
        bar = "█" * int(avg / max(s["total_views"]/s["count"] for s in hour_stats.values()) * 15)
        table.add_row(
            f"{hour:02d}:00",
            str(stats["count"]),
            f"{stats['total_views']:,}",
            f"{avg:,.0f}",
            bar,
        )

    console.print(table)
