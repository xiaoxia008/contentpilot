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


@track.command("insights")
@click.option("-p", "--platform", default=None, help="筛选平台")
@click.option("-n", "--last", default=20, help="分析最近N篇")
def insights(platform, last):
    """内容洞察 - 基于数据生成优化建议。

    分析你的内容表现数据，找出：
    • 最佳发布时间和内容类型
    • 表现最好的标签和话题
    • 具体的优化建议
    """
    data = _load()
    posts = data["posts"]

    if platform:
        posts = [p for p in posts if p["platform"] == platform]

    posts = posts[-last:]

    if not posts or len(posts) < 2:
        console.print("[yellow]📊 数据不足，至少需要 2 篇内容才能生成洞察[/yellow]")
        console.print("[dim]💡 使用 contentpilot track add 添加更多发布记录[/dim]")
        return

    console.print(f"\n[cyan]🔍 内容洞察分析[/cyan] (基于 {len(posts)} 篇内容)\n")

    # 1. 整体表现
    total_views = sum(p["metrics"]["views"] for p in posts)
    total_likes = sum(p["metrics"]["likes"] for p in posts)
    total_comments = sum(p["metrics"]["comments"] for p in posts)
    total_shares = sum(p["metrics"]["shares"] for p in posts)
    total_saves = sum(p["metrics"]["saves"] for p in posts)

    avg_views = total_views / len(posts)
    avg_engagement = sum(
        (m["likes"] + m["comments"] + m["shares"] + m["saves"]) / max(m["views"], 1) * 100
        for p in posts
        for m in [p["metrics"]]
    ) / len(posts)

    table = Table(title="📊 整体表现")
    table.add_column("指标", style="cyan")
    table.add_column("数值", justify="right")
    table.add_column("评估", style="green")

    table.add_row("总浏览", f"{total_views:,}", "")
    table.add_row("平均浏览", f"{avg_views:,.0f}", _rate_view(avg_views))
    table.add_row("平均互动率", f"{avg_engagement:.1f}%", _rate_engagement(avg_engagement))
    table.add_row("总互动", f"{total_likes + total_comments + total_shares + total_saves:,}", "")

    console.print(table)

    # 2. 最佳发布时间
    hour_stats = {}
    for p in posts:
        hour = int(p["time"].split(":")[0])
        if hour not in hour_stats:
            hour_stats[hour] = {"count": 0, "total_views": 0}
        hour_stats[hour]["count"] += 1
        hour_stats[hour]["total_views"] += p["metrics"]["views"]

    if hour_stats:
        best_hour = max(hour_stats.items(), key=lambda x: x[1]["total_views"]/max(x[1]["count"], 1))
        avg_at_best = best_hour[1]["total_views"] / best_hour[1]["count"]
        console.print(f"\n⏰ [bold]最佳发布时间:[/bold] {best_hour[0]:02d}:00 (平均 {avg_at_best:,.0f} 浏览)")

    # 3. 最佳内容类型
    topic_stats = {}
    for p in posts:
        t_type = p.get("topic_type") or "未分类"
        if t_type not in topic_stats:
            topic_stats[t_type] = {"count": 0, "total_views": 0, "total_engagement": 0}
        topic_stats[t_type]["count"] += 1
        topic_stats[t_type]["total_views"] += p["metrics"]["views"]
        m = p["metrics"]
        topic_stats[t_type]["total_engagement"] += (m["likes"] + m["comments"] + m["shares"] + m["saves"]) / max(m["views"], 1) * 100

    if topic_stats and len(topic_stats) > 1:
        best_topic = max(topic_stats.items(), key=lambda x: x[1]["total_engagement"]/max(x[1]["count"], 1))
        console.print(f"🎯 [bold]最佳内容类型:[/bold] {best_topic[0]} (平均互动率 {best_topic[1]['total_engagement']/best_topic[1]['count']:.1f}%)")

    # 4. 最佳标签
    tag_stats = {}
    for p in posts:
        for tag in p.get("tags", []):
            if tag not in tag_stats:
                tag_stats[tag] = {"count": 0, "total_views": 0}
            tag_stats[tag]["count"] += 1
            tag_stats[tag]["total_views"] += p["metrics"]["views"]

    if tag_stats:
        sorted_tags = sorted(tag_stats.items(), key=lambda x: x[1]["total_views"]/x[1]["count"], reverse=True)
        console.print(f"\n🏷️ [bold]标签表现排名:[/bold]")
        for tag, stats in sorted_tags[:5]:
            avg = stats["total_views"] / stats["count"]
            console.print(f"   #{tag}: 平均 {avg:,.0f} 浏览 ({stats['count']}篇)")

    # 5. 表现最好和最差
    sorted_by_views = sorted(posts, key=lambda p: p["metrics"]["views"], reverse=True)
    best = sorted_by_views[0]
    worst = sorted_by_views[-1]

    console.print(f"\n🏆 [bold]最佳内容:[/bold] 「{best['title'][:25]}」 ({best['metrics']['views']:,} 浏览)")
    console.print(f"📉 [bold]待提升:[/bold] 「{worst['title'][:25]}」 ({worst['metrics']['views']:,} 浏览)")

    # 6. 优化建议
    console.print(f"\n💡 [bold]优化建议:[/bold]")

    suggestions = []

    if avg_engagement < 5:
        suggestions.append("互动率偏低，尝试在结尾增加互动引导（提问/投票/征集）")
    if avg_engagement > 10:
        suggestions.append("互动率优秀！保持当前内容风格")

    if hour_stats:
        worst_hours = [h for h, s in hour_stats.items() if s["total_views"]/max(s["count"],1) < avg_views * 0.5]
        if worst_hours:
            suggestions.append(f"避免在 {', '.join(f'{h}:00' for h in worst_hours)} 发布，数据表现较差")

    if tag_stats and len(sorted_tags) >= 2:
        top_tag = sorted_tags[0][0]
        suggestions.append(f"「{top_tag}」标签表现最好，可以多围绕这个方向创作")

    if len(sorted_by_views) >= 3:
        top3_avg = sum(p["metrics"]["views"] for p in sorted_by_views[:3]) / 3
        bottom3_avg = sum(p["metrics"]["views"] for p in sorted_by_views[-3:]) / 3
        if top3_avg > bottom3_avg * 3:
            suggestions.append("内容表现差异大，分析最佳内容的共同点并复制成功模式")

    for i, s in enumerate(suggestions, 1):
        console.print(f"   {i}. {s}")

    if not suggestions:
        console.print("   表现稳定，继续保持！")

    console.print()


def _rate_view(avg_views):
    """评估浏览量水平"""
    if avg_views >= 10000:
        return "🔥 优秀"
    elif avg_views >= 5000:
        return "👍 良好"
    elif avg_views >= 1000:
        return "📊 一般"
    else:
        return "📈 需提升"


def _rate_engagement(rate):
    """评估互动率水平"""
    if rate >= 10:
        return "🔥 优秀"
    elif rate >= 5:
        return "👍 良好"
    elif rate >= 2:
        return "📊 一般"
    else:
        return "📈 需提升"


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

    # 计算最大平均浏览量（安全处理全0情况）
    max_avg = max((s["total_views"] / max(s["count"], 1)) for s in hour_stats.values())

    for hour in sorted(hour_stats.keys()):
        stats = hour_stats[hour]
        avg = stats["total_views"] / stats["count"]
        bar = "█" * int(avg / max_avg * 15) if max_avg > 0 else "·"
        table.add_row(
            f"{hour:02d}:00",
            str(stats["count"]),
            f"{stats['total_views']:,}",
            f"{avg:,.0f}",
            bar,
        )

    console.print(table)
