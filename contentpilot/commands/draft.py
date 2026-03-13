"""AI 初稿生成模块 - P0 核心功能

从第一性原理: 解决"写不出来"的核心痛点
"""

import os

import click
from rich.console import Console
from rich.panel import Panel

from contentpilot.utils.ai import call_ai
from contentpilot.utils.config import get_api_config

console = Console()

# 平台风格
PLATFORM_STYLES = {
    "xiaohongshu": "小红书风格: 活泼亲切、带emoji、口语化、引发互动、15-20字标题",
    "douyin": "抖音风格: 简洁有力、有节奏感、开头要有钩子、引导完播",
    "wechat": "公众号风格: 专业深度、有观点、分章节、信息量大",
    "zhihu": "知乎风格: 理性专业、有理有据、干货多、直接切入主题",
    "weibo": "微博风格: 短平快、有情绪、互动性强、引发转发",
}


@click.command()
@click.argument("topic")
@click.option("-p", "--platform", default="xiaohongshu", help="目标平台")
@click.option("--style", default=None, help="语气风格 (如: 专业/幽默/温暖)")
@click.option("--outline", is_flag=True, help="先生成大纲，确认后再生成正文")
@click.option("-o", "--output", default=None, help="输出文件路径")
def draft(topic, platform, style, outline, output):
    """AI 初稿生成 - 从选题直接生成可发布的初稿。

    TOPIC: 选题或标题

    \b
    示例:
        contentpilot draft "5个减肥食谱推荐" -p xiaohongshu
        contentpilot draft "Python入门教程" -p douyin --style 专业
        contentpilot draft "理财心得" -p wechat --outline
    """
    api_key, base_url, model = get_api_config()
    if not api_key:
        console.print("[red]✗[/red] 请设置 OPENAI_API_KEY")
        return

    platform_style = PLATFORM_STYLES.get(platform, PLATFORM_STYLES["xiaohongshu"])
    style_str = f"\n语气风格: {style}" if style else ""

    console.print(f"\n[cyan]📝 选题:[/cyan] {topic}")
    console.print(f"[cyan]📱 平台:[/cyan] {platform}")
    console.print("\n[green]AI 正在创作...[/green]\n")

    if outline:
        # 先生成大纲
        outline_prompt = f"""你是一位{platform}内容创作专家。

选题: {topic}
{platform_style}{style_str}

请先生成内容大纲，包含:
1. 开头钩子（如何抓住注意力）
2. 核心要点（3-5个，每个一句话说明）
3. 结尾互动引导

输出简洁的大纲，不需要展开写。"""

        result = call_ai(outline_prompt, api_key, base_url, model)
        if result:
            console.print(Panel(result, title="📋 内容大纲", border_style="yellow"))
            console.print("\n[dim]确认大纲后，直接运行不带 --outline 生成完整初稿[/dim]")
        return

    # 生成完整初稿
    draft_prompt = f"""你是一位{platform}内容创作专家。

选题: {topic}
{platform_style}{style_str}

请生成一篇完整的帖子内容，要求:
1. 标题吸引眼球
2. 开头3秒抓住注意力
3. 正文分段清晰，每段有小标题
4. 适当使用emoji增加可读性
5. 结尾引导互动（点赞/评论/收藏）
6. 附上5-8个相关话题标签

直接输出完整内容，不要有多余解释。"""

    result = call_ai(draft_prompt, api_key, base_url, model)
    if result:
        console.print(Panel(result, title=f"📄 {topic}", border_style="green"))

        # 保存
        if not output:
            output = f"draft_{platform}.md"
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]✓[/green] 已保存: {output}")

        # 提示下一步
        console.print("\n[dim]💡 下一步: contentpilot title 优化标题 | contentpilot publish 适配多平台[/dim]")
