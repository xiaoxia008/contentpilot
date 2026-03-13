"""内容复用模块 - 第一性原理推导的核心功能

本质洞见: 一篇好内容应该被最大化利用
- 同一篇内容适配不同平台（已完成: publish）
- 一篇长内容拆分为多篇短内容（新增）
- 文字内容转为其他形式（新增）
"""

import os

import click
from rich.console import Console
from rich.panel import Panel

from contentpilot.utils.ai import call_ai
from contentpilot.utils.config import get_api_config

console = Console()


@click.group()
def repurpose():
    """内容复用 - 把一篇内容变成多篇，最大化内容价值。

    \b
    示例:
        contentpilot repurpose split article.md -p xiaohongshu -n 5
        contentpilot repurpose to-video article.md -p douyin
        contentpilot repurpose to-thread article.md -p weibo
    """
    pass


@repurpose.command("split")
@click.argument("content_file", type=click.Path(exists=True))
@click.option("-p", "--platform", default="xiaohongshu", help="目标平台")
@click.option("-n", "--count", default=5, help="拆分为几篇")
@click.option("-o", "--output-dir", default="repurposed", help="输出目录")
def split_content(content_file, platform, count, output_dir):
    """长文拆分 - 把一篇长内容拆为多篇短内容。

    \b
    示例:
        contentpilot repurpose split 文章.md -p xiaohongshu -n 5
    """
    api_key, base_url, model = get_api_config()
    if not api_key:
        console.print("[red]✗[/red] 请设置 OPENAI_API_KEY")
        return

    with open(content_file, "r", encoding="utf-8") as f:
        content = f.read()

    os.makedirs(output_dir, exist_ok=True)

    console.print(f"\n[cyan]📄 原文:[/cyan] {content_file}")
    console.print(f"[cyan]📱 目标平台:[/cyan] {platform}")
    console.print(f"[cyan]🔢 拆分数量:[/cyan] {count}")
    console.print("\n[green]AI 正在拆分...[/green]\n")

    prompt = f"""你是一位内容策略专家。请把以下长文拆分为{count}篇独立的{platform}短文。

要求:
1. 每篇短文独立成章，不需要依赖原文
2. 每篇都有自己的标题和完整的开头/结尾
3. 按照逻辑递进排列，第一篇最吸引人
4. 符合{platform}平台调性
5. 每篇末尾引导看下一篇

原文:
{content[:2000]}

请输出{count}篇完整的短文，用"===SEPARATOR==="分隔每篇。"""

    result = call_ai(prompt, api_key, base_url, model)
    if result:
        articles = [a.strip() for a in result.split("===SEPARATOR===") if a.strip()]
        for i, article in enumerate(articles, 1):
            filepath = os.path.join(output_dir, f"part_{i}.md")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(article)
            console.print(Panel(article[:200] + "...", title=f"📝 第{i}篇", border_style="cyan"))

        console.print(f"\n[green]✅ 已拆分为 {len(articles)} 篇，保存到 {output_dir}/[/green]")


@repurpose.command("to-video")
@click.argument("content_file", type=click.Path(exists=True))
@click.option("-p", "--platform", default="douyin", help="目标平台")
@click.option("-o", "--output", default=None, help="输出文件路径")
def to_video_script(content_file, platform, output):
    """文字转视频脚本 - 把文章转为短视频脚本。

    \b
    示例:
        contentpilot repurpose to-video 文章.md -p douyin
    """
    api_key, base_url, model = get_api_config()
    if not api_key:
        console.print("[red]✗[/red] 请设置 OPENAI_API_KEY")
        return

    with open(content_file, "r", encoding="utf-8") as f:
        content = f.read()

    console.print(f"\n[cyan]📄 原文:[/cyan] {content_file}")
    console.print(f"[cyan]📱 目标平台:[/cyan] {platform}")
    console.print("\n[green]AI 正在生成视频脚本...[/green]\n")

    prompt = f"""你是一位短视频编导。请把以下文字内容转为{platform}短视频脚本。

原文:
{content[:1500]}

要求:
1. 时长控制在60秒以内
2. 开头3秒必须有钩子
3. 标注画面建议和文字叠加
4. 标注口播文案
5. 结尾引导互动
6. 语言口语化，有节奏感

输出格式:
【画面】描述画面
【文字】屏幕上的文字
【口播】配音文案
---"""

    result = call_ai(prompt, api_key, base_url, model)
    if result:
        console.print(Panel(result, title=f"🎬 {platform}视频脚本", border_style="magenta"))

        if not output:
            output = f"video_script_{platform}.md"
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]✓[/green] 已保存: {output}")


@repurpose.command("to-thread")
@click.argument("content_file", type=click.Path(exists=True))
@click.option("-p", "--platform", default="weibo", help="目标平台")
@click.option("-o", "--output", default=None, help="输出文件路径")
def to_thread(content_file, platform, output):
    """转为话题帖 - 把长文转为微博/B站动态话题帖。

    \b
    示例:
        contentpilot repurpose to-thread 文章.md -p weibo
        contentpilot repurpose to-thread 文章.md -p bilibili
    """
    api_key, base_url, model = get_api_config()
    if not api_key:
        console.print("[red]✗[/red] 请设置 OPENAI_API_KEY")
        return

    with open(content_file, "r", encoding="utf-8") as f:
        content = f.read()

    console.print(f"\n[cyan]📄 原文:[/cyan] {content_file}")
    console.print(f"[cyan]📱 目标平台:[/cyan] {platform}")
    console.print("\n[green]AI 正在生成话题帖...[/green]\n")

    prompt = f"""你是一位{platform}运营专家。请把以下长文转为{platform}话题帖格式。

原文:
{content[:1500]}

要求:
1. 每条不超过平台字数限制
2. 编号排列，逻辑递进
3. 第一条要有吸引力
4. 最后一条引导讨论
5. 适当使用emoji
6. 语言符合平台调性

输出格式:
第N条: [内容]
---"""

    result = call_ai(prompt, api_key, base_url, model)
    if result:
        console.print(Panel(result, title=f"🧵 {platform}话题帖", border_style="green"))

        if not output:
            output = f"thread_{platform}.md"
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]✓[/green] 已保存: {output}")
