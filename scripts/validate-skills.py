#!/usr/bin/env python3
"""SKILL.md の frontmatter を検査する。"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$|^[a-z0-9]$")
KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$")
MAX_DESCRIPTION_LENGTH = 1024
MAX_NAME_LENGTH = 64
MIN_QUOTED_LENGTH = 2


@dataclass(frozen=True)
class Finding:
    """検査で見つかった問題を表す。"""

    level: str
    path: Path
    message: str


def extract_frontmatter(path: Path) -> tuple[list[str] | None, list[Finding]]:
    """SKILL.md から YAML frontmatter の行を取り出す。"""

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None, [Finding("error", path, "missing opening frontmatter delimiter")]

    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            return lines[1:index], []

    return None, [Finding("error", path, "missing closing frontmatter delimiter")]


def is_quoted(value: str) -> bool:
    """値が単一行のクオート済みスカラーか判定する。"""

    return len(value) >= MIN_QUOTED_LENGTH and value[0] == value[-1] and value[0] in {"'", '"'}


def parse_frontmatter(path: Path, lines: list[str]) -> tuple[dict[str, str], list[Finding]]:
    """このリポジトリで使う範囲の YAML frontmatter を検査しながら読む。"""

    values: dict[str, str] = {}
    findings: list[Finding] = []
    current_mapping: str | None = None

    for line_number, line in enumerate(lines, start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        if line.startswith("  "):
            if current_mapping != "metadata":
                findings.append(Finding("error", path, f"line {line_number}: unexpected indented value"))
            continue

        current_mapping = None
        match = KEY_RE.match(line)
        if not match:
            findings.append(Finding("error", path, f"line {line_number}: invalid frontmatter line"))
            continue

        key, raw_value = match.groups()
        value = raw_value or ""
        if not value:
            current_mapping = key
            continue

        if ": " in value and not is_quoted(value):
            findings.append(Finding("error", path, f"line {line_number}: quote scalar values that contain ': '"))

        values[key] = value[1:-1] if is_quoted(value) else value

    return values, findings


def validate_skill(path: Path) -> list[Finding]:
    """単一の SKILL.md を agentskills.io 互換の観点で検査する。"""

    lines, findings = extract_frontmatter(path)
    if lines is None:
        return findings

    values, parse_findings = parse_frontmatter(path, lines)
    findings.extend(parse_findings)

    name = values.get("name")
    description = values.get("description")

    if not name:
        findings.append(Finding("error", path, "missing required field: name"))
    elif len(name) > MAX_NAME_LENGTH:
        findings.append(Finding("warn", path, "name is longer than 64 characters"))
    elif not NAME_RE.fullmatch(name) or "--" in name:
        findings.append(Finding("warn", path, "name should use lowercase letters, numbers, and hyphens only"))
    elif name != path.parent.name:
        findings.append(Finding("warn", path, f"name does not match directory name: {path.parent.name}"))

    if not description:
        findings.append(Finding("error", path, "missing required field: description"))
    elif len(description) > MAX_DESCRIPTION_LENGTH:
        findings.append(Finding("error", path, "description is longer than 1024 characters"))

    return findings


def collect_skill_files(skills_dir: Path) -> list[Path]:
    """skills ディレクトリ直下から SKILL.md を列挙する。"""

    return sorted(path / "SKILL.md" for path in skills_dir.iterdir() if (path / "SKILL.md").is_file())


def main() -> int:
    """コマンドライン引数を解釈して検査を実行する。"""

    parser = argparse.ArgumentParser(description="Validate SKILL.md frontmatter files.")
    parser.add_argument("skills_dir", nargs="?", default=Path(__file__).resolve().parents[1] / "skills")
    parser.add_argument("--strict", action="store_true", help="Treat portability warnings as failures.")
    args = parser.parse_args()

    skills_dir = Path(args.skills_dir)
    findings: list[Finding] = []
    for skill_file in collect_skill_files(skills_dir):
        findings.extend(validate_skill(skill_file))

    errors = [finding for finding in findings if finding.level == "error"]
    warnings = [finding for finding in findings if finding.level == "warn"]

    for finding in findings:
        print(f"{finding.level.upper()} {finding.path}: {finding.message}")

    checked_count = len(collect_skill_files(skills_dir))
    print(f"Checked {checked_count} skill file(s): {len(errors)} error(s), {len(warnings)} warning(s)")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
