"""AI 初稿生成模块 - 集成平台专用模板"""

import os

import click
from rich.console import Console
from rich.panel import Panel

from contentpilot.utils.ai import call_ai
from contentpilot.utils.config import get_api_config
from contentpilot.utils.templates import get_template, list_templates, PLATFORM_TEMPLATES

console = Console()


@click.command()
@click.argument("topic")
@click.option("-p", "--platform", default="xiaohongshu", help="目标平台")
@click.option("--style", default=None, help="语气风格")
@click.option("--template", default=None, help="使用专用模板")
@click.option("-o", "--output", default=None, help="输出文件路径")
def draft(topic, platform, style, template, output):
    """AI 初稿生成 - 从选题直接生成可发布的初稿。

    支持平台专用模板: 小红书(种草/探店/教程/好物), 抖音(脚本/直播/标题), B站(视频/动态)

    \b
    示例:
        contentpilot draft "Python自动化办公" -p xiaohongshu
        contentpilot draft "咖啡店探店" -p xiaohongshu --template 探店文案
        contentpilot draft "Python教程" -p douyin --template 短视频脚本
    """
    api_key, base_url, model = get_api_config()
    if not api_key:
        console.print("[red]✗[/red] 请设置 OPENAI_API_KEY")
        return

    console.print(f"\n[cyan]📝 选题:[/cyan] {topic}")
    console.print(f"[cyan]📱 平台:[/cyan] {platform}")
    if template:
        console.print(f"[cyan]📋 模板:[/cyan] {template}")
    console.print("\n[green]AI 正在创作...[/green]\n")

    # 优先使用专用模板
    if template:
        tmpl = get_template(platform, template)
        if tmpl:
            prompt = tmpl["prompt"].format(topic=topic)
        else:
            console.print(f"[yellow]⚠️ 未找到模板 '{template}'，使用通用生成[/yellow]")
            prompt = _generic_prompt(platform, topic, style)
    else:
        prompt = _generic_prompt(platform, topic, style)

    if style:
        prompt += f"\n语气风格: {style}"

    result = call_ai(prompt, api_key, base_url, model)

    if result:
        console.print(Panel(result, title=f"📄 {topic}", border_style="green"))

        if not output:
            safe_topic = topic[:20].replace(" ", "_")
            output = f"draft_{platform}_{safe_topic}.md"
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]✓[/green] 已保存: {output}")
        console.print("\n[dim]💡 下一步: contentpilot title 优化标题 | contentpilot check 检测违禁词[/dim]")


def _generic_prompt(platform, topic, style):
    """通用生成 prompt"""
    platform_styles = {
        "xiaohongshu": "小红书风格: 活泼亲切、带emoji、口语化、引发互动",
        "douyin": "抖音风格: 简洁有力、有节奏感、开头有钩子",
        "wechat": "公众号风格: 专业深度、有观点、分章节",
        "zhihu": "知乎风格: 理性专业、有理有据",
        "weibo": "微博风格: 短平快、有情绪、互动性强",
        "bilibili": "B站风格: 年轻化、有梗、干货+趣味",
        "kuaishou": "快手风格: 接地气、真实",
    }
    p_style = platform_styles.get(platform, platform_styles["xiaohongshu"])

    return f"""你是一位{platform}内容创作专家。

选题: {topic}
风格: {p_style}

请生成完整的帖子内容，包含:
1. 标题（吸引眼球）
2. 正文（分段清晰，适当emoji）
3. 结尾互动引导
4. 话题标签(3-8个)

直接输出，不要解释。"""
