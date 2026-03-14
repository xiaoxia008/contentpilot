"""AI 标题优化模块 - P1

从第一性原理: 标题决定点击率，平台算法匹配的关键
"""

import click
from rich.console import Console
from rich.panel import Panel

from contentpilot.utils.ai import call_ai
from contentpilot.utils.config import get_api_config
from contentpilot.utils.validators import PLATFORM, COUNT

console = Console()


@click.command()
@click.argument("content", type=click.Path(exists=True))
@click.option("-p", "--platform", default="xiaohongshu", type=PLATFORM, help="目标平台")
@click.option("-n", "--count", default=5, type=COUNT, help="生成数量(1-20)")
@click.option("-o", "--output", default=None, help="输出文件路径")
def title(content, platform, count, output):
    """AI 标题优化 - 生成多个高点击率标题备选。

    CONTENT: 已有内容文件路径

    \b
    示例:
        contentpilot title draft.md -p xiaohongshu -n 5
        contentpilot title draft.md -p douyin
    """
    api_key, base_url, model = get_api_config()
    if not api_key:
        console.print("[red]✗[/red] 请设置 OPENAI_API_KEY")
        return

    # 读取内容
    with open(content, "r", encoding="utf-8") as f:
        text = f.read()

    console.print(f"\n[cyan]📄 内容文件:[/cyan] {content}")
    console.print(f"[cyan]📱 平台:[/cyan] {platform}")
    console.print("\n[green]AI 正在生成标题...[/green]\n")

    prompt = f"""你是一位{platform}爆款标题专家。

请为以下内容生成{count}个高点击率标题。

内容摘要:
{text[:500]}...

要求:
1. 标题要能激发好奇心/情绪共鸣
2. 使用数字、疑问、冲突等技巧
3. 符合{platform}平台调性
4. 每个标题后面标注点击率预估(高/中/低)和理由

输出格式:
标题: [标题内容]
预估: [高/中/低] - [理由]
---"""

    result = call_ai(prompt, api_key, base_url, model)
    if result:
        titles = [t.strip() for t in result.split("---") if t.strip()]
        for i, t in enumerate(titles, 1):
            console.print(Panel(t, title=f"📌 标题方案 {i}", border_style="cyan"))

        if not output:
            output = "title_suggestions.txt"
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]✓[/green] 已保存: {output}")
