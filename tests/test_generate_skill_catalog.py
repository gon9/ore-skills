"""scripts/generate-skill-catalog.py の構成判定のテスト。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "generate_skill_catalog", Path(__file__).resolve().parents[1] / "scripts" / "generate-skill-catalog.py"
)
assert _SPEC and _SPEC.loader
gsc = importlib.util.module_from_spec(_SPEC)
sys.modules["generate_skill_catalog"] = gsc
_SPEC.loader.exec_module(gsc)


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")


def test_markdown_only(tmp_path: Path) -> None:
    _touch(tmp_path / "SKILL.md")
    assert gsc.detect_structure(tmp_path) == "markdown"


def test_counts_directories_with_files(tmp_path: Path) -> None:
    _touch(tmp_path / "pyproject.toml")
    _touch(tmp_path / "scripts" / "run.sh")
    _touch(tmp_path / "references" / "nested" / "doc.md")
    assert gsc.detect_structure(tmp_path) == "python, scripts, references"


def test_ignores_empty_and_cache_only_directories(tmp_path: Path) -> None:
    # git checkout には存在しないディレクトリ。数えるとローカルと CI で結果が変わる
    (tmp_path / "references").mkdir()
    _touch(tmp_path / "assets" / ".DS_Store")
    _touch(tmp_path / "src" / "pkg" / "__pycache__" / "mod.cpython-314.pyc")
    _touch(tmp_path / "scripts" / "run.sh")
    assert gsc.detect_structure(tmp_path) == "scripts"
