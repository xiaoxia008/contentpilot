"""多平台发布适配模块 - P2

从第一性原理: 分发是必要但非核心，作为最后一步的增值功能
"""

import os
import re

import click
from rich.console import Console
from rich.panel import Panel

console = Console()

# 平台格式规则
PLATFORM_FORMATS = {
    "xiaohongshu": {
        "name": "小红书",
        "title_max": 20,
        "content_max": 1000,
        "emoji": "活泼",
        "hashtags": (5, 8),
        "rules": [
            "标题加emoji开头",
            "正文分段用emoji标注",
            "结尾加话题标签",
        ],
    },
    "douyin": {
        "name": "抖音",
        "title_max": 30,
        "content_max": 500,
        "emoji": "简洁",
        "hashtags": (3, 5),
        "rules": [
            "开头要有钩子",
            "段落不宜过长",
            "引导点赞评论",
        ],
    },
    "wechat": {
        "name": "公众号",
        "title_max": 30,
        "content_max": 5000,
        "emoji": "克制",
        "hashtags": (0, 3),
        "rules": [
            "分章节用H2/H3",
            "适合长文深度",
            "结尾引导关注",
        ],
    },
    "zhihu": {
        "name": "知乎",
        "title_max": 30,
        "content_max": 3000,
        "emoji": "少用",
        "hashtags": (0, 2),
        "rules": [
            "逻辑清晰分段",
            "有理有据",
            "专业术语适度",
        ],
    },
    "weibo": {
        "name": "微博",
        "title_max": 15,
        "content_max": 2000,
        "emoji": "适中",
        "hashtags": (1, 3),
        "rules": [
            "开头抓眼球",
            "不超过2000字",
            "互动性强",
        ],
    },
    "bilibili": {
        "name": "B站",
        "title_max": 30,
        "content_max": 3000,
        "emoji": "适度玩梗",
        "hashtags": (3, 5),
        "rules": [
            "标题要有吸引力，可玩梗",
            "内容干货+趣味并重",
            "引导三连(点赞投币收藏)",
            "适当加入B站特色用语",
        ],
    },
    "kuaishou": {
        "name": "快手",
        "title_max": 20,
        "content_max": 1000,
        "emoji": "接地气",
        "hashtags": (3, 5),
        "rules": [
            "语言朴实接地气",
            "真实有烟火气",
            "引导双击关注",
            "避免太书面化",
        ],
    },
}


@click.command()
@click.argument("content", type=click.Path(exists=True))
@click.option("-f", "--from-platform", default="xiaohongshu", help="源平台")
@click.option("-t", "--to", "to_platform", required=True, help="目标平台")
@click.option("-o", "--output", default=None, help="输出文件路径")
def publish(content, from_platform, to_platform, output):
    """多平台发布适配 - 一键转换内容格式。

    CONTENT: 内容文件路径

    \b
    示例:
        contentpilot publish draft.md -f xiaohongshu -t douyin
        contentpilot publish draft.md -f xiaohongshu -t wechat -o output.md
    """
    with open(content, "r", encoding="utf-8") as f:
        text = f.read()

    source = PLATFORM_FORMATS.get(from_platform, PLATFORM_FORMATS["xiaohongshu"])
    target = PLATFORM_FORMATS.get(to_platform, PLATFORM_FORMATS["douyin"])

    console.print(f"\n[cyan]📤 源平台:[/cyan] {source['name']}")
    console.print(f"[cyan]📥 目标平台:[/cyan] {target['name']}")

    # 执行格式转换
    result = _adapt_content(text, source, target)

    if not output:
        base, ext = os.path.splitext(content)
        output = f"{base}_{to_platform}{ext}"

    with open(output, "w", encoding="utf-8") as f:
        f.write(result)

    console.print(f"[green]✓[/green] 转换完成: {output}")

    # 显示预览
    console.print("\n[bold]📝 转换预览:[/bold]\n")
    preview = result[:300] + ("..." if len(result) > 300 else "")
    console.print(Panel(preview, title=f"{target['name']}格式", border_style="green"))

    # 显示适配说明
    console.print("\n[dim]适配规则:[/dim]")
    for rule in target["rules"]:
        console.print(f"  • {rule}")


def _adapt_content(content, source, target):
    """适配内容格式"""
    result = content

    # 清理源平台格式
    result = result.replace("【", "").replace("】", "")

    # 调整emoji密度
    if target["emoji"] == "少用":
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]+",
            flags=re.UNICODE,
        )
        count = 0
        def replace(m):
            nonlocal count
            count += 1
            return m.group() if count <= 2 else ""
        result = emoji_pattern.sub(replace, result)

    # 调整话题标签
    hashtags = re.findall(r"#(\S+)#", result) or re.findall(r"#(\S+)", result)
    if hashtags:
        # 移除原有标签
        result = re.sub(r"#\S+#?\s*", "", result).strip()
        # 按目标平台要求添加
        min_tags, max_tags = target["hashtags"]
        if max_tags > 0:
            selected = hashtags[:max_tags]
            tag_str = " ".join(f"#{tag}" for tag in selected)
            result += f"\n\n{tag_str}"

    return result
