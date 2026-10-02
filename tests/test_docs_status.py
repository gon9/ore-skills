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
STATUS_LINE = re.compile(r"^status:[ \t]*(.*?)[ \t]*$", re.MULTILINE)
QUOTED = re.compile(r"""\A(["'])(.*)\1\Z""")


def _scalar(raw: str) -> str:
    """YAML のプレーン/引用符付きスカラーを値に直す(行末コメントを除く)。"""
    value = raw.strip()
    quoted = QUOTED.match(value) or QUOTED.match(value.split(" #", 1)[0].strip())
    if quoted:
        return quoted.group(2)
    return value.split(" #", 1)[0].strip()


def read_statuses(text: str) -> list[str]:
    """frontmatter 内の status 値をすべて返す。frontmatter がなければ空リスト。"""
    match = FRONTMATTER.match(text)
    if not match:
        return []
    return [_scalar(raw) for raw in STATUS_LINE.findall(match.group(1))]


DOC_FILES = sorted(DOCS_DIR.rglob("*.md"))


def test_docs_exist() -> None:
    # 0 件だと下のパラメータ化テストが黙って空振りするため、明示的に検出する
    assert DOC_FILES, f"{DOCS_DIR} に Markdown が見つからない"


@pytest.mark.parametrize("path", DOC_FILES, ids=lambda p: str(p.relative_to(DOCS_DIR)))
def test_status_is_allowed(path: Path) -> None:
    statuses = read_statuses(path.read_text(encoding="utf-8"))
    assert len(statuses) <= 1, f"{path.name}: status が複数ある {statuses}"
    allowed = sorted(ALLOWED_STATUSES)
    for status in statuses:
        assert status in ALLOWED_STATUSES, f"{path.name}: status '{status}' は {allowed} のどれでもない"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("---\nstatus: frozen\n---\n\n# t", ["frozen"]),
        ("---\ntitle: x\nstatus:  active \n---\n", ["active"]),
        ('---\nstatus: "frozen"\n---\n', ["frozen"]),  # 引用符付き
        ("---\nstatus: 'draft'\n---\n", ["draft"]),
        ("---\nstatus: frozen  # 2026-10 凍結\n---\n", ["frozen"]),  # 行末コメント
        ('---\nstatus: "frozen" # memo\n---\n', ["frozen"]),
        ("---\nstatus: frozen\nstatus: done\n---\n", ["frozen", "done"]),  # 重複は両方返す
        ("---\ntitle: x\n---\n", []),  # status なし
        ("# t\nstatus: frozen\n", []),  # frontmatter 外は無視
    ],
)
def test_read_statuses(text: str, expected: list[str]) -> None:
    assert read_statuses(text) == expected


@pytest.mark.parametrize(
    "text",
    ["---\nstatus: done\n---\n", "---\nstatus: frozen\nstatus: done\n---\n"],
)
def test_invalid_frontmatter_is_rejected(tmp_path: Path, text: str) -> None:
    path = tmp_path / "bad.md"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(AssertionError):
        test_status_is_allowed(path)
