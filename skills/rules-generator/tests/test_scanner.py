"""scanner モジュールのテスト。"""

import json
import tempfile
from pathlib import Path

from rules_generator.scanner import scan_project


class TestScanPythonProject:
    """Python プロジェクトの検出テスト。"""

    def test_detects_python_with_pyproject(self) -> None:
        """pyproject.toml から Python プロジェクトを検出できること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "my-app"\nrequires-python = ">=3.12"\n'
            )
            info = scan_project(root)
            assert info.language == "Python"
            assert info.name == "my-app"
            assert info.language_version == ">=3.12"

    def test_detects_ruff_and_pytest(self) -> None:
        """ruff と pytest を検出できること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            toml_content = (
                '[project]\nname = "app"\n\n'
                '[tool.ruff]\nline-length = 120\n\n'
                '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n'
            )
            (root / "pyproject.toml").write_text(toml_content)
            info = scan_project(root)
            assert info.linter == "ruff"
            assert info.test_framework == "pytest"

    def test_detects_uv_package_manager(self) -> None:
        """uv.lock から uv を検出できること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "pyproject.toml").write_text('[project]\nname = "app"\n')
            (root / "uv.lock").write_text("")
            info = scan_project(root)
            assert info.package_manager == "uv"

    def test_detects_fastapi(self) -> None:
        """FastAPI フレームワークを検出できること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "api"\ndependencies = ["fastapi"]\n'
            )
            info = scan_project(root)
            assert info.framework == "FastAPI"


class TestScanNodeProject:
    """Node.js プロジェクトの検出テスト。"""

    def test_detects_nodejs(self) -> None:
        """package.json から Node.js を検出できること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "package.json").write_text(json.dumps({"name": "my-app"}))
            info = scan_project(root)
            assert info.language == "JavaScript"
            assert info.name == "my-app"

    def test_detects_typescript(self) -> None:
        """tsconfig.json から TypeScript を検出できること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "package.json").write_text(json.dumps({"name": "ts-app"}))
            (root / "tsconfig.json").write_text("{}")
            info = scan_project(root)
            assert info.language == "TypeScript"

    def test_detects_nextjs(self) -> None:
        """Next.js フレームワークを検出できること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pkg = {"name": "web", "dependencies": {"next": "^14.0.0", "react": "^18"}}
            (root / "package.json").write_text(json.dumps(pkg))
            info = scan_project(root)
            assert info.framework == "Next.js"

    def test_detects_pnpm(self) -> None:
        """pnpm-lock.yaml から pnpm を検出できること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "package.json").write_text(json.dumps({"name": "app"}))
            (root / "pnpm-lock.yaml").write_text("")
            info = scan_project(root)
            assert info.package_manager == "pnpm"


class TestScanGoProject:
    """Go プロジェクトの検出テスト。"""

    def test_detects_go(self) -> None:
        """go.mod から Go を検出できること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "go.mod").write_text("module example.com/app\n\ngo 1.22\n")
            info = scan_project(root)
            assert info.language == "Go"
            assert info.language_version == "1.22"
            assert info.test_command == "go test ./..."


class TestScanRustProject:
    """Rust プロジェクトの検出テスト。"""

    def test_detects_rust(self) -> None:
        """Cargo.toml から Rust を検出できること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "Cargo.toml").write_text('[package]\nname = "my-crate"\n')
            info = scan_project(root)
            assert info.language == "Rust"
            assert info.name == "my-crate"
            assert info.package_manager == "Cargo"


class TestScanInfra:
    """インフラ系の検出テスト。"""

    def test_detects_docker_compose(self) -> None:
        """docker-compose.yml を検出できること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "pyproject.toml").write_text('[project]\nname = "app"\n')
            (root / "docker-compose.yml").write_text("")
            info = scan_project(root)
            assert info.container == "Docker Compose"

    def test_detects_github_actions(self) -> None:
        """GitHub Actions を検出できること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "pyproject.toml").write_text('[project]\nname = "app"\n')
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            (workflows / "ci.yml").write_text("")
            info = scan_project(root)
            assert info.ci_service == "GitHub Actions"

    def test_detects_directories(self) -> None:
        """主要ディレクトリを検出できること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "src").mkdir()
            (root / "tests").mkdir()
            (root / "docs").mkdir()
            info = scan_project(root)
            assert "src" in info.directories
            assert "tests" in info.directories
            assert "docs" in info.directories


class TestScanEmptyProject:
    """空プロジェクトの検出テスト。"""

    def test_empty_directory(self) -> None:
        """空ディレクトリでもエラーにならないこと。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            info = scan_project(tmpdir)
            assert info.language == ""
            assert info.name == ""

    def test_invalid_path_raises(self) -> None:
        """存在しないパスで NotADirectoryError が発生すること。"""
        raised = False
        try:
            scan_project("/nonexistent/path")
        except NotADirectoryError:
            raised = True
        assert raised, "Expected NotADirectoryError"
