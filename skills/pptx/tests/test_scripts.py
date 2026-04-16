"""pptx スキルのスクリプトテスト。"""

import tempfile
import zipfile
from pathlib import Path

from scripts.add_slide import find_next_slide_number
from scripts.pack import condense_xml, pack
from scripts.unpack import pretty_print_xml, unpack


def _create_minimal_pptx(path: Path) -> None:
    """テスト用の最小限の PPTX ファイルを作成する。"""
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<Types>"
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            "</Types>",
        )
        zf.writestr(
            "ppt/presentation.xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<p:presentation>"
            "<p:sldIdLst/>"
            "</p:presentation>",
        )
        zf.writestr(
            "ppt/slides/slide1.xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<p:sld><p:cSld><p:spTree/></p:cSld></p:sld>",
        )


class TestPrettyPrintXml:
    """pretty_print_xml のテスト。"""

    def test_valid_xml(self) -> None:
        """正常な XML を整形できること。"""
        raw = b"<root><child>text</child></root>"
        result = pretty_print_xml(raw)
        assert "<root>" in result
        assert "<child>" in result
        assert "text" in result

    def test_invalid_xml_returns_raw(self) -> None:
        """不正な XML はそのまま返すこと。"""
        raw = b"not xml at all"
        result = pretty_print_xml(raw)
        assert result == "not xml at all"


class TestCondenseXml:
    """condense_xml のテスト。"""

    def test_condense(self) -> None:
        """整形された XML を圧縮できること。"""
        xml_text = '<?xml version="1.0" ?>\n<root>\n  <child>text</child>\n</root>'
        result = condense_xml(xml_text)
        assert b"<root>" in result
        assert b"<child>text</child>" in result


class TestUnpackPack:
    """unpack / pack の往復テスト。"""

    def test_roundtrip(self) -> None:
        """展開→再パックで有効な ZIP が生成されること。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            pptx_path = tmp / "test.pptx"
            unpacked_dir = tmp / "unpacked"
            output_path = tmp / "output.pptx"

            _create_minimal_pptx(pptx_path)
            unpack(str(pptx_path), str(unpacked_dir))

            assert unpacked_dir.exists()
            assert (unpacked_dir / "[Content_Types].xml").exists()
            assert (unpacked_dir / "ppt" / "slides" / "slide1.xml").exists()

            pack(str(unpacked_dir), str(output_path))

            assert output_path.exists()
            assert zipfile.is_zipfile(output_path)

            with zipfile.ZipFile(output_path, "r") as zf:
                names = zf.namelist()
                assert "[Content_Types].xml" in names
                assert "ppt/slides/slide1.xml" in names


class TestFindNextSlideNumber:
    """find_next_slide_number のテスト。"""

    def test_with_existing_slides(self) -> None:
        """既存スライドがある場合、次の番号を返すこと。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            slides_dir = Path(tmpdir)
            (slides_dir / "slide1.xml").touch()
            (slides_dir / "slide2.xml").touch()
            (slides_dir / "slide3.xml").touch()

            expected_next = 4
            assert find_next_slide_number(slides_dir) == expected_next

    def test_empty_directory(self) -> None:
        """スライドがない場合、1 を返すこと。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            slides_dir = Path(tmpdir)
            assert find_next_slide_number(slides_dir) == 1
