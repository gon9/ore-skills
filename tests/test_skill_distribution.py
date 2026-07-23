from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def load_list_skills_module() -> ModuleType:
    """配布一覧スクリプトをテスト対象のモジュールとして読み込む。"""

    script_path = Path(__file__).resolve().parents[1] / "scripts" / "list-skills.py"
    spec = importlib.util.spec_from_file_location("ore_skills_list_skills", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_skill(skills_dir: Path, name: str) -> None:
    """テスト用の最小SKILL.mdを作成する。"""

    skill_dir = skills_dir / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(f"---\nname: {name}\ndescription: test\n---\n", encoding="utf-8")


def test_select_skills_filters_release_channels(tmp_path: Path) -> None:
    module = load_list_skills_module()
    skills_dir = tmp_path / "skills"
    create_skill(skills_dir, "alpha")
    create_skill(skills_dir, "beta")
    config = {
        "alpha": {"channel": "stable", "plugin_bundle": "core"},
        "beta": {"channel": "experimental"},
    }

    assert module.select_skills(skills_dir, config, "stable") == ["alpha"]
    assert module.select_skills(skills_dir, config, "experimental") == ["beta"]
    assert module.select_skills(skills_dir, config, "all") == ["alpha", "beta"]
    assert module.select_skills(skills_dir, config, "all", "core") == ["alpha"]


def test_unclassified_skill_defaults_to_experimental(tmp_path: Path) -> None:
    module = load_list_skills_module()
    skills_dir = tmp_path / "skills"
    create_skill(skills_dir, "unclassified")

    assert module.select_skills(skills_dir, {}, "stable") == []
    assert module.select_skills(skills_dir, {}, "experimental") == ["unclassified"]


def test_invalid_channel_is_rejected(tmp_path: Path) -> None:
    module = load_list_skills_module()
    skills_dir = tmp_path / "skills"
    create_skill(skills_dir, "broken")

    with pytest.raises(ValueError, match="invalid channel"):
        module.select_skills(skills_dir, {"broken": {"channel": "preview"}}, "all")
