"""竞品内容分析模块 - P1

从第一性原理: 学习爆款的底层逻辑，不靠猜测
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from contentpilot.utils.ai import call_ai
from contentpilot.utils.config import get_api_config

console = Console()


@click.command()
@click.argument("niche")
@click.option("-p", "--platform", default="xiaohongshu", help="目标平台")
@click.option("--url", default=None, help="竞品内容链接（用于分析）")
@click.option("--text", default=None, help="竞品内容文本（直接粘贴）")
def analyze(niche, platform, url, text):
    """竞品内容分析 - 学习爆款背后的逻辑。

    NICHE: 领域/关键词

    \b
    示例:
        contentpilot analyze "减肥" -p xiaohongshu
        contentpilot analyze "Python" --text "竞品内容全文"
    """
    api_key, base_url, model = get_api_config()
    if not api_key:
        console.print("[red]✗[/red] 请设置 OPENAI_API_KEY")
        return

    console.print(f"\n[cyan]🔍 分析领域:[/cyan] {niche}")
    console.print(f"[cyan]📱 平台:[/cyan] {platform}")
    console.print("\n[green]AI 正在分析竞品...[/green]\n")

    if text:
        # 分析具体内容
        prompt = f"""你是一位内容策略分析师。请深度分析以下{platform}内容。

内容:
{text}

请从以下维度分析:
1. **标题分析**: 标题用了什么技巧？为什么能吸引点击？
2. **开头分析**: 前3秒/前3行是如何抓住注意力的？
3. **结构分析**: 内容结构是怎样的？为什么这样设计？
4. **情绪分析**: 调动了什么情绪？如何引发共鸣？
5. **互动分析**: 如何引导互动的？用了什么话术？
6. **可复用点**: 这篇内容有哪些技巧可以复用？
7. **改进点**: 有哪些可以做得更好的地方？

输出结构化分析报告。"""
    else:
        # 分析领域爆款规律
        prompt = f"""你是一位内容策略分析师。请分析{platform}上"{niche}"领域的爆款内容规律。

请提供:
1. **爆款标题公式**: 总结5个最常用的标题模板
2. **内容结构模板**: 爆款内容通常采用什么结构？
3. **情绪触发点**: 这个领域最能引发互动的情绪点是什么？
4. **发布时间**: 最佳发布时间分析
5. **内容空白**: 竞争少但需求大的细分方向
6. **差异化策略**: 新账号如何在这个领域脱颖而出

输出可执行的策略报告，包含具体示例。"""

    result = call_ai(prompt, api_key, base_url, model)
    if result:
        console.print(Panel(result, title=f"📊 {niche} 竞品分析", border_style="magenta"))

        output = f"analysis_{niche}.md"
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]✓[/green] 已保存: {output}")
