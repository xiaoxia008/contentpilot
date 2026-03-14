"""ContentPilot Prompt 测试工具
受 promptfoo 启发，但用 Python 轻量实现

测试 AI 调用的:
1. 输出格式稳定性 (是否返回预期结构)
2. 内容质量 (长度、相关性)
3. 错误处理 (空输入、超长输入)
"""

import json
import os
import sys
import time
from typing import Optional

# ContentPilot 根目录
sys.path.insert(0, "/root/projects/contentpilot")

from contentpilot.utils.ai import call_ai
from contentpilot.utils.config import get_api_config


class PromptTest:
    """单个 prompt 测试"""

    def __init__(self, name: str, prompt_fn, validators: list):
        self.name = name
        self.prompt_fn = prompt_fn  # 返回 (prompt, system) 的函数
        self.validators = validators  # 验证函数列表

    def run(self, api_key, base_url, model) -> dict:
        prompt, system = self.prompt_fn()
        start = time.time()
        result = call_ai(prompt, api_key, base_url, model, system)
        elapsed = time.time() - start

        test_result = {
            "name": self.name,
            "success": result is not None,
            "latency_s": round(elapsed, 2),
            "output_length": len(result) if result else 0,
            "validators": {},
        }

        if result:
            for validator in self.validators:
                vname = validator.__name__
                try:
                    passed, detail = validator(result)
                    test_result["validators"][vname] = {"passed": passed, "detail": detail}
                except Exception as e:
                    test_result["validators"][vname] = {"passed": False, "detail": str(e)}

        return test_result


# ============ 验证器 ============

def has_structure(text: str) -> tuple:
    """验证输出有基本结构 (标题/段落/分隔符)"""
    has_headers = "# " in text or "##" in text or "**" in text
    has_sections = "---" in text or "\n\n" in text
    passed = has_headers or has_sections
    return passed, f"headers={has_headers}, sections={has_sections}"


def min_length_100(text: str) -> tuple:
    """验证输出至少 100 字符"""
    length = len(text)
    return length >= 100, f"length={length}"


def max_length_5000(text: str) -> tuple:
    """验证输出不超过 5000 字符"""
    length = len(text)
    return length <= 5000, f"length={length}"


def contains_chinese(text: str) -> tuple:
    """验证输出包含中文"""
    has_cn = any('\u4e00' <= c <= '\u9fff' for c in text)
    return has_cn, f"has_chinese={has_cn}"


def has_keywords(text: str, keywords: list = None) -> tuple:
    """验证输出包含关键词"""
    if keywords is None:
        keywords = ["选题", "角度", "流量", "内容", "标题"]
    found = [kw for kw in keywords if kw in text]
    ratio = len(found) / len(keywords)
    return ratio >= 0.3, f"found={found}, ratio={ratio:.0%}"


def no_placeholder(text: str) -> tuple:
    """验证输出没有占位符"""
    placeholders = ["[在此", "[TODO", "Lorem ipsum", "..."]
    found = [p for p in placeholders if p.lower() in text.lower()]
    return len(found) == 0, f"placeholders_found={found}"


# ============ 测试用例 ============

def topic_hot_prompt():
    """测试 topic hot 选题生成"""
    prompt = """你是一位资深自媒体运营专家。请根据以下领域，结合当下热点趋势，生成3个高流量潜力的选题。

领域: Python编程
平台: 小红书

要求:
1. 每个选题要结合当前热点或普遍痛点
2. 标题要有情绪钩子，让人忍不住点
3. 说明为什么这个选题有流量潜力
4. 预估阅读量级别(高/中/低)

输出格式:
选题: [标题]
角度: [切入角度]
流量潜力: [高/中/低] - [理由]
---"""
    return prompt, None


def draft_prompt():
    """测试 draft 初稿生成"""
    prompt = """你是一位小红书内容创作专家。

选题: Python自动化办公，告别重复劳动
风格: 小红书风格: 活泼亲切、带emoji、口语化、引发互动

请生成完整的帖子内容，包含:
1. 标题（吸引眼球）
2. 正文（分段清晰，适当emoji）
3. 结尾互动引导
4. 话题标签(3-8个)

直接输出，不要解释。"""
    return prompt, None


