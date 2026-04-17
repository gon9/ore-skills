"""generator モジュールのテスト。"""

from rules_generator.generator import generate_rules_md
from rules_generator.scanner import ProjectInfo


class TestGenerateRulesMd:
    """generate_rules_md のテスト。"""

    def test_python_project(self) -> None:
        """Python プロジェクトのルールファイルを生成できること。"""
        info = ProjectInfo(
            name="my-api",
            language="Python",
            language_version=">=3.12",
            framework="FastAPI",
            package_manager="uv",
            linter="ruff",
            test_framework="pytest",
            test_command="uv run pytest",
            lint_command="uv run ruff check --fix",
            container="Docker Compose",
        )
        md = generate_rules_md(info)
        assert "# my-api" in md
        assert "Python" in md
        assert "FastAPI" in md
        assert "uv" in md
        assert "ruff" in md
        assert "pytest" in md
        assert "Docker Compose" in md
        assert "Lint → テスト" in md
        assert "ハードコーディング禁止" in md

    def test_typescript_project(self) -> None:
        """TypeScript プロジェクトのルールファイルを生成できること。"""
        info = ProjectInfo(
            name="web-app",
            language="TypeScript",
            framework="Next.js",
            package_manager="pnpm",
            linter="ESLint",
            test_framework="Vitest",
            test_command="npx vitest",
        )
        md = generate_rules_md(info)
        assert "# web-app" in md
        assert "TypeScript" in md
        assert "Next.js" in md
        assert "`any` 型の使用禁止" in md

    def test_empty_project(self) -> None:
        """空の ProjectInfo でもエラーにならないこと。"""
        info = ProjectInfo()
        md = generate_rules_md(info)
        assert "# Project" in md
        assert "## 技術スタック" in md

    def test_agents_md_format(self) -> None:
        """AGENTS.md フォーマットでコメントが含まれること。"""
        info = ProjectInfo(name="test")
        md = generate_rules_md(info, format_type="AGENTS.md")
        assert "rules-generator" in md

    def test_directories_section(self) -> None:
        """ディレクトリ構成セクションが生成されること。"""
        info = ProjectInfo(
            name="app",
            directories={"src": "ソースコード", "tests": "テスト"},
        )
        md = generate_rules_md(info)
        assert "`src/`" in md
        assert "`tests/`" in md

    def test_go_project(self) -> None:
        """Go プロジェクトのルールファイルを生成できること。"""
        info = ProjectInfo(
            name="service",
            language="Go",
            language_version="1.22",
            test_framework="go test",
            test_command="go test ./...",
            lint_command="go vet ./...",
        )
        md = generate_rules_md(info)
        assert "Go" in md
        assert "go test" in md
        assert "go vet" in md
