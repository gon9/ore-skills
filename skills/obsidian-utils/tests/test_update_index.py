"""obsidian_utils.update_index のテスト。"""

from __future__ import annotations

from pathlib import Path

import pytest
from obsidian_utils import update_index as ui


def _vault(tmp_path: Path, index_body: str, notes: dict[str, str]) -> Path:
    target = tmp_path / "docs_obsidian/10_Notes/Personal"
    target.mkdir(parents=True)
    for name, body in notes.items():
        (target / name).write_text(body, encoding="utf-8")
    (target / "つれづれメモ.md").write_text(index_body, encoding="utf-8")
    return target / "つれづれメモ.md"


# --- カテゴリ推測 ---


@pytest.mark.parametrize(
    ("filename", "content", "expected"),
    [
        ("ADHD対策.md", "", "生産性・効率化"),
        ("pw管理.md", "", "リソース・参考情報"),
        ("todo.md", "", "タスク管理"),
        ("夢日記.md", "", "日記・記録"),
        ("サッカー観戦.md", "", "趣味・関心"),
        ("メモ.md", "チームと組織のリーダー", "マネジメント"),  # 内容のキーワード頻度で決まる
        ("メモ.md", "何もない", "未分類"),
    ],
)
def test_infer_category_from_content(filename: str, content: str, expected: str) -> None:
    assert ui.infer_category_from_content(Path(filename), content) == expected


def test_categorize_by_tags_priority() -> None:
    assert ui.categorize_by_tags(["type/book-review", "topic/productivity"]) == "生産性・効率化"
    assert ui.categorize_by_tags(["type/book-review"]) == "Book Review"
    assert ui.categorize_by_tags(["status/in-progress"]) == "Status: In Progress"
    assert ui.categorize_by_tags(["other"]) == "その他"


# --- セクションの差し込み ---


def test_merge_replaces_existing_markers() -> None:
    content = f"head\n{ui.START_MARKER}\nold\n{ui.END_MARKER}\ntail"
    assert ui.merge_index_section(content, "NEW") == "head\nNEW\ntail"


def test_merge_inserts_before_tags_line() -> None:
    assert ui.merge_index_section("# t\ntags: #x\n本文", "NEW") == "# t\nNEW\n\ntags: #x\n本文"


def test_merge_appends_when_no_marker_and_no_tags() -> None:
    assert ui.merge_index_section("本文", "NEW") == "本文\n\nNEW\n"


def test_merge_returns_none_for_corrupted_markers() -> None:
    assert ui.merge_index_section(f"{ui.END_MARKER}\n{ui.START_MARKER}\nold", "NEW") is None


# --- update_index (end to end) ---


def test_update_index_writes_categorized_links(tmp_path: Path) -> None:
    index = _vault(tmp_path, "# つれづれ\n", {"旅行記.md": "", "tagged.md": "tags: #topic/tech"})
    ui.update_index(tmp_path)
    body = index.read_text(encoding="utf-8")
    assert "### 日記・記録" in body
    assert "- [旅行記](旅行記.md)" in body
    assert "### 技術" in body
    assert body.count(ui.START_MARKER) == 1


def test_update_index_leaves_file_untouched_when_markers_corrupted(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    original = f"{ui.END_MARKER}\n{ui.START_MARKER}\nold\n"
    index = _vault(tmp_path, original, {"a.md": ""})
    ui.update_index(tmp_path)
    assert index.read_text(encoding="utf-8") == original
    assert "Markers are corrupted" in capsys.readouterr().out


def test_update_index_missing_directory(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ui.update_index(tmp_path)
    assert "not found" in capsys.readouterr().out
