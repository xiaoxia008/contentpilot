"""平台专用模板 - 像5118那样为每个平台提供专用功能"""

# 小红书专用模板
XIAOHONGSHU_TEMPLATES = {
    "种草文案": {
        "prompt": "你是一位小红书种草达人。请为{topic}写一篇种草文案。\n\n要求:\n1. 标题带emoji，吸引眼球\n2. 开头要有个人体验感（'用了XX之后...'）\n3. 列出3-5个核心卖点\n4. 加入使用场景描述\n5. 结尾自然引导收藏\n6. 适当加emoji但不过度",
    },
    "探店文案": {
        "prompt": "你是一位小红书探店博主。请写一篇关于{topic}的探店文案。\n\n要求:\n1. 标题包含地点+亮点\n2. 开头描述到店第一印象\n3. 详细介绍环境/服务/产品\n4. 列出推荐指数(⭐)\n5. 给出实用信息(地址/营业时间/人均)\n6. 结尾引导互动",
    },
    "教程攻略": {
        "prompt": "你是一位小红书教程博主。请写一篇关于{topic}的教程攻略。\n\n要求:\n1. 标题突出'教程'/'攻略'关键词\n2. 开头说明能帮读者解决什么问题\n3. 步骤清晰，每步有emoji标注\n4. 加入常见问题FAQ\n5. 结尾鼓励实践并评论反馈",
    },
    "好物分享": {
        "prompt": "你是一位小红书好物分享博主。请写一篇关于{topic}的好物分享。\n\n要求:\n1. 标题突出'好物'/'推荐'\n2. 开头说明为什么需要这个产品\n3. 列出优缺点（真实感）\n4. 适合人群说明\n5. 价格参考\n6. 结尾引导收藏+关注",
    },
}

# 抖音专用模板
DOUYIN_TEMPLATES = {
    "短视频脚本": {
        "prompt": "你是一位抖音短视频编剧。请为{topic}写一个60秒短视频脚本。\n\n要求:\n1. 前3秒必须有钩子（提问/冲突/悬念）\n2. 正文节奏快，信息密度高\n3. 标注画面建议和字幕\n4. 结尾引导点赞评论\n5. 语言口语化",
    },
    "直播话术": {
        "prompt": "你是一位抖音直播运营专家。请为{topic}设计一套直播话术。\n\n要求:\n1. 开场白(30秒)\n2. 产品介绍话术\n3. 互动话术(引导评论)\n4. 促单话术\n5. 应对质疑话术",
    },
    "抖音标题": {
        "prompt": "你是一位抖音标题专家。请为{topic}生成10个抖音视频标题。\n\n要求:\n1. 15-25字\n2. 有悬念或冲突\n3. 引导完播\n4. 带1个emoji\n5. 避免标题党",
    },
}

# B站专用模板
BILIBILI_TEMPLATES = {
    "视频脚本": {
        "prompt": "你是一位B站UP主。请为{topic}写一个视频脚本。\n\n要求:\n1. 开头要有梗或hook\n2. 内容干货+趣味并重\n3. 适当加入B站用语\n4. 标注画面/BGM建议\n5. 结尾引导三连\n6. 时长建议5-10分钟",
    },
    "动态文案": {
        "prompt": "你是一位B站UP主。请为{topic}写一条B站动态。\n\n要求:\n1. 简洁有趣\n2. 可以加投票或话题\n3. 引导互动\n4. 符合B站社区氛围",
    },
}

# 汇总
PLATFORM_TEMPLATES = {
    "小红书": XIAOHONGSHU_TEMPLATES,
    "抖音": DOUYIN_TEMPLATES,
    "B站": BILIBILI_TEMPLATES,
}


def get_template(platform, template_type):
    """获取平台专用模板"""
    templates = PLATFORM_TEMPLATES.get(platform, {})
    return templates.get(template_type)


def list_templates(platform=None):
    """列出可用模板"""
    if platform:
        return PLATFORM_TEMPLATES.get(platform, {})
    return PLATFORM_TEMPLATES
