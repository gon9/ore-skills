#!/usr/bin/env python3
"""stableなcore SkillをCodex Plugin bundleへ同期する。"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import tempfile
import tomllib
from pathlib import Path

COPY_NAMES = {"SKILL.md", "LICENSE", "agents", "assets", "references", "scripts"}


def bundled_skill_names(config_path: Path) -> list[str]:
    """stableかつcore bundle対象のスキル名を返す。"""

    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    skills = data.get("skills", {})
    return sorted(
        name
        for name, config in skills.items()
        if config.get("channel") == "stable" and config.get("plugin_bundle") == "core"
    )


def copy_skill(source: Path, destination: Path) -> None:
    """Plugin実行に必要なSkill資源だけをコピーする。"""

    destination.mkdir(parents=True)
    for child in source.iterdir():
        if child.name not in COPY_NAMES:
            continue
        target = destination / child.name
        if child.is_dir():
            shutil.copytree(child, target)
        else:
            shutil.copy2(child, target)


def directories_match(left: Path, right: Path) -> bool:
    """2つのディレクトリツリーが同一か再帰的に判定する。"""

    comparison = filecmp.dircmp(left, right)
    if comparison.left_only or comparison.right_only or comparison.funny_files:
        return False
    _, mismatches, errors = filecmp.cmpfiles(left, right, comparison.common_files, shallow=False)
    if mismatches or errors:
        return False
    return all(directories_match(left / name, right / name) for name in comparison.common_dirs)


def build_bundle(repo_root: Path, destination: Path) -> None:
    """一時領域でbundleを構築してから配置先を置き換える。"""

    config_path = repo_root / "docs" / "skill-catalog.toml"
    with tempfile.TemporaryDirectory(dir=destination.parent) as temporary_dir:
        staged = Path(temporary_dir) / "skills"
        staged.mkdir()
        for name in bundled_skill_names(config_path):
            copy_skill(repo_root / "skills" / name, staged / name)
        if destination.exists():
            shutil.rmtree(destination)
        os.replace(staged, destination)


def check_bundle(repo_root: Path, destination: Path) -> bool:
    """現在のbundleが正本と一致するか判定する。"""

    with tempfile.TemporaryDirectory() as temporary_dir:
        expected = Path(temporary_dir) / "skills"
        expected.mkdir()
        for name in bundled_skill_names(repo_root / "docs" / "skill-catalog.toml"):
            copy_skill(repo_root / "skills" / name, expected / name)
        return destination.is_dir() and directories_match(expected, destination)


def main() -> int:
    """CLI引数に応じてbundleを同期または検証する。"""

    repo_root = Path(__file__).resolve().parents[1]
    destination = repo_root / "plugins" / "ore-skills-stable" / "skills"
    parser = argparse.ArgumentParser(description="Sync the stable Codex plugin skill bundle.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.check:
        if check_bundle(repo_root, destination):
            print("Stable plugin bundle is up to date.")
            return 0
        print("Stable plugin bundle is out of date. Run scripts/sync-stable-plugin.py.")
        return 1

    build_bundle(repo_root, destination)
    names = bundled_skill_names(repo_root / "docs" / "skill-catalog.toml")
    print(f"Synced {len(names)} skill(s) into {destination}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
