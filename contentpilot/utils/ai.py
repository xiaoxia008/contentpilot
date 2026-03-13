"""AI 调用工具函数"""

import os


def call_ai(prompt, api_key=None, base_url=None, model=None, system=None):
    """调用 AI 生成内容

    Args:
        prompt: 用户提示词
        api_key: API Key (默认从环境变量读取)
        base_url: API Base URL (默认从环境变量读取)
        model: 模型名称 (默认从环境变量读取)
        system: 系统提示词

    Returns:
        生成的内容字符串，失败返回 None
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = model or os.getenv("CONTENTPILOT_MODEL", "stepfun/step-3.5-flash:free")

    if not api_key:
        return None

    try:
        import openai

        client = openai.OpenAI(api_key=api_key, base_url=base_url)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.9,
            max_tokens=2000,
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"AI 调用失败: {e}")
        return None
