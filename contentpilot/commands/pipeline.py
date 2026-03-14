"""内容生产流水线 - 串联多个命令的完整工作流

从第一性原理: 创作者要的不是一个一个工具，是从选题到发布的完整流程
"""

import os

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from contentpilot.utils.ai import call_ai
from contentpilot.utils.config import get_api_config
from contentpilot.utils.validators import PLATFORM

console = Console()


@click.command("pipeline")
@click.argument("niche")
@click.option("-p", "--platform", default="xiaohongshu", type=PLATFORM, help="目标平台")
@click.option("-n", "--count", default=3, type=click.IntRange(1, 5), help="生成选题数(1-5)")
@click.option("--skip-check", is_flag=True, help="跳过违禁词检测")
@click.option("-o", "--output-dir", default="output", help="输出目录")
def pipeline(niche, platform, count, skip_check, output_dir):
    """内容生产流水线 - 一键从选题到可发布初稿。

    完整流程: 选题生成 → 初稿撰写 → 标题优化 → 违禁词检测

    NICHE: 领域/关键词

    \b
    示例:
        contentpilot pipeline "Python教程" -p xiaohongshu
        contentpilot pipeline "减肥食谱" -p douyin -n 5
        contentpilot pipeline "AI工具" --skip-check
    """
    api_key, base_url, model = get_api_config()
    if not api_key:
        console.print("[red]✗[/red] 请设置 OPENAI_API_KEY")
        return

    os.makedirs(output_dir, exist_ok=True)

    console.print(Panel(
        f"🎯 领域: {niche}\n"
        f"📱 平台: {platform}\n"
        f"📝 选题数: {count}\n"
        f"📁 输出: {output_dir}/",
        title="🚀 内容生产流水线",
        border_style="cyan"
    ))

    # ============ Step 1: 生成选题 ============
    console.print("\n[cyan]━━━ Step 1/4: 生成选题 ━━━[/cyan]")

    topic_prompt = f"""你是一位{platform}内容策略专家。请为"{niche}"领域生成{count}个高流量潜力的选题。

要求:
1. 结合当前热点或普遍痛点
2. 标题要有情绪钩子
3. 说明切入角度和流量潜力

输出格式:
选题: [标题]
角度: [切入角度]
流量潜力: [高/中/低]
---"""

    topics_result = call_ai(topic_prompt, api_key, base_url, model)
    if not topics_result:
        console.print("[red]✗[/red] 选题生成失败")
        return

    # 解析选题
    topics_raw = [t.strip() for t in topics_result.split("---") if t.strip() and "选题:" in t]
    topics = []
    for t in topics_raw:
        lines = t.strip().split("\n")
        title = ""
        for line in lines:
            if line.startswith("选题:"):
                title = line.replace("选题:", "").strip()
                break
        if title:
            topics.append({"title": title, "raw": t.strip()})

    if not topics:
        # fallback: 用整个输出作为一个选题
        topics = [{"title": niche, "raw": topics_result}]

    for i, topic in enumerate(topics, 1):
        console.print(f"  💡 选题 {i}: {topic['title']}")

    # 保存选题
    topics_file = os.path.join(output_dir, f"topics_{niche}.txt")
    with open(topics_file, "w", encoding="utf-8") as f:
        f.write(topics_result)

    # ============ Step 2: 生成初稿 ============
    console.print(f"\n[cyan]━━━ Step 2/4: 生成初稿 ({len(topics)}篇) ━━━[/cyan]")

    platform_style = {
        "xiaohongshu": "活泼亲切、带emoji、口语化、引发互动",
        "douyin": "简洁有力、开头有钩子",
        "bilibili": "年轻化、有梗、干货+趣味",
        "wechat": "专业深度、有观点、分章节",
        "zhihu": "理性专业、有理有据",
        "weibo": "短平快、有情绪",
        "kuaishou": "接地气、真实",
    }.get(platform, "活泼亲切")

    drafts = []
    for i, topic in enumerate(topics, 1):
        console.print(f"  ✏️ 正在撰写 [{i}/{len(topics)}]: {topic['title'][:30]}...")

        draft_prompt = f"""你是一位{platform}内容创作专家。

选题: {topic['title']}
风格: {platform_style}

请生成完整的帖子内容，包含:
1. 标题（吸引眼球）
2. 正文（分段清晰，适当emoji）
3. 结尾互动引导
4. 话题标签(3-8个)

直接输出，不要解释。"""

        draft = call_ai(draft_prompt, api_key, base_url, model)
        if draft:
            draft_file = os.path.join(output_dir, f"draft_{i}_{niche}.md")
            with open(draft_file, "w", encoding="utf-8") as f:
                f.write(f"# {topic['title']}\n\n{draft}")
            drafts.append({"title": topic["title"], "content": draft, "file": draft_file})

    console.print(f"  ✅ 完成 {len(drafts)}/{len(topics)} 篇初稿")

    # ============ Step 3: 标题优化 ============
    console.print(f"\n[cyan]━━━ Step 3/4: 标题优化 ━━━[/cyan]")

    for i, draft in enumerate(drafts, 1):
        title_prompt = f"""你是一位{platform}爆款标题专家。

请为以下内容生成3个高点击率标题备选。

内容摘要:
{draft['content'][:300]}...

要求:
1. 激发好奇心/情绪共鸣
2. 使用数字、疑问、冲突等技巧
3. 符合{platform}平台调性

输出格式:
标题: [标题]
预估: [高/中/低] - [理由]
---"""

        titles = call_ai(title_prompt, api_key, base_url, model)
        if titles:
            # 提取第一个推荐标题
            for line in titles.split("\n"):
                if line.startswith("标题:"):
                    suggested = line.replace("标题:", "").strip()
                    console.print(f"  📌 原标题: {draft['title'][:25]}")
                    console.print(f"     推荐: {suggested[:40]}")
                    break

            title_file = os.path.join(output_dir, f"title_suggestions_{i}.md")
            with open(title_file, "w", encoding="utf-8") as f:
                f.write(titles)

    # ============ Step 4: 违禁词检测 ============
    if not skip_check:
        console.print(f"\n[cyan]━━━ Step 4/4: 违禁词检测 ━━━[/cyan]")

        from contentpilot.commands.check import _check_content, SENSITIVE_WORDS

        all_clean = True
        for i, draft in enumerate(drafts, 1):
            found = _check_content(draft["content"], SENSITIVE_WORDS)
            if found:
                all_clean = False
                total = sum(len(words) for words in found.values())
                console.print(f"  ⚠️ 第{i}篇: 发现 {total} 个可疑词")
                for cat, words in found.items():
                    for w in words:
                        console.print(f"     - {cat}: 「{w['word']}」→ 建议: {w.get('suggestion', '-')}")
            else:
                console.print(f"  ✅ 第{i}篇: 通过检测")

        if all_clean:
            console.print("  🎉 全部通过违禁词检测！")
    else:
        console.print("\n[dim]⏭️ 跳过违禁词检测[/dim]")

    # ============ 汇总 ============
    console.print(f"\n[green]{'='*40}[/green]")
    console.print(f"[green]✅ 流水线完成！[/green]")
    console.print(f"  📁 输出目录: {output_dir}/")
    console.print(f"  📝 选题: {len(topics)} 个")
    console.print(f"  📄 初稿: {len(drafts)} 篇")
    console.print(f"  📌 标题: 每篇 3 个备选")

    if drafts:
        console.print(f"\n[dim]💡 下一步: 检查 {output_dir}/ 中的文件，选择最佳版本发布[/dim]")
        console.print(f"[dim]💡 发布后: contentpilot track add '标题' -p {platform}[/dim]")
