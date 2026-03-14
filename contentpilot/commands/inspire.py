"""灵感衍生模块 - 从趋势和主题创作原创内容

核心理念: 不是"复用"别人的内容，而是从趋势和主题出发创作全新内容
- 从趋势衍生选题（一个主题 → 多个原创角度）
- 从已有内容获取灵感（自己的内容 → 新的创作方向）
- 跨形式创作（同一主题 → 不同形式的原创内容）
"""

import os
import re

import click
from rich.console import Console
from rich.panel import Panel

from contentpilot.utils.ai import call_ai
from contentpilot.utils.config import get_api_config

console = Console()


@click.group()
def inspire():
    """灵感衍生 - 从趋势和主题创作原创内容。

    \b
    示例:
        contentpilot inspire angles "AI教育" -p xiaohongshu -n 5
        contentpilot inspire from-trend "新能源汽车" -p douyin
        contentpilot inspire video-ideas "Python教程" -n 3
    """
    pass


@inspire.command("angles")
@click.argument("topic")
@click.option("-p", "--platform", default="xiaohongshu", help="目标平台")
@click.option("-n", "--count", default=5, help="衍生数量")
def find_angles(topic, platform, count):
    """从一个主题找到多个原创角度。

    同一个主题，不同人有不同切入角度。
    这个功能帮你找到最有流量潜力的原创角度。

    \b
    示例:
        contentpilot inspire angles "AI教育" -n 5
    """
    api_key, base_url, model = get_api_config()
    if not api_key:
        console.print("[red]✗[/red] 请设置 OPENAI_API_KEY")
        return

    console.print(f"\n[cyan]💡 主题:[/cyan] {topic}")
    console.print(f"[cyan]📱 平台:[/cyan] {platform}")
    console.print("\n[green]AI 正在寻找原创角度...[/green]\n")

    prompt = f"""你是一位{platform}内容策略专家。

主题: {topic}

请为这个主题找到{count}个不同的原创切入角度。要求:
1. 每个角度都要独特，不重复
2. 角度要新颖，避免老生常谈
3. 每个角度要能引发目标读者的兴趣
4. 说明每个角度的独特价值和目标读者
5. 提供一个能激发原创写作的提示（不是现成文案）

输出格式:
角度N: [角度名称]
- 独特视角: [这个角度有什么独特之处]
- 目标读者: [谁会对这个角度感兴趣]
- 创作提示: [一个能激发写作灵感的问题或提示]
---"""

    result = call_ai(prompt, api_key, base_url, model)
    if result:
        angles = [a.strip() for a in result.split("---") if a.strip()]
        for i, angle in enumerate(angles, 1):
            console.print(Panel(angle, title=f"🎯 原创角度 {i}", border_style="cyan"))

        safe_topic = re.sub(r'[^\w\u4e00-\u9fff-]', '_', topic)[:20]
        safe_topic = re.sub(r'_+', '_', safe_topic).strip('_') or "untitled"
        output_file = f"angles_{safe_topic}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]✓[/green] 已保存: {output_file}")


@inspire.command("from-trend")
@click.argument("trend")
@click.option("-p", "--platform", default="xiaohongshu", help="目标平台")
@click.option("-n", "--count", default=5, help="衍生数量")
def from_trend(trend, platform, count):
    """从趋势热点衍生原创内容灵感。

    不是抄热点，而是从热点中找到你独特的创作角度。

    \b
    示例:
        contentpilot inspire from-trend "新能源汽车降价" -n 5
    """
    api_key, base_url, model = get_api_config()
    if not api_key:
        console.print("[red]✗[/red] 请设置 OPENAI_API_KEY")
        return

    console.print(f"\n[cyan]🔥 趋势热点:[/cyan] {trend}")
    console.print(f"[cyan]📱 平台:[/cyan] {platform}")
    console.print("\n[green]AI 正在从趋势衍生原创灵感...[/green]\n")

    prompt = f"""你是一位{platform}内容策略专家。

当前热点: {trend}

请从这个热点中衍生{count}个原创内容方向。要求:
1. 不是简单复述热点，而是找到独特的创作角度
2. 每个方向要有你的独特观点或见解
3. 避免人云亦云，要有差异化
4. 每个方向给出一个具体的创作提示

输出格式:
方向N: [标题方向]
- 独特观点: [你对这个角度的独特看法]
- 为什么有流量: [这个角度的传播价值]
- 创作提示: [具体可以写什么]
---"""

    result = call_ai(prompt, api_key, base_url, model)
    if result:
        ideas = [i.strip() for i in result.split("---") if i.strip()]
        for i, idea in enumerate(ideas, 1):
            console.print(Panel(idea, title=f"💡 原创灵感 {i}", border_style="yellow"))


@inspire.command("video-ideas")
@click.argument("topic")
@click.option("-p", "--platform", default="douyin", help="目标平台")
@click.option("-n", "--count", default=3, help="数量")
def video_ideas(topic, platform, count):
    """从文字内容主题衍生视频创意。

    同一个主题，如何用视频形式讲出新意？

    \b
    示例:
        contentpilot inspire video-ideas "Python教程" -p douyin
    """
    api_key, base_url, model = get_api_config()
    if not api_key:
        console.print("[red]✗[/red] 请设置 OPENAI_API_KEY")
        return

    console.print(f"\n[cyan]📝 主题:[/cyan] {topic}")
    console.print(f"[cyan]📱 视频平台:[/cyan] {platform}")
    console.print("\n[green]AI 正在衍生视频创意...[/green]\n")

    prompt = f"""你是一位{platform}短视频策划专家。

主题: {topic}

请为这个主题设计{count}个不同的短视频创意。要求:
1. 每个创意都要独特，有记忆点
2. 适合{platform}平台的风格
3. 开头要有钩子
4. 给出具体的画面建议和脚本框架

输出格式:
创意N: [视频标题]
- 时长: [建议时长]
- 钩子: [开头3秒如何抓住注意力]
- 画面: [具体的视觉呈现方式]
- 脚本框架: [开头-中间-结尾的结构]
---"""

    result = call_ai(prompt, api_key, base_url, model)
    if result:
        ideas = [i.strip() for i in result.split("---") if i.strip()]
        for i, idea in enumerate(ideas, 1):
            console.print(Panel(idea, title=f"🎬 视频创意 {i}", border_style="magenta"))
