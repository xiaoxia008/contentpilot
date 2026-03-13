"""ContentPilot Web UI - Streamlit 界面

小白友好的可视化界面，无需命令行。

运行: streamlit run web/app.py
"""

import os
import sys

import streamlit as st

# 添加项目根目录到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contentpilot.utils.ai import call_ai
from contentpilot.utils.config import get_api_config

# 页面配置
st.set_page_config(
    page_title="ContentPilot - AI内容创作助手",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===== CSS 样式 =====
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 0.9rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .result-box {
        background: #f0f7ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1E88E5;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ===== 侧边栏配置 =====
with st.sidebar:
    st.image("https://img.shields.io/badge/ContentPilot-v0.2.0-blue", use_container_width=True)
    st.markdown("---")

    st.subheader("⚙️ API 配置")
    api_key = st.text_input(
        "API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="OpenAI API Key 或 OpenRouter Key"
    )
    base_url = st.text_input(
        "API Base URL",
        value=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        help="默认 OpenAI，可用 OpenRouter"
    )
    model = st.selectbox(
        "模型",
        [
            "gpt-4o-mini",
            "gpt-4o",
            "stepfun/step-3.5-flash:free",
            "deepseek/deepseek-chat",
            "qwen/qwen3-coder:free",
        ],
        help="选择 AI 模型"
    )

    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_BASE_URL"] = base_url
        st.success("✅ API 已配置")
    else:
        st.warning("⚠️ 请配置 API Key")

    st.markdown("---")
    st.caption("🔒 所有数据在本地处理")
    st.caption("💡 不上传任何内容到第三方")


def ai_call(prompt, system=None):
    """统一的 AI 调用"""
    if not api_key:
        st.error("请先在左侧配置 API Key")
        return None
    with st.spinner("AI 思考中..."):
        result = call_ai(prompt, api_key, base_url, model, system)
    return result


# ===== 主界面 =====
st.markdown('<div class="main-header">🚀 ContentPilot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI内容创作助手 — 找选题、写内容、优化发布</div>', unsafe_allow_html=True)

# 功能 Tab
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🎯 爆款选题", "✏️ 初稿生成", "📌 标题优化",
    "💡 灵感衍生", "📊 竞品分析", "📤 发布适配", "🚫 违禁词检测"
])

# ===== Tab 1: 爆款选题 =====
with tab1:
    st.header("🎯 AI 爆款选题")
    st.caption("找到有流量潜力的内容方向")

    col1, col2 = st.columns(2)
    with col1:
        niche = st.text_input("📝 你的领域", placeholder="例如: Python教程、减肥食谱、职场沟通")
    with col2:
        platform = st.selectbox("📱 目标平台", ["小红书", "抖音", "公众号", "知乎", "微博", "B站"])

    strategy = st.radio(
        "🎲 选题策略",
        ["🔥 热点追踪", "😤 痛点挖掘", "📚 常青内容", "📚 系列内容"],
        horizontal=True
    )
    count = st.slider("生成数量", 1, 10, 5)

    if st.button("🚀 开始找选题", type="primary", disabled=not niche):
        strategy_map = {
            "🔥 热点追踪": "热点追踪", "😤 痛点挖掘": "痛点挖掘",
            "📚 常青内容": "常青内容", "📚 系列内容": "系列内容",
        }
        prompt = f"""你是一位{platform}内容创作专家。
请为"{niche}"领域生成{count}个选题。
策略: {strategy_map[strategy]}
要求: 每个选题有角度说明和流量潜力分析。用"---"分隔。"""
        result = ai_call(prompt)
        if result:
            for i, topic in enumerate([t.strip() for t in result.split("---") if t.strip()], 1):
                st.markdown(f'<div class="result-box"><strong>💡 选题 {i}</strong><br>{topic}</div>', unsafe_allow_html=True)

# ===== Tab 2: 初稿生成 =====
with tab2:
    st.header("✏️ AI 初稿生成")
    st.caption("从选题直接生成可发布的初稿")

    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input("📝 选题/标题", placeholder="例如: 5个Python自动化办公技巧")
    with col2:
        platform2 = st.selectbox("📱 平台", ["小红书", "抖音", "公众号", "知乎", "微博", "B站"], key="p2")

    style = st.text_input("🎨 语气风格（可选）", placeholder="例如: 专业、幽默、温暖")

    if st.button("🚀 生成初稿", type="primary", disabled=not topic):
        prompt = f"""你是一位{platform2}内容创作专家。
选题: {topic}
风格: {style if style else '自然'}
请生成完整帖子，含标题、正文、互动引导、话题标签。"""
        result = ai_call(prompt)
        if result:
            st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
            st.download_button("📥 下载", result, f"draft_{platform2}.md", "text/markdown")

