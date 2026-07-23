#!/usr/bin/env python3
"""配布チャネルとPlugin bundleに基づいてスキル名を列挙する。"""

from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path

VALID_CHANNELS = {"stable", "experimental"}


def load_skill_config(path: Path) -> dict[str, dict[str, str]]:
    """カタログ設定を読み込み、スキルごとの設定を返す。"""

    if not path.exists():
        return {}
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    skills = data.get("skills", {})
    if not isinstance(skills, dict):
        raise ValueError(f"{path}: [skills] must be a table")
    return skills


def select_skills(
    skills_dir: Path,
    config: dict[str, dict[str, str]],
    channel: str,
    plugin_bundle: str | None = None,
) -> list[str]:
    """指定した配布チャネルまたはPlugin bundleのスキルを返す。"""

    selected: list[str] = []
    for skill_dir in sorted(path for path in skills_dir.iterdir() if path.is_dir()):
        if not (skill_dir / "SKILL.md").is_file():
            continue
        skill_config = config.get(skill_dir.name, {})
        skill_channel = skill_config.get("channel", "experimental")
        if skill_channel not in VALID_CHANNELS:
            raise ValueError(f"{skill_dir.name}: invalid channel: {skill_channel}")
        if channel not in ("all", skill_channel):
            continue
        if plugin_bundle is not None and skill_config.get("plugin_bundle") != plugin_bundle:
            continue
        selected.append(skill_dir.name)
    return selected


def main() -> int:
    """CLI引数を解釈してスキル名を出力する。"""

    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="List distributable skills by release channel.")
    parser.add_argument("--channel", choices=("stable", "experimental", "all"), default="stable")
    parser.add_argument("--plugin-bundle")
    parser.add_argument("--format", choices=("lines", "json"), default="lines")
    parser.add_argument("--skills-dir", type=Path, default=repo_root / "skills")
    parser.add_argument("--config", type=Path, default=repo_root / "docs" / "skill-catalog.toml")
    args = parser.parse_args()

    skills = select_skills(
        args.skills_dir,
        load_skill_config(args.config),
        args.channel,
        args.plugin_bundle,
    )
    if args.format == "json":
        print(json.dumps(skills, ensure_ascii=False))
    else:
        print("\n".join(skills))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
