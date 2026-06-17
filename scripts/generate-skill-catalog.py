#!/usr/bin/env python3
"""skills ディレクトリから skill catalog を生成する。"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\n(?P<frontmatter>.*?)\n---", re.DOTALL)
FIELD_RE = re.compile(r"^(?P<key>[A-Za-z0-9_-]+):(?:\s*(?P<value>.*))?$")
EXCLUDED_SKILLS = {"common"}
MIN_QUOTED_LENGTH = 2


@dataclass(frozen=True)
class SkillCatalogEntry:
    """カタログに出力するスキル情報。"""

    name: str
    path: Path
    description: str
    status: str
    origin: str
    structure: str


def unquote(value: str) -> str:
    """単純な YAML スカラーのクオートを外す。"""

    if len(value) >= MIN_QUOTED_LENGTH and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


def parse_frontmatter(path: Path) -> dict[str, str]:
    """SKILL.md の frontmatter から単純な key-value を読む。"""

    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"{path}: missing frontmatter")

    values: dict[str, str] = {}
    for line in match.group("frontmatter").splitlines():
        if not line.strip() or line.startswith("  "):
            continue
        field_match = FIELD_RE.match(line)
        if not field_match:
            continue
        key = field_match.group("key")
        value = field_match.group("value")
        if value:
            values[key] = unquote(value)
    return values


def load_catalog_config(path: Path) -> dict[str, dict[str, str]]:
    """任意のカタログ補助設定を読む。"""

    if not path.exists():
        return {}
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    skills = data.get("skills", {})
    if not isinstance(skills, dict):
        raise ValueError(f"{path}: [skills] must be a table")
    return skills


def detect_structure(skill_dir: Path) -> str:
    """スキルの構成種別を判定する。"""

    parts: list[str] = []
    if (skill_dir / "pyproject.toml").exists() or (skill_dir / "src").is_dir():
        parts.append("python")
    if (skill_dir / "scripts").is_dir():
        parts.append("scripts")
    if (skill_dir / "references").is_dir():
        parts.append("references")
    if (skill_dir / "assets").is_dir():
        parts.append("assets")
    if not parts:
        return "markdown"
    return ", ".join(parts)


def collect_entries(skills_dir: Path, config: dict[str, dict[str, str]]) -> list[SkillCatalogEntry]:
    """skills ディレクトリからカタログエントリを集める。"""

    entries: list[SkillCatalogEntry] = []
    for skill_dir in sorted(path for path in skills_dir.iterdir() if path.is_dir()):
        if skill_dir.name in EXCLUDED_SKILLS:
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        frontmatter = parse_frontmatter(skill_file)
        name = frontmatter.get("name", skill_dir.name)
        skill_config = config.get(name, {})
        entries.append(
            SkillCatalogEntry(
                name=name,
                path=skill_file,
                description=frontmatter.get("description", ""),
                status=skill_config.get("status", "実装済"),
                origin=skill_config.get("origin", "-"),
                structure=detect_structure(skill_dir),
            )
        )
    return entries


def render_catalog(entries: list[SkillCatalogEntry], repo_root: Path) -> str:
    """Markdown カタログを描画する。"""

    lines = [
        "# Skill Catalog",
        "",
        "このファイルは `scripts/generate-skill-catalog.py` で自動生成されます。"
        "手動編集せず、由来などの補助情報は `docs/skill-catalog.toml` を更新してください。",
        "",
        "## ステータス凡例",
        "",
        "- `実装済`: `skills/` に `SKILL.md` が存在し、配布対象として扱う",
        "",
        "## 現在のカタログ",
        "",
        "| スキル名 | ステータス | 由来 | 構成 | description |",
        "|---|---|---|---|---|",
    ]

    for entry in entries:
        relative_path = entry.path.relative_to(repo_root)
        description = entry.description.replace("|", "\\|")
        row = [
            f"[{entry.name}](../{relative_path})",
            entry.status,
            entry.origin,
            entry.structure,
            description,
        ]
        lines.append(f"| {' | '.join(row)} |")

    lines.extend(
        [
            "",
            "## 新規スキルの追加プロセス",
            "",
            "1. `scripts/create-skill.sh` で最小雛形を生成する",
            "2. 必要な場合だけ `--python` または `--resources=` を指定する",
            "3. `SKILL.md` を agentskills.io 仕様に従って執筆する",
            "4. `python3 scripts/validate-skills.py --strict` を実行する",
            "5. `python3 scripts/generate-skill-catalog.py` で本カタログを更新する",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    """カタログを生成してファイルに書き出す。"""

    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Generate docs/skill-catalog.md from skills/*/SKILL.md.")
    parser.add_argument("--check", action="store_true", help="Fail if the generated catalog differs from disk.")
    parser.add_argument("--skills-dir", default=repo_root / "skills", type=Path)
    parser.add_argument("--config", default=repo_root / "docs" / "skill-catalog.toml", type=Path)
    parser.add_argument("--output", default=repo_root / "docs" / "skill-catalog.md", type=Path)
    args = parser.parse_args()

    entries = collect_entries(args.skills_dir, load_catalog_config(args.config))
    rendered = render_catalog(entries, repo_root)

    if args.check:
        current = args.output.read_text(encoding="utf-8") if args.output.exists() else ""
        if current != rendered:
            print(f"{args.output} is out of date. Run scripts/generate-skill-catalog.py.", file=sys.stderr)
            return 1
        return 0

    args.output.write_text(rendered, encoding="utf-8")
    print(f"Generated {args.output} with {len(entries)} skill(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