# ===== Tab 3: 标题优化 =====
with tab3:
    st.header("📌 AI 标题优化")
    st.caption("生成多个高点击率标题")

    content = st.text_area("📄 粘贴你的内容", height=150)
    count3 = st.slider("生成数量", 1, 10, 5, key="c3")

    if st.button("🚀 生成标题", type="primary", disabled=not content):
        prompt = f"""你是一位爆款标题专家。
请为以下内容生成{count3}个高点击率标题:
{content[:500]}
每个标题标注预估点击率(高/中/低)和理由。用"---"分隔。"""
        result = ai_call(prompt)
        if result:
            for i, t in enumerate([x.strip() for x in result.split("---") if x.strip()], 1):
                st.markdown(f'<div class="result-box"><strong>📌 标题 {i}</strong><br>{t}</div>', unsafe_allow_html=True)

# ===== Tab 4: 灵感衍生 =====
with tab4:
    st.header("💡 灵感衍生")
    st.caption("从趋势和主题创作原创内容")

    topic4 = st.text_input("📝 主题", placeholder="例如: AI教育、新能源汽车")
    count4 = st.slider("生成数量", 1, 10, 5, key="c4")

    if st.button("🚀 找灵感", type="primary", disabled=not topic4):
        prompt = f"""你是一位内容策略专家。
主题: {topic4}
请找到{count4}个不同的原创切入角度。
每个角度要有: 独特视角、目标读者、创作提示。
用"---"分隔。"""
        result = ai_call(prompt)
        if result:
            for i, angle in enumerate([a.strip() for a in result.split("---") if a.strip()], 1):
                st.markdown(f'<div class="result-box"><strong>🎯 角度 {i}</strong><br>{angle}</div>', unsafe_allow_html=True)

# ===== Tab 5: 竞品分析 =====
with tab5:
    st.header("📊 竞品分析")
    st.caption("学习爆款背后的逻辑")

    niche5 = st.text_input("🔍 分析领域", placeholder="例如: 减肥、Python教程")

    if st.button("🚀 开始分析", type="primary", disabled=not niche5):
        prompt = f"""你是一位内容策略分析师。
请分析"{niche5}"领域的爆款内容规律。
提供: 标题公式、内容结构、情绪触发点、发布时间建议、差异化策略。
输出结构化分析报告。"""
        result = ai_call(prompt)
        if result:
            st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

# ===== Tab 6: 发布适配 =====
with tab6:
    st.header("📤 多平台发布适配")
    st.caption("一键转换内容格式")

    content6 = st.text_area("📄 粘贴你的内容", height=150, key="c6")
    col1, col2 = st.columns(2)
    with col1:
        from_p = st.selectbox("📤 源平台", ["小红书", "抖音", "公众号", "知乎", "微博"], key="fp")
    with col2:
        to_p = st.selectbox("📥 目标平台", ["小红书", "抖音", "公众号", "知乎", "微博"], key="tp")

    if st.button("🚀 转换", type="primary", disabled=not content6):
        prompt = f"""你是一位多平台内容专家。
请把以下{from_p}内容适配到{to_p}平台风格。
保持核心内容不变，调整格式、语气、互动方式。

{content6}"""
        result = ai_call(prompt)
        if result:
            st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
            st.download_button("📥 下载", result, f"adapted_{to_p}.md", "text/markdown", key="dl6")

# ===== Tab 7: 违禁词检测 =====
with tab7:
    st.header("🚫 违禁词检测")
    st.caption("检查文案中的违禁词，避免被平台限流")

    content7 = st.text_area("📄 粘贴要检测的文案", height=200, key="c7")
    strict = st.checkbox("严格模式（含广告法违禁词）")

    if st.button("🔍 开始检测", type="primary", disabled=not content7):
        sensitive = {
            "广告法违禁词": ["最好", "最佳", "第一", "唯一", "顶级", "绝对", "100%", "永久", "万能"],
            "平台敏感词": ["加微信", "私信我", "VX", "微信号", "免费领", "扫码"],
            "夸大宣传": ["震惊", "保证", "必买", "必看", "史上最强"],
            "医疗违禁词": ["治愈", "根治", "药到病除", "无副作用", "立即见效"],
            "金融违禁词": ["稳赚", "保本", "零风险", "必涨", "暴富"],
        }

        found = []
        cats = sensitive.keys() if strict else ["平台敏感词", "夸大宣传"]

        for cat in cats:
            for word in sensitive.get(cat, []):
                if word in content7:
                    found.append((cat, word))

        if found:
            st.warning(f"⚠️ 发现 {len(found)} 个可疑词")
            for cat, word in found:
                st.error(f"**{cat}**: {word}")
        else:
            st.success("✅ 未发现违禁词")

# ===== 页脚 =====
st.markdown("---")
st.caption("ContentPilot v0.2.0 | 所有处理在本地完成 | [GitHub](https://github.com/xiaoxia008/contentpilot)")