def title_prompt():
    """测试 title 标题优化"""
    prompt = """你是一位小红书爆款标题专家。

请为以下内容生成5个高点击率标题。

内容摘要:
Python自动化办公教程，教上班族用Python处理Excel、PDF、邮件等重复工作。包含实际代码示例，30分钟上手。

要求:
1. 标题要能激发好奇心/情绪共鸣
2. 使用数字、疑问、冲突等技巧
3. 符合小红书平台调性
4. 每个标题后面标注点击率预估(高/中/低)和理由

输出格式:
标题: [标题内容]
预估: [高/中/低] - [理由]
---"""
    return prompt, None


def check_prompt():
    """测试违禁词检测 prompt (不是 AI 调用，测试规则引擎)"""
    from contentpilot.commands.check import _check_content, SENSITIVE_WORDS

    test_cases = [
        ("这个产品绝对有效，100%治愈率", True, "含违禁词"),
        ("今天天气很好", False, "无违禁词"),
        ("加VX了解详情", True, "含平台敏感词"),
        ("强烈推荐这个方法", True, "含夸大宣传"),
    ]

    results = []
    for content, should_find, desc in test_cases:
        found = _check_content(content, SENSITIVE_WORDS)
        has_findings = len(found) > 0
        passed = has_findings == should_find
        results.append(f"{'✅' if passed else '❌'} {desc}: {content[:20]}...")

    return "\n".join(results), None


# ============ 运行器 ============

def run_tests():
    """运行所有测试"""
    api_key, base_url, model = get_api_config()
    if not api_key:
        print("❌ 未设置 OPENAI_API_KEY")
        return

    print(f"🔧 API: {base_url}")
    print(f"🤖 Model: {model}")
    print("=" * 60)

    # AI 调用测试
    tests = [
        PromptTest("topic_hot", topic_hot_prompt, [
            has_structure, min_length_100, max_length_5000,
            contains_chinese, has_keywords, no_placeholder
        ]),
        PromptTest("draft", draft_prompt, [
            has_structure, min_length_100, contains_chinese, no_placeholder
        ]),
        PromptTest("title", title_prompt, [
            has_structure, min_length_100, contains_chinese, no_placeholder
        ]),
    ]

    results = []
    for test in tests:
        print(f"\n🧪 测试: {test.name}")
        result = test.run(api_key, base_url, model)
        results.append(result)

        status = "✅" if result["success"] else "❌"
        print(f"   {status} 调用: {result['latency_s']}s, 输出: {result['output_length']}字")

        if result["success"]:
            for vname, vresult in result["validators"].items():
                vstatus = "✅" if vresult["passed"] else "⚠️"
                print(f"   {vstatus} {vname}: {vresult['detail']}")

    # 规则引擎测试
    print(f"\n🧪 测试: check (规则引擎)")
    check_result, _ = check_prompt()
    print(f"   {check_result}")

    # 汇总
    print("\n" + "=" * 60)
    total = len(tests)
    passed = sum(1 for r in results if r["success"])
    print(f"📊 汇总: {passed}/{total} AI 调用通过")

    total_validators = sum(len(r["validators"]) for r in results)
    passed_validators = sum(
        sum(1 for v in r["validators"].values() if v["passed"])
        for r in results
    )
    print(f"📋 验证器: {passed_validators}/{total_validators} 通过")

    avg_latency = sum(r["latency_s"] for r in results if r["success"]) / max(passed, 1)
    print(f"⏱️ 平均延迟: {avg_latency:.1f}s")

    # 保存报告
    report_path = "/root/projects/contentpilot/reports/prompt_test_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump({"results": results, "summary": {
            "total": total, "passed": passed,
            "validators_total": total_validators,
            "validators_passed": passed_validators,
            "avg_latency": round(avg_latency, 2)
        }}, f, indent=2, ensure_ascii=False)
    print(f"\n📄 报告已保存: {report_path}")


if __name__ == "__main__":
    run_tests()
