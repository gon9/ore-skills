"""ocr-local スキルのテスト"""

from pathlib import Path

from ocr_local.ocr import build_markdown, clean_japanese_ocr, find_images, natural_key


class TestNaturalKey:
    """natural_key 関数のテスト"""

    def test_numeric_sort(self) -> None:
        paths = [Path("slide_10.png"), Path("slide_2.png"), Path("slide_1.png")]
        sorted_paths = sorted(paths, key=natural_key)
        assert [p.name for p in sorted_paths] == ["slide_1.png", "slide_2.png", "slide_10.png"]

    def test_alphabetic_sort(self) -> None:
        paths = [Path("c.png"), Path("a.png"), Path("b.png")]
        sorted_paths = sorted(paths, key=natural_key)
        assert [p.name for p in sorted_paths] == ["a.png", "b.png", "c.png"]


class TestFindImages:
    """find_images 関数のテスト"""

    def test_finds_supported_formats(self, tmp_path: Path) -> None:
        (tmp_path / "img.png").touch()
        (tmp_path / "img.jpg").touch()
        (tmp_path / "img.jpeg").touch()
        (tmp_path / "img.webp").touch()
        (tmp_path / "not_image.txt").touch()
        images = find_images(tmp_path)
        expected_count = 4
        assert len(images) == expected_count

    def test_returns_sorted(self, tmp_path: Path) -> None:
        (tmp_path / "slide_10.png").touch()
        (tmp_path / "slide_2.png").touch()
        (tmp_path / "slide_1.png").touch()
        images = find_images(tmp_path)
        assert [p.name for p in images] == ["slide_1.png", "slide_2.png", "slide_10.png"]

    def test_empty_dir(self, tmp_path: Path) -> None:
        images = find_images(tmp_path)
        assert images == []


class TestCleanJapaneseOcr:
    """clean_japanese_ocr 関数のテスト"""

    def test_removes_spaces_between_japanese(self) -> None:
        text = "日本 語の テスト"
        result = clean_japanese_ocr(text)
        assert result == "日本語のテスト"

    def test_preserves_spaces_between_ascii(self) -> None:
        text = "Hello World"
        result = clean_japanese_ocr(text)
        assert result == "Hello World"

    def test_compresses_multiple_newlines(self) -> None:
        text = "行1\n\n\n\n\n行2"
        result = clean_japanese_ocr(text)
        assert result == "行1\n\n行2"

    def test_preserves_newlines_between_japanese(self) -> None:
        """改行が日本語文字間に存在しても除去されないことを確認する回帰テスト"""
        text = "日本語の長い文章が\nここで改行されています"
        result = clean_japanese_ocr(text)
        assert "\n" in result
        assert result == "日本語の長い文章が\nここで改行されています"

    def test_strips_whitespace(self) -> None:
        text = "  テキスト  "
        result = clean_japanese_ocr(text)
        assert result == "テキスト"


class TestBuildMarkdown:
    """build_markdown 関数のテスト"""

    def test_raw_mode(self) -> None:
        result = build_markdown(
            title="テスト",
            source=None,
            pages=[("01. slide_1", "テキスト1")],
            raw=True,
        )
        assert "type/raw" in result
        assert "# テスト" in result
        assert "## 01. slide_1" in result
        assert "テキスト1" in result
        assert "OCR 原文" in result

    def test_readable_mode(self) -> None:
        result = build_markdown(
            title="テスト",
            source=None,
            pages=[("01. slide_1", "テキスト1")],
            raw=False,
        )
        assert "type/transcript" in result
        assert "整形した読み物版" in result

    def test_with_source(self) -> None:
        result = build_markdown(
            title="テスト",
            source="https://example.com",
            pages=[],
            raw=True,
        )
        assert "source: https://example.com" in result

    def test_without_source(self) -> None:
        result = build_markdown(
            title="テスト",
            source=None,
            pages=[],
            raw=True,
        )
        assert "source:" not in result

    def test_empty_page(self) -> None:
        result = build_markdown(
            title="テスト",
            source=None,
            pages=[("01. blank", "")],
            raw=True,
        )
        assert "(空ページ / OCR 結果なし)" in result

    def test_frontmatter_structure(self) -> None:
        result = build_markdown(
            title="テスト",
            source=None,
            pages=[],
            raw=True,
        )
        assert result.startswith("---\n")
        assert "creation_date:" in result
        assert "status/inprogress" in result
        assert 'title: "テスト"' in result
