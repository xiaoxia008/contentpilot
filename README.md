# ContentPilot 🚀

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

**AI内容创作助手 — 帮你找到好选题、写出好内容、优化发布策略**

## 🎯 第一性原理

> 创作者的本质需求是"持续产出**原创好内容**获取流量"
> 不是复用别人的内容，而是从趋势中找到自己的独特角度

```
流量 = 原创内容质量 × 独特视角 × 持续输出
```

## ✨ 功能模块

| 模块 | 功能 | 核心价值 |
|------|------|----------|
| 🎯 **topic** | AI爆款选题 | 找到有流量潜力的方向 |
| ✏️ **draft** | AI初稿生成 | 从选题到可发布初稿 |
| 📌 **title** | AI标题优化 | 多个高点击率标题 |
| 📊 **analyze** | 竞品分析 | 学习爆款背后的逻辑 |
| 📤 **publish** | 多平台适配 | 一键转换平台格式 |
| 📦 **batch** | 批量生成 | 从选题文件批量出稿 |
| 💡 **inspire** | 灵感衍生 | 从趋势创作**原创**内容 |
| 📈 **track** | 数据追踪 | 记录表现，用数据指导 |

## 💡 核心理念

**不是"复用"，是"原创驱动"**

| ❌ 不做 | ✅ 做 |
|--------|------|
| 洗稿/搬运 | 从趋势找原创角度 |
| 复制粘贴到多平台 | 同主题不同平台的原创版本 |
| AI生成一模一样的内容 | AI激发你的独特观点 |

## 🚀 快速开始

```bash
# 1. 找选题
contentpilot topic hot "AI教育" -p xiaohongshu

# 2. 写初稿
contentpilot draft "选定的选题" -p xiaohongshu

# 3. 优化标题
contentpilot title draft.md -n 3

# 4. 灵感衍生（从一个主题找多个原创角度）
contentpilot inspire angles "AI教育" -n 5

# 5. 视频创意
contentpilot inspire video-ideas "Python教程" -p douyin

# 6. 发布适配
contentpilot publish draft.md -f xiaohongshu -t bilibili

# 7. 追踪数据
contentpilot track add "文章标题" -p xiaohongshu
contentpilot track update 1 --views 5000 --likes 200
```

## 📦 安装

```bash
pip install contentpilot

# 设置 API Key
export OPENAI_API_KEY=sk-...
```

## 🔒 合规

- ✅ 纯 AI 生成原创内容
- ✅ 不爬取、不搬运他人内容
- ✅ 本地运行，数据自主

## 📄 License

MIT

## 🧪 实际测试效果

### 选题生成示例
**输入**: `topic hot "AI教育" -p xiaohongshu`
**输出**:
- 别再"人工智障"式鸡娃了！这3个AI工具让我家娃主动学习到凌晨
- 卷王同学都在偷偷用的AI外挂！期末复习效率翻倍不是玄学
- 教育博主不敢说的真相：普通家庭如何用免费AI搭个"私教工作室"

### 违禁词检测示例
**输入**: `这款产品绝对有效，100%治愈率，加微信了解详情`
**输出**: 检测到 7 个违禁词（广告法/医疗/平台敏感词/夸大宣传）
