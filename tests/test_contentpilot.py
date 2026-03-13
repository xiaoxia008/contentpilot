"""ContentPilot 核心功能测试"""

import os
import tempfile

import pytest
from click.testing import CliRunner

from contentpilot.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestCLI:
    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "ContentPilot" in result.output

    def test_version(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0

    def test_all_commands(self, runner):
        result = runner.invoke(cli, ["--help"])
        for cmd in ["topic", "draft", "title", "analyze", "publish"]:
            assert cmd in result.output


class TestTopic:
    def test_help(self, runner):
        result = runner.invoke(cli, ["topic", "--help"])
        assert result.exit_code == 0

    def test_subcommands(self, runner):
        result = runner.invoke(cli, ["topic", "--help"])
        for cmd in ["hot", "pain", "evergreen", "series", "trending"]:
            assert cmd in result.output


class TestDraft:
    def test_help(self, runner):
        result = runner.invoke(cli, ["draft", "--help"])
        assert result.exit_code == 0

    def test_no_api_key(self, runner):
        result = runner.invoke(cli, ["draft", "测试"], env={"OPENAI_API_KEY": ""})
        # Should show error or handle gracefully
        assert result.exit_code == 0 or "API_KEY" in result.output


class TestPublish:
    def test_help(self, runner):
        result = runner.invoke(cli, ["publish", "--help"])
        assert result.exit_code == 0

    def test_convert(self, runner):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("【测试标题】\n\n这是正文内容\n\n#话题1 #话题2")
            f.flush()

            with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as out:
                result = runner.invoke(
                    cli,
                    ["publish", f.name, "-f", "xiaohongshu", "-t", "douyin", "-o", out.name],
                )
                assert result.exit_code == 0

                with open(out.name, "r") as rf:
                    content = rf.read()
                assert len(content) > 0

                os.unlink(out.name)
            os.unlink(f.name)


class TestTitle:
    def test_help(self, runner):
        result = runner.invoke(cli, ["title", "--help"])
        assert result.exit_code == 0


class TestAnalyze:
    def test_help(self, runner):
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
