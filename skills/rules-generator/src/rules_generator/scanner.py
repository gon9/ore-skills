"""プロジェクトの技術スタックを解析するスキャナー。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProjectInfo:
    """プロジェクト解析結果を保持するデータクラス。"""

    name: str = ""
    language: str = ""
    language_version: str = ""
    framework: str = ""
    package_manager: str = ""
    linter: str = ""
    formatter: str = ""
    test_framework: str = ""
    test_command: str = ""
    lint_command: str = ""
    container: str = ""
    ci_service: str = ""
    directories: dict[str, str] = field(default_factory=dict)
    additional_tools: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)


def scan_project(project_root: str | Path) -> ProjectInfo:
    """プロジェクトルートを解析して技術スタック情報を返す。"""
    root = Path(project_root)
    if not root.is_dir():
        raise NotADirectoryError(f"ディレクトリが見つかりません: {root}")

    info = ProjectInfo()

    _detect_python(root, info)
    _detect_node(root, info)
    _detect_go(root, info)
    _detect_rust(root, info)
    _detect_container(root, info)
    _detect_ci(root, info)
    _detect_directories(root, info)

    return info


def _detect_python(root: Path, info: ProjectInfo) -> None:
    """Python プロジェクトを検出する。"""
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        setup_py = root / "setup.py"
        setup_cfg = root / "setup.cfg"
        if not setup_py.exists() and not setup_cfg.exists():
            return

    info.language = "Python"

    if pyproject.exists():
        content = pyproject.read_text(encoding="utf-8")
        info.name = _extract_toml_value(content, "name")

        version = _extract_toml_value(content, "requires-python")
        if version:
            info.language_version = version

        if "[tool.ruff]" in content:
            info.linter = "ruff"
            info.lint_command = "uv run ruff check --fix"

        if "[tool.pytest" in content:
            info.test_framework = "pytest"
            info.test_command = "uv run pytest"

        if "[tool.mypy]" in content:
            info.additional_tools.append("mypy")

        _detect_python_framework(content, info)

    _detect_python_package_manager(root, info)


def _detect_python_framework(content: str, info: ProjectInfo) -> None:
    """Python フレームワークを検出する。"""
    frameworks = {
        "fastapi": "FastAPI",
        "django": "Django",
        "flask": "Flask",
        "streamlit": "Streamlit",
    }
    for pkg, name in frameworks.items():
        if pkg in content.lower():
            info.framework = name
            break


def _detect_python_package_manager(root: Path, info: ProjectInfo) -> None:
    """Python パッケージマネージャを検出する。"""
    if (root / "uv.lock").exists():
        info.package_manager = "uv"
    elif (root / "poetry.lock").exists():
        info.package_manager = "Poetry"
    elif (root / "Pipfile.lock").exists():
        info.package_manager = "Pipenv"
    else:
        info.package_manager = "pip"


def _detect_node(root: Path, info: ProjectInfo) -> None:
    """Node.js プロジェクトを検出する。"""
    pkg_json = root / "package.json"
    if not pkg_json.exists():
        return

    if not info.language:
        info.language = "JavaScript"

    try:
        data = json.loads(pkg_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return

    info.name = info.name or data.get("name", "")

    if (root / "tsconfig.json").exists():
        info.language = "TypeScript"

    engines = data.get("engines", {})
    if "node" in engines:
        info.language_version = engines["node"]

    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
    _detect_node_framework(deps, info)
    _detect_node_linter(root, deps, info)
    _detect_node_test(deps, data, info)
    _detect_node_package_manager(root, info)


def _detect_node_framework(deps: dict, info: ProjectInfo) -> None:
    """フレームワークを検出する。"""
    node_frameworks = {
        "next": "Next.js",
        "nuxt": "Nuxt",
        "@sveltejs/kit": "SvelteKit",
        "express": "Express",
        "react": "React",
        "vue": "Vue",
    }
    for pkg, name in node_frameworks.items():
        if pkg in deps:
            info.framework = name
            break


def _detect_node_linter(root: Path, deps: dict, info: ProjectInfo) -> None:
    """Node.js の Linter を検出する。"""
    eslint_configs = ["", ".js", ".json", ".yml"]
    if "eslint" in deps or any((root / f".eslintrc{ext}").exists() for ext in eslint_configs):
        info.linter = "ESLint"
    if (root / "biome.json").exists():
        info.linter = "Biome"


def _detect_node_test(deps: dict, data: dict, info: ProjectInfo) -> None:
    """Node.js のテストフレームワークを検出する。"""
    if "vitest" in deps:
        info.test_framework = "Vitest"
        info.test_command = "npx vitest"
    elif "jest" in deps or "jest" in data.get("jest", {}):
        info.test_framework = "Jest"
        info.test_command = "npx jest"


def _detect_node_package_manager(root: Path, info: ProjectInfo) -> None:
    """Node.js のパッケージマネージャを検出する。"""
    if (root / "pnpm-lock.yaml").exists():
        info.package_manager = "pnpm"
    elif (root / "yarn.lock").exists():
        info.package_manager = "Yarn"
    elif (root / "bun.lockb").exists():
        info.package_manager = "Bun"
    else:
        info.package_manager = info.package_manager or "npm"


def _detect_go(root: Path, info: ProjectInfo) -> None:
    """Go プロジェクトを検出する。"""
    go_mod = root / "go.mod"
    if not go_mod.exists():
        return

    info.language = "Go"
    content = go_mod.read_text(encoding="utf-8")
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("go "):
            info.language_version = stripped.split()[1]
            break

    info.test_framework = "go test"
    info.test_command = "go test ./..."
    info.lint_command = "go vet ./..."


def _detect_rust(root: Path, info: ProjectInfo) -> None:
    """Rust プロジェクトを検出する。"""
    cargo_toml = root / "Cargo.toml"
    if not cargo_toml.exists():
        return

    info.language = "Rust"
    info.package_manager = "Cargo"
    info.test_framework = "cargo test"
    info.test_command = "cargo test"
    info.lint_command = "cargo clippy"

    content = cargo_toml.read_text(encoding="utf-8")
    info.name = _extract_toml_value(content, "name")


def _detect_container(root: Path, info: ProjectInfo) -> None:
    """コンテナ設定を検出する。"""
    if (root / "docker-compose.yml").exists() or (root / "compose.yml").exists():
        info.container = "Docker Compose"
    elif (root / "Dockerfile").exists():
        info.container = "Docker"


def _detect_ci(root: Path, info: ProjectInfo) -> None:
    """CI/CD サービスを検出する。"""
    if (root / ".github" / "workflows").is_dir():
        info.ci_service = "GitHub Actions"
    elif (root / ".gitlab-ci.yml").exists():
        info.ci_service = "GitLab CI"
    elif (root / "Jenkinsfile").exists():
        info.ci_service = "Jenkins"


def _detect_directories(root: Path, info: ProjectInfo) -> None:
    """主要ディレクトリを検出する。"""
    dir_roles = {
        "src": "ソースコード",
        "lib": "ライブラリコード",
        "app": "アプリケーションコード",
        "pages": "ページコンポーネント",
        "components": "UIコンポーネント",
        "tests": "テスト",
        "test": "テスト",
        "docs": "ドキュメント",
        "scripts": "スクリプト",
        "public": "静的ファイル",
        "migrations": "DBマイグレーション",
    }
    for dir_name, role in dir_roles.items():
        if (root / dir_name).is_dir():
            info.directories[dir_name] = role


def _extract_toml_value(content: str, key: str) -> str:
    """TOML コンテンツからキーに対応する値を簡易抽出する。"""
    expected_parts = 2
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith(f"{key} ") or stripped.startswith(f"{key}="):
            parts = stripped.split("=", 1)
            if len(parts) == expected_parts:
                return parts[1].strip().strip('"').strip("'")
    return ""
