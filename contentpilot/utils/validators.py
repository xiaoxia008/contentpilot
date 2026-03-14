"""输入验证工具 - 共享验证逻辑"""

import click


class PlatformType(click.ParamType):
    """平台参数验证"""
    name = "platform"
    VALID_PLATFORMS = [
        "xiaohongshu", "douyin", "bilibili", "wechat",
        "zhihu", "weibo", "kuaishou",
    ]

    def convert(self, value, param, ctx):
        if value in self.VALID_PLATFORMS:
            return value
        self.fail(
            f"'{value}' 不是支持的平台。可选: {', '.join(self.VALID_PLATFORMS)}",
            param,
            ctx,
        )


class CountType(click.IntRange):
    """数量参数验证 (1-20)"""
    name = "count"

    def __init__(self):
        super().__init__(min=1, max=20)


# 单例实例
PLATFORM = PlatformType()
COUNT = CountType()
