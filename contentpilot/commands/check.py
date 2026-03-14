"""违禁词检测模块 - 整合句易网级别的检测能力

检测广告法违禁词、平台敏感词、夸大宣传等
"""

import re
import os

import click
from rich.console import Console
from rich.table import Table

console = Console()

# ===== 违禁词库 =====
SENSITIVE_WORDS = {
    "广告法违禁词": {
        "desc": "《广告法》明确禁止使用的绝对化用语",
        "words": [
            "最好", "最佳", "最优", "最先进", "第一", "唯一", "首选",
            "顶级", "极致", "巅峰", "绝无仅有", "史无前例", "万能",
            "永久", "100%", "绝对", "完全", "彻底", "根本性",
            "国家级", "世界级", "最高级", "最低价", "全网最低",
            "独一无二", "空前绝后", "无与伦比", "首屈一指",
        ],
    },
    "医疗健康违禁词": {
        "desc": "医疗健康领域违规宣传用语",
        "words": [
            "治愈", "根治", "药到病除", "包治百病", "祖传秘方",
            "立即见效", "无副作用", "零风险", "保证有效",
            "癌症克星", "糖尿病救星", "降压神药", "治疗",
            "疗效", "药效", "治愈率", "康复率",
        ],
    },
    "金融投资违禁词": {
        "desc": "金融投资领域违规承诺用语",
        "words": [
            "稳赚", "保本", "零风险高收益", "内幕消息", "必涨",
            "涨停板", "翻倍", "暴富", "无风险", "保证收益",
            "稳赢", "包赚", "只赚不赔",
        ],
    },
    "平台敏感词": {
        "desc": "各平台可能限流的敏感词",
        "words": [
            "加微信", "私信我", "VX", "微信号", "加V", "扫码",
            "加我微信", "微信联系", "私聊", "公众号后台",
            "淘宝搜索", "拼多多搜索", "京东搜索",
            "免费领", "免费送", "0元购", "白嫖",
        ],
    },
    "夸大宣传": {
        "desc": "容易被判定为夸大宣传的用语",
        "words": [
            "震惊", "惊呆", "吓尿", "炸裂", "逆天", "神了",
            "不可能", "绝对不会", "保证", "承诺", "100%有效",
            "必火", "必看", "必买", "必收藏", "强烈推荐",
            "史上最强", "年度最佳", "全网首发",
        ],
    },
}


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", default=None, help="输出报告路径")
@click.option("--strict", is_flag=True, help="严格模式（包含所有分类）")
@click.option("--category", default=None, help="指定检测分类")
def check(input_file, output, strict, category):
    """违禁词/敏感词检测。

    检查文案中的违禁词和敏感词，避免被平台限流或处罚。

    \b
    示例:
        contentpilot check post.md
        contentpilot check post.md --strict
        contentpilot check post.md --category "平台敏感词"
    """
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    console.print(f"\n[cyan]📄 检测文件:[/cyan] {input_file}")
    console.print(f"[cyan]📊 文案长度:[/cyan] {len(content)} 字符\n")

    # 选择检测分类
    if category:
        categories = {category: SENSITIVE_WORDS[category]} if category in SENSITIVE_WORDS else {}
    elif strict:
        categories = SENSITIVE_WORDS
    else:
        # 默认只检测平台敏感词和夸大宣传
        categories = {k: v for k, v in SENSITIVE_WORDS.items()
                     if k in ["平台敏感词", "夸大宣传"]}

    found = _check_content(content, categories)

    if not found:
        console.print("[green]✅ 恭喜！未检测到违禁词或敏感词。[/green]")
        return

    total = sum(len(words) for words in found.values())
    console.print(f"[yellow]⚠️  检测到 {total} 个可疑词汇[/yellow]\n")

    table = Table(title="🔍 检测结果")
    table.add_column("类别", style="cyan", width=15)
    table.add_column("词汇", style="red", width=15)
    table.add_column("次数", width=5, justify="right")
    table.add_column("上下文", width=40)
    table.add_column("建议替换", style="green", width=15)

    for category_name, words in found.items():
        for word_info in words:
            table.add_row(
                category_name,
                word_info["word"],
                str(word_info["count"]),
                word_info["context"],
                word_info.get("suggestion", "-"),
            )

    console.print(table)

    # 保存报告
    if output:
        _save_report(output, input_file, content, found)
        console.print(f"\n[green]✓[/green] 报告已保存: {output}")


def _check_content(content, categories):
    """检测内容中的敏感词"""
    found = {}

    for cat_name, cat_data in categories.items():
        for word in cat_data["words"]:
            # 使用正则匹配，英文部分大小写不敏感
            pattern = re.escape(word)
            # 检查是否包含英文字母，如果有则用 IGNORECASE
            has_ascii = any(c.isascii() and c.isalpha() for c in word)
            flags = re.IGNORECASE if has_ascii else 0
            matches = re.findall(pattern, content, flags)
            count = len(matches)

            if count > 0:
                if cat_name not in found:
                    found[cat_name] = []

                # 获取上下文（使用正则查找以支持大小写不敏感）
                match = re.search(pattern, content, flags)
                idx = match.start() if match else content.lower().find(word.lower())
                start = max(0, idx - 15)
                end = min(len(content), idx + len(word) + 15)
                context = content[start:end].replace("\n", " ").strip()
                if start > 0:
                    context = "..." + context
                if end < len(content):
                    context = context + "..."

                found[cat_name].append({
                    "word": word,
                    "count": count,
                    "context": context,
                    "suggestion": _get_suggestion(word),
                })

    return found


# 替换建议
SUGGESTIONS = {
    "最好": "很棒",
    "最佳": "优质",
    "第一": "领先",
    "绝对": "相当",
    "100%": "高比例",
    "免费领": "限时福利",
    "震惊": "值得关注",
    "保证": "尽力",
    "治愈": "改善",
    "稳赚": "有收益潜力",
    "加微信": "私信了解更多",
    "必看": "推荐",
    "必买": "值得考虑",
    "永久": "长期",
    "万能": "多功能",
}


def _get_suggestion(word):
    """获取替换建议"""
    return SUGGESTIONS.get(word, "-")


def _save_report(output, input_file, content, found):
    """保存检测报告"""
    with open(output, "w", encoding="utf-8") as f:
        f.write("# 违禁词检测报告\n\n")
        f.write(f"**文件**: {input_file}\n")
        f.write(f"**文案长度**: {len(content)} 字符\n\n")

        for cat_name, words in found.items():
            f.write(f"\n## {cat_name}\n\n")
            for w in words:
                f.write(f"- **{w['word']}** (出现{w['count']}次)\n")
                f.write(f"  - 上下文: {w['context']}\n")
                f.write(f"  - 建议: {w['suggestion']}\n")
