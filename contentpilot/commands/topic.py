"""AI 爆款选题模块 - P0 核心功能

从第一性原理: 选题决定内容天花板，没有好选题再好的文案也没用
"""

import os

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from contentpilot.utils.ai import call_ai
from contentpilot.utils.config import get_api_config

console = Console()

# 选题策略配置
TOPIC_STRATEGIES = {
    "hot": {
        "name": "热点追踪",
        "desc": "结合当下热点，快速出内容",
        "prompt": "你是一位资深自媒体运营专家。请根据以下领域，结合当下热点趋势，生成{count}个高流量潜力的选题。\n\n领域: {niche}\n平台: {platform}\n\n要求:\n1. 每个选题要结合当前热点或普遍痛点\n2. 标题要有情绪钩子，让人忍不住点\n3. 说明为什么这个选题有流量潜力\n4. 预估阅读量级别(高/中/低)\n\n输出格式:\n选题: [标题]\n角度: [切入角度]\n流量潜力: [高/中/低] - [理由]\n---",
    },
    "pain": {
        "name": "痛点挖掘",
        "desc": "解决用户真实痛点，长尾流量",
        "prompt": "你是一位用户研究专家。请针对以下领域，挖掘{count}个用户真实痛点，并转化为内容选题。\n\n领域: {niche}\n目标用户: {audience}\n平台: {platform}\n\n要求:\n1. 基于真实用户场景，不要编造\n2. 痛点要具体，不要泛泛而谈\n3. 每个痛点对应一个可执行的内容选题\n4. 说明解决这个痛点能给用户带来什么价值\n\n输出格式:\n痛点: [用户真实痛点描述]\n选题: [对应的内容标题]\n价值: [解决痛点带来的价值]\n---",
    },
    "evergreen": {
        "name": "常青内容",
        "desc": "长期有搜索价值的内容",
        "prompt": "你是一位SEO和内容策略专家。请针对以下领域，生成{count}个常青内容选题。\n\n领域: {niche}\n平台: {platform}\n\n要求:\n1. 选题要有长期搜索价值，不随热点消退\n2. 内容要能持续获取搜索/推荐流量\n3. 标题要包含用户常搜索的关键词\n4. 说明这个选题的长尾价值\n\n输出格式:\n选题: [标题]\n关键词: [核心搜索词]\n长尾价值: [为什么长期有价值]\n---",
    },
    "series": {
        "name": "系列内容",
        "desc": "打造内容矩阵，提升账号权重",
        "prompt": "你是一位内容策略专家。请针对以下领域，设计一个包含{count}篇内容的系列选题。\n\n领域: {niche}\n平台: {platform}\n\n要求:\n1. 系列要有清晰的主题线和递进逻辑\n2. 每篇内容独立成章，又能相互引流\n3. 第一篇要能吸引关注，最后一篇要能引发分享\n4. 说明系列的整体策略和每篇的定位\n\n输出格式:\n系列主题: [整体主题]\n\n第N篇:\n标题: [标题]\n定位: [这篇在系列中的角色]\n引流点: [如何引导看下一篇]\n---",
    },
}


@click.group()
def topic():
    """AI 爆款选题 - 找到有流量潜力的内容方向。

    \b
    示例:
        contentpilot topic hot "Python教程" -p xiaohongshu
        contentpilot topic pain "减肥" --audience "上班族"
        contentpilot topic evergreen "理财入门"
        contentpilot topic series "AI工具使用" -n 5
    """
    pass


@topic.command("hot")
@click.argument("niche")
@click.option("-p", "--platform", default="xiaohongshu", help="目标平台")
@click.option("-n", "--count", default=5, help="生成数量")
def hot_topics(niche, platform, count):
    """热点追踪选题 - 结合当下热点快速出内容。"""
    _generate_topics("hot", niche, platform, count, {})


@topic.command("pain")
@click.argument("niche")
@click.option("--audience", default="大众", help="目标受众")
@click.option("-p", "--platform", default="xiaohongshu", help="目标平台")
@click.option("-n", "--count", default=5, help="生成数量")
def pain_topics(niche, audience, platform, count):
    """痛点挖掘选题 - 解决用户真实痛点。"""
    _generate_topics("pain", niche, platform, count, {"audience": audience})


@topic.command("evergreen")
@click.argument("niche")
@click.option("-p", "--platform", default="xiaohongshu", help="目标平台")
@click.option("-n", "--count", default=5, help="生成数量")
def evergreen_topics(niche, platform, count):
    """常青内容选题 - 长期有搜索价值。"""
    _generate_topics("evergreen", niche, platform, count, {})


@topic.command("series")
@click.argument("niche")
@click.option("-p", "--platform", default="xiaohongshu", help="目标平台")
@click.option("-n", "--count", default=5, help="系列篇数")
def series_topics(niche, platform, count):
    """系列内容选题 - 打造内容矩阵。"""
    _generate_topics("series", niche, platform, count, {})


def _generate_topics(strategy_name, niche, platform, count, extra):
    """生成选题"""
    api_key, base_url, model = get_api_config()
    if not api_key:
        console.print("[red]✗[/red] 请设置 OPENAI_API_KEY")
        return

    strategy = TOPIC_STRATEGIES[strategy_name]

    console.print(f"\n[cyan]🎯 选题策略:[/cyan] {strategy['name']}")
    console.print(f"[cyan]📍 领域:[/cyan] {niche}")
    console.print(f"[cyan]📱 平台:[/cyan] {platform}")
    console.print("\n[green]AI 正在挖掘选题...[/green]\n")

    prompt = strategy["prompt"].format(
        niche=niche, platform=platform, count=count, **extra
    )

    result = call_ai(prompt, api_key, base_url, model)

    if result:
        # 按分隔符拆分
        topics = [t.strip() for t in result.split("---") if t.strip()]
        for i, t in enumerate(topics, 1):
            console.print(Panel(t, title=f"💡 选题 {i}", border_style="cyan"))

        # 保存
        output_file = f"topics_{strategy_name}_{niche}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]✓[/green] 已保存: {output_file}")


@topic.command("trending")
@click.argument("niche")
@click.option("-p", "--platform", default="xiaohongshu", help="目标平台")
def trending(niche, platform):
    """分析当前热门话题趋势（需要API）。"""
    api_key, base_url, model = get_api_config()
    if not api_key:
        console.print("[red]✗[/red] 请设置 OPENAI_API_KEY")
        return

    console.print(f"\n[cyan]🔥 分析 {niche} 在 {platform} 的热门趋势...[/cyan]\n")

    prompt = f"""你是一位数据分析师。请分析"{niche}"领域在{platform}平台当前的热门趋势。

请提供:
1. 当前最火的5个相关话题
2. 每个话题的热度(高/中/低)
3. 用户最关心的问题
4. 内容空白点(竞争少但需求大的方向)
5. 建议的切入角度

输出为结构化分析报告。"""

    result = call_ai(prompt, api_key, base_url, model)
    if result:
        console.print(Panel(result, title=f"🔥 {niche} 趋势分析", border_style="red"))
