"""配置管理"""

import os


def get_api_config():
    """获取 API 配置

    Returns:
        (api_key, base_url, model) 元组
    """
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("CONTENTPILOT_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("CONTENTPILOT_MODEL", "stepfun/step-3.5-flash:free")
    return api_key, base_url, model
