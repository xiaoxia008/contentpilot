from setuptools import find_packages, setup

setup(
    name="contentpilot",
    version="0.1.0",
    description="AI内容创作全流程助手",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
        "rich>=12.0",
        "openai>=1.0,<1.55",
    ],
    entry_points={
        "console_scripts": [
            "contentpilot=contentpilot.cli:cli",
        ],
    },
)
