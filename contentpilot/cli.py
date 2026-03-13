"""ContentPilot CLI 入口"""

import click
from rich.console import Console

from contentpilot import __version__
from contentpilot.commands.topic import topic
from contentpilot.commands.draft import draft
from contentpilot.commands.title import title
from contentpilot.commands.analyze import analyze
from contentpilot.commands.publish import publish

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="ContentPilot")
def cli():
    """ContentPilot - AI内容创作全流程助手

    从选题到发布，帮创作者持续产出好内容获取流量。

    工作流: topic(选题) → draft(初稿) → title(标题优化) → analyze(竞品分析) → publish(多平台发布)
    """
    pass


cli.add_command(topic)
cli.add_command(draft)
cli.add_command(title)
cli.add_command(analyze)
cli.add_command(publish)


if __name__ == "__main__":
    cli()
