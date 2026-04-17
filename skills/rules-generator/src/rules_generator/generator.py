"""解析結果からルールファイルのMarkdownを生成するジェネレーター。"""

from __future__ import annotations

from rules_generator.scanner import ProjectInfo


def generate_rules_md(info: ProjectInfo, format_type: str = "CLAUDE.md") -> str:
    """ProjectInfo からルールファイルの Markdown テキストを生成する。"""
    sections: list[str] = []

    sections.append(_header(info, format_type))
    sections.append(_tech_stack(info))
    sections.append(_directory_structure(info))
    sections.append(_coding_conventions(info))
    sections.append(_testing(info))
    sections.append(_error_handling(info))
    sections.append(_git_conventions())
    sections.append(_constraints(info))

    return "\n".join(s for s in sections if s)


def _header(info: ProjectInfo, format_type: str) -> str:
    """ヘッダーセクションを生成する。"""
    title = info.name or "Project"
    lines = [f"# {title}", ""]
    if format_type == "AGENTS.md":
        lines.append("<!-- このファイルは rules-generator スキルで自動生成されました -->")
        lines.append("")
    return "\n".join(lines)


def _tech_stack(info: ProjectInfo) -> str:
    """技術スタックセクションを生成する。"""
    lines = ["## 技術スタック", ""]
    if info.language:
        version = f" {info.language_version}" if info.language_version else ""
        lines.append(f"- **言語**: {info.language}{version}")
    if info.framework:
        lines.append(f"- **フレームワーク**: {info.framework}")
    if info.package_manager:
        lines.append(f"- **パッケージマネージャ**: {info.package_manager}")
    if info.linter:
        lines.append(f"- **Linter / Formatter**: {info.linter}")
    if info.test_framework:
        lines.append(f"- **テストフレームワーク**: {info.test_framework}")
    if info.additional_tools:
        lines.append(f"- **追加ツール**: {', '.join(info.additional_tools)}")
    if info.container:
        lines.append(f"- **コンテナ**: {info.container}")
    if info.ci_service:
        lines.append(f"- **CI/CD**: {info.ci_service}")
    lines.append("")
    return "\n".join(lines)


def _directory_structure(info: ProjectInfo) -> str:
    """ディレクトリ構成セクションを生成する。"""
    if not info.directories:
        return ""
    lines = ["## ディレクトリ構成", ""]
    for dir_name, role in sorted(info.directories.items()):
        lines.append(f"- `{dir_name}/` — {role}")
    lines.append("")
    return "\n".join(lines)


def _coding_conventions(info: ProjectInfo) -> str:
    """コーディング規約セクションを生成する。"""
    lines = ["## コーディング規約", ""]

    if info.linter:
        lines.append(f"- {info.linter} の設定に従うこと")

    if info.language == "Python":
        lines.append("- Docstring は日本語で記述すること")
        lines.append("- 型ヒントを必ず付けること")
        lines.append("- import は常にファイルの先頭に配置すること")
        if info.linter == "ruff":
            lines.append("- コードを書いたら必ず `uv run ruff check --fix` を実行すること")
    elif info.language in ("TypeScript", "JavaScript"):
        lines.append("- `any` 型の使用禁止 (TypeScript)")
        lines.append("- `console.log` はデバッグ完了後に必ず削除すること")

    lines.append("")
    return "\n".join(lines)


def _testing(info: ProjectInfo) -> str:
    """テストセクションを生成する。"""
    lines = ["## テスト", ""]
    if info.test_framework:
        lines.append(f"- テストフレームワーク: {info.test_framework}")
    if info.test_command:
        lines.append(f"- テスト実行: `{info.test_command}`")
    if info.lint_command:
        lines.append(f"- Lint 実行: `{info.lint_command}`")
    if info.lint_command and info.test_command:
        lines.append("- **順序: Lint → テスト** (Lint が clean になってからテストを実行)")
    lines.append("- テストはモジュール単位で正常系・異常系を実装すること")
    lines.append("")
    return "\n".join(lines)


def _error_handling(info: ProjectInfo) -> str:
    """エラーハンドリングセクションを生成する。"""
    lines = ["## エラーハンドリング", ""]
    lines.append("- 例外は適切な粒度でキャッチし、握りつぶさないこと")
    lines.append("- ログは structured logging (JSON形式) を推奨")
    if info.framework == "FastAPI":
        lines.append("- FastAPI のエラーレスポンスは統一フォーマットを使用すること")
    lines.append("")
    return "\n".join(lines)


def _git_conventions() -> str:
    """Git 規約セクションを生成する。"""
    return "\n".join([
        "## Git 規約",
        "",
        "- ブランチ: `feature/`, `fix/`, `docs/` プレフィックス",
        "- コミットメッセージ: Conventional Commits 準拠",
        "- `.env` は `.gitignore` に含め、`.env.example` を提供すること",
        "",
    ])


def _constraints(info: ProjectInfo) -> str:
    """禁止事項セクションを生成する。"""
    lines = ["## 禁止事項", ""]
    lines.append("- ハードコーディング禁止 (API キー、URL、マジックナンバー等)")
    lines.append("- テストなしでのマージ禁止")

    if info.language == "Python":
        lines.append("- `type: ignore` コメントの安易な使用禁止")
    elif info.language in ("TypeScript", "JavaScript"):
        lines.append("- `any` 型の使用禁止")
        lines.append("- `@ts-ignore` の使用禁止")

    for constraint in info.constraints:
        lines.append(f"- {constraint}")

    lines.append("")
    return "\n".join(lines)
