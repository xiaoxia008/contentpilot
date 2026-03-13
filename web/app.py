"""ContentPilot Web UI - v0.3 优化版

改进:
- 加载状态提示
- 错误处理
- 历史记录
- 一键复制
- API Key 持久化
"""

import os
import sys
import json
from datetime import datetime

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contentpilot.utils.ai import call_ai
from contentpilot.utils.config import get_api_config

# ===== 页面配置 =====
st.set_page_config(
    page_title="ContentPilot - AI内容创作助手",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===== 自定义CSS =====
st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: bold; color: #1E88E5; text-align: center; margin-bottom: 0.5rem; }
    .sub-header { font-size: 0.9rem; color: #666; text-align: center; margin-bottom: 1.5rem; }
    .result-box { background: #f0f7ff; padding: 1rem; border-radius: 8px; border-left: 4px solid #1E88E5; margin: 0.5rem 0; }
    .success-box { background: #e8f5e9; padding: 1rem; border-radius: 8px; border-left: 4px solid #4CAF50; margin: 0.5rem 0; }
    .warning-box { background: #fff8e1; padding: 1rem; border-radius: 8px; border-left: 4px solid #FFC107; margin: 0.5rem 0; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 16px; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ===== 历史记录 =====
HISTORY_FILE = os.path.expanduser("~/.contentpilot/web_history.json")

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(entry):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    history = load_history()
    history.append(entry)
    # Keep last 50 entries
    history = history[-50:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ===== 侧边栏 =====
with st.sidebar:
    st.markdown("### 🚀 ContentPilot")
    st.caption("v0.3.0 | AI内容创作助手")
    st.markdown("---")

    # API 配置
    st.subheader("⚙️ 配置")
    api_key = st.text_input("API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
    base_url = st.text_input("API URL", value=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    model = st.selectbox("模型", [
        "gpt-4o-mini", "gpt-4o",
        "stepfun/step-3.5-flash:free",
        "deepseek/deepseek-chat",
        "qwen/qwen3-coder:free",
    ])

    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_BASE_URL"] = base_url
        st.success("✅ 已配置")
    else:
        st.warning("⚠️ 请配置 API Key")

    st.markdown("---")

    # 历史记录
    st.subheader("📜 最近记录")
    history = load_history()
    if history:
        for h in reversed(history[-5:]):
            st.caption(f"• {h['time']} | {h['action']} | {h['topic'][:15]}...")
    else:
        st.caption("暂无记录")

    st.markdown("---")
    st.caption("🔒 数据本地处理")
    st.caption("🌐 github.com/xiaoxia008/contentpilot")


def ai_call(prompt, system=None):
    """统一AI调用，带错误处理"""
    if not api_key:
        st.error("请先在左侧配置 API Key")
        return None
    try:
        with st.spinner("🤔 AI思考中..."):
            result = call_ai(prompt, api_key, base_url, model, system)
            if not result:
                st.error("AI 返回为空，请检查 API Key 和模型配置")
            return result
    except Exception as e:
        st.error(f"调用失败: {str(e)[:100]}")
        return None


def show_result(content, title="结果"):
    """显示结果，带复制按钮"""
    st.markdown(f'<div class="result-box">{content}</div>', unsafe_allow_html=True)
    st.code(content, language=None)


# ===== 主界面 =====
st.markdown('<div class="main-header">🚀 ContentPilot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI内容创作助手 — 找选题、写内容、优化发布</div>', unsafe_allow_html=True)

# Tab
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🎯 爆款选题", "✏️ 初稿生成", "📌 标题优化",
    "💡 灵感衍生", "📊 竞品分析", "📤 发布适配", "🚫 违禁词检测"
])

# ===== Tab 1: 选题 =====
with tab1:
    st.header("🎯 AI 爆款选题")
    col1, col2 = st.columns([3, 1])
    with col1:
        niche = st.text_input("📝 领域", placeholder="AI教育、减肥食谱...", key="t1")
    with col2:
        platform = st.selectbox("平台", ["小红书", "抖音", "公众号", "知乎", "微博", "B站"], key="p1")

    strategy = st.radio("策略", ["🔥热点追踪", "😤痛点挖掘", "📚常青内容", "📚系列内容"], horizontal=True, key="s1")
    count = st.slider("数量", 1, 10, 5, key="c1")

    if st.button("🚀 找选题", type="primary", disabled=not niche, key="b1"):
        strat_map = {"🔥热点追踪":"热点追踪","😤痛点挖掘":"痛点挖掘","📚常青内容":"常青内容","📚系列内容":"系列内容"}
        prompt = f"你是一位{platform}内容专家。为'{niche}'生成{count}个选题。策略:{strat_map[strategy]}。每个含角度和流量分析。用---分隔。"
        result = ai_call(prompt)
        if result:
            for i, t in enumerate([x.strip() for x in result.split("---") if x.strip()], 1):
                st.markdown(f"**💡 选题 {i}**")
                st.info(t)
            save_history({"time": datetime.now().strftime("%H:%M"), "action": "选题", "topic": niche, "result": result[:200]})

# ===== Tab 2: 初稿 =====
with tab2:
    st.header("✏️ AI 初稿生成")
    topic = st.text_input("📝 选题", placeholder="5个Python自动化技巧", key="t2")
    platform2 = st.selectbox("平台", ["小红书", "抖音", "公众号", "知乎", "微博", "B站"], key="p2")
    style = st.text_input("风格(可选)", placeholder="专业/幽默/温暖", key="s2")

    if st.button("🚀 生成", type="primary", disabled=not topic, key="b2"):
        prompt = f"你是一位{platform2}内容专家。为'{topic}'写完整帖子。风格:{style if style else '自然'}。含标题/正文/互动引导/话题标签。"
        result = ai_call(prompt)
        if result:
            show_result(result)
            st.download_button("📥 下载", result, f"draft_{platform2}.md")
            save_history({"time": datetime.now().strftime("%H:%M"), "action": "初稿", "topic": topic})

# ===== Tab 3: 标题 =====
with tab3:
    st.header("📌 AI 标题优化")
    content = st.text_area("📄 内容", height=150, key="c3")
    if st.button("🚀 优化标题", type="primary", disabled=not content, key="b3"):
        prompt = f"为以下内容生成5个高点击率标题，标注预估点击率和理由:\n{content[:500]}\n用---分隔。"
        result = ai_call(prompt)
        if result:
            for i, t in enumerate([x.strip() for x in result.split("---") if x.strip()], 1):
                st.info(f"**📌 {i}**: {t}")

# ===== Tab 4: 灵感 =====
with tab4:
    st.header("💡 灵感衍生")
    topic4 = st.text_input("📝 主题", placeholder="AI教育", key="t4")
    if st.button("🚀 找灵感", type="primary", disabled=not topic4, key="b4"):
        prompt = f"为'{topic4}'找到5个原创切入角度，每个含独特视角/目标读者/创作提示。用---分隔。"
        result = ai_call(prompt)
        if result:
            for i, a in enumerate([x.strip() for x in result.split("---") if x.strip()], 1):
                st.info(f"**🎯 角度 {i}**: {a}")

# ===== Tab 5: 竞品 =====
with tab5:
    st.header("📊 竞品分析")
    niche5 = st.text_input("🔍 领域", placeholder="减肥", key="t5")
    if st.button("🚀 分析", type="primary", disabled=not niche5, key="b5"):
        prompt = f"分析'{niche5}'领域爆款内容规律:标题公式/内容结构/情绪触发/发布时间/差异化策略。"
        result = ai_call(prompt)
        if result:
            show_result(result)

# ===== Tab 6: 发布适配 =====
with tab6:
    st.header("📤 发布适配")
    content6 = st.text_area("📄 内容", height=150, key="c6")
    col1, col2 = st.columns(2)
    with col1:
        from_p = st.selectbox("从", ["小红书", "抖音", "公众号", "知乎", "微博"], key="fp")
    with col2:
        to_p = st.selectbox("到", ["小红书", "抖音", "公众号", "知乎", "微博"], key="tp", index=1)
    if st.button("🚀 适配", type="primary", disabled=not content6, key="b6"):
        prompt = f"将以下{from_p}内容适配到{to_p}风格:\n{content6}"
        result = ai_call(prompt)
        if result:
            show_result(result)
            st.download_button("📥 下载", result, f"adapted_{to_p}.md", key="dl6")

# ===== Tab 7: 违禁词 =====
with tab7:
    st.header("🚫 违禁词检测")
    content7 = st.text_area("📄 粘贴文案", height=150, key="c7")
    strict = st.checkbox("严格模式(含广告法)", key="st7")

    if st.button("🔍 检测", type="primary", disabled=not content7, key="b7"):
        sensitive = {
            "广告法": ["最好","最佳","第一","唯一","顶级","绝对","100%","永久","万能"],
            "平台敏感词": ["加微信","私信我","VX","微信号","免费领","扫码"],
            "夸大宣传": ["震惊","保证","必买","必看","史上最强"],
            "医疗": ["治愈","根治","药到病除","无副作用","立即见效"],
            "金融": ["稳赚","保本","零风险","必涨","暴富"],
        }
        cats = sensitive.keys() if strict else ["平台敏感词","夸大宣传"]
        found = [(cat, w) for cat in cats for w in sensitive.get(cat, []) if w in content7]

        if found:
            st.warning(f"⚠️ 发现 {len(found)} 个可疑词")
            for cat, word in found:
                st.error(f"**{cat}**: {word}")
        else:
            st.success("✅ 未发现违禁词")

# 页脚
st.markdown("---")
st.caption("ContentPilot v0.3.0 | 本地处理 | [GitHub](https://github.com/xiaoxia008/contentpilot)")
