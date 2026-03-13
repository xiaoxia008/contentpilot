"""ContentPilot CLI 入口"""

import click
from rich.console import Console

from contentpilot import __version__
from contentpilot.commands.topic import topic
from contentpilot.commands.draft import draft
from contentpilot.commands.title import title
from contentpilot.commands.analyze import analyze
from contentpilot.commands.publish import publish
from contentpilot.commands.batch import batch
from contentpilot.commands.inspire import inspire
from contentpilot.commands.track import track
from contentpilot.commands.check import check

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="ContentPilot")
def cli():
    """ContentPilot - AI内容创作助手

    帮你找到好选题、写出好内容、优化发布策略。

    工作流: topic(选题) → draft(初稿) → title(标题优化) → publish(发布适配) → track(数据追踪) → inspire(灵感衍生)
    """
    pass


cli.add_command(topic)
cli.add_command(draft)
cli.add_command(title)
cli.add_command(analyze)
cli.add_command(publish)
cli.add_command(batch)
cli.add_command(inspire)
cli.add_command(track)
cli.add_command(check)


if __name__ == "__main__":
    cli()
