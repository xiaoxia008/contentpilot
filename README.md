# ContentPilot 🚀

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

**AI内容创作全流程助手 — 从选题到发布，帮创作者持续产出好内容获取流量**

## 🎯 第一性原理

> 创作者的本质需求不是"写文案"，而是"持续产出好内容获取流量"

```
流量 = 内容质量 × 发布频率 × 平台算法匹配度
```

ContentPilot 围绕这个公式设计，覆盖内容创作全流程：

| 步骤 | 功能 | 解决的核心问题 |
|------|------|----------------|
| 1️⃣ | **AI 爆款选题** | 不知道写什么 → 找到有流量潜力的方向 |
| 2️⃣ | **AI 初稿生成** | 写不出来 → 从选题直接生成可发布初稿 |
| 3️⃣ | **AI 标题优化** | 标题没吸引力 → 生成多个高点击率标题 |
| 4️⃣ | **竞品内容分析** | 不知道为什么别人火 → 拆解爆款底层逻辑 |
| 5️⃣ | **多平台发布** | 手动适配太麻烦 → 一键转换多平台格式 |

## 📦 安装

```bash
pip install contentpilot

# 设置 API Key
export OPENAI_API_KEY=sk-...
# 可选: 使用 OpenRouter
export OPENAI_BASE_URL=https://openrouter.ai/api/v1
export CONTENTPILOT_MODEL=stepfun/step-3.5-flash:free
```

## 🚀 使用

### 1️⃣ AI 爆款选题

```bash
# 热点追踪
contentpilot topic hot "Python教程" -p xiaohongshu

# 痛点挖掘
contentpilot topic pain "减肥" --audience "上班族"

# 常青内容
contentpilot topic evergreen "理财入门"

# 系列内容
contentpilot topic series "AI工具使用" -n 5

# 趋势分析
contentpilot topic trending "健身" -p douyin
```

### 2️⃣ AI 初稿生成

```bash
# 直接生成完整帖子
contentpilot draft "5个减肥食谱推荐" -p xiaohongshu

# 先看大纲再写正文
contentpilot draft "Python入门教程" --outline

# 指定风格
contentpilot draft "理财心得" --style 专业严谨
```

### 3️⃣ AI 标题优化

```bash
contentpilot title draft.md -p xiaohongshu -n 5
```

### 4️⃣ 竞品内容分析

```bash
# 分析领域爆款规律
contentpilot analyze "减肥" -p xiaohongshu

# 分析具体竞品内容
contentpilot analyze "Python" --text "竞品内容全文"
```

### 5️⃣ 多平台发布

```bash
contentpilot publish draft.md -f xiaohongshu -t douyin
contentpilot publish draft.md -f xiaohongshu -t wechat -o output.md
```

## 💡 与 ContentForge 的区别

| 维度 | ContentForge | ContentPilot |
|------|--------------|--------------|
| 定位 | 文案生成工具 | 全流程创作助手 |
| 核心功能 | AI写文案 | 选题→初稿→优化→分析→发布 |
| 设计理念 | 做加法（堆功能） | 第一性原理（只做核心） |
| 用户价值 | 帮你写 | 帮你获取流量 |

## 🔒 合规

- ✅ 纯 AI 生成，不使用爬虫
- ✅ 不违反任何平台协议
- ✅ 本地运行，数据自主

## 📄 License

MIT
