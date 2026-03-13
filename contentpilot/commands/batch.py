"""AI 批量生成模块 - 新功能

一次性生成多个选题的初稿，提升创作效率
"""

import os

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

from contentpilot.utils.ai import call_ai
from contentpilot.utils.config import get_api_config

console = Console()


@click.command("batch")
@click.argument("topics_file", type=click.Path(exists=True))
@click.option("-p", "--platform", default="xiaohongshu", help="目标平台")
@click.option("-o", "--output-dir", default="output", help="输出目录")
@click.option("--style", default=None, help="统一风格")
def batch(topics_file, platform, output_dir, style):
    """批量生成 - 从选题文件批量生成初稿。

    TOPICS_FILE: 选题文件（每行一个选题）

    \b
    示例:
        contentpilot batch topics.txt -p xiaohongshu
        contentpilot batch topics.txt -p douyin --style 幽默
    """
    api_key, base_url, model = get_api_config()
    if not api_key:
        console.print("[red]✗[/red] 请设置 OPENAI_API_KEY")
        return

    # 读取选题
    with open(topics_file, "r", encoding="utf-8") as f:
        topics = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not topics:
        console.print("[red]✗[/red] 选题文件为空")
        return

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    console.print(f"\n[cyan]📄 选题文件:[/cyan] {topics_file}")
    console.print(f"[cyan]📱 平台:[/cyan] {platform}")
    console.print(f"[cyan]📝 选题数量:[/cyan] {len(topics)}")
    console.print(f"[cyan]📁 输出目录:[/cyan] {output_dir}")
    console.print()

    platform_styles = {
        "xiaohongshu": "小红书风格: 活泼亲切、带emoji、口语化",
        "douyin": "抖音风格: 简洁有力、开头有钩子",
        "bilibili": "B站风格: 年轻化、有梗、干货+趣味",
        "wechat": "公众号风格: 专业深度、分章节",
        "zhihu": "知乎风格: 理性专业、有理有据",
        "weibo": "微博风格: 短平快、有情绪",
        "kuaishou": "快手风格: 接地气、真实",
    }
    p_style = platform_styles.get(platform, platform_styles["xiaohongshu"])
    style_str = f"\n语气风格: {style}" if style else ""

    success = 0
    with Progress() as progress:
        task = progress.add_task("生成中...", total=len(topics))

        for i, topic in enumerate(topics, 1):
            progress.update(task, description=f"[{i}/{len(topics)}] {topic[:15]}...")

            prompt = f"""你是一位{platform}内容创作专家。

选题: {topic}
{p_style}{style_str}

请生成完整的帖子内容，包含标题、正文、互动引导和话题标签。"""

            result = call_ai(prompt, api_key, base_url, model)

            if result:
                # 保存到文件
                filename = f"{i:02d}_{topic[:20].replace(' ', '_')}.md"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# {topic}\n\n{result}")
                success += 1

            progress.advance(task)

    console.print(f"\n[green]✅ 批量生成完成！成功 {success}/{len(topics)}[/green]")
    console.print(f"[green]📁 输出目录: {output_dir}[/green]")
