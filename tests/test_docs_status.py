"""docs/ の frontmatter `status:` が規約の値に収まっているかを検証する。

規約: plugins/ore-rules/rules/project-governance.md
「状態は frontmatter の status:(draft / active / implemented / superseded / frozen)だけで持つ」
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs"
ALLOWED_STATUSES = {"draft", "active", "implemented", "superseded", "frozen"}
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
STATUS_LINE = re.compile(r"^status:\s*(.*?)\s*$", re.MULTILINE)


def read_status(text: str) -> str | None:
    """frontmatter の status 値を返す。frontmatter または status がなければ None。"""
    match = FRONTMATTER.match(text)
    if not match:
        return None
    status = STATUS_LINE.search(match.group(1))
    return status.group(1) if status else None


DOC_FILES = sorted(DOCS_DIR.rglob("*.md"))


def test_docs_exist() -> None:
    # 0 件だと下のパラメータ化テストが黙って空振りするため、明示的に検出する
    assert DOC_FILES, f"{DOCS_DIR} に Markdown が見つからない"


@pytest.mark.parametrize("path", DOC_FILES, ids=lambda p: str(p.relative_to(DOCS_DIR)))
def test_status_is_allowed(path: Path) -> None:
    status = read_status(path.read_text(encoding="utf-8"))
    if status is not None:
        allowed = sorted(ALLOWED_STATUSES)
        assert status in ALLOWED_STATUSES, f"{path.name}: status '{status}' は {allowed} のどれでもない"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("---\nstatus: frozen\n---\n\n# t", "frozen"),
        ("---\ntitle: x\nstatus:  active \n---\n", "active"),
        ("---\ntitle: x\n---\n", None),  # status なし
        ("# t\nstatus: frozen\n", None),  # frontmatter 外は無視
        ("---\nstatus: done\n---\n", "done"),  # 不正値も読み取りはする(判定は呼び出し側)
    ],
)
def test_read_status(text: str, expected: str | None) -> None:
    assert read_status(text) == expected
