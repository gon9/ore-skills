#!/usr/bin/env python3
"""PPTX ファイルを展開し、XML を整形表示するスクリプト。"""

import argparse
import shutil
import zipfile
from pathlib import Path
from xml.dom import minidom


def pretty_print_xml(xml_bytes: bytes) -> str:
    """XML バイト列を整形して文字列に変換する。"""
    try:
        dom = minidom.parseString(xml_bytes)
        return dom.toprettyxml(indent="  ", encoding="UTF-8").decode("UTF-8")
    except Exception:
        return xml_bytes.decode("UTF-8", errors="replace")


def unpack(pptx_path: str, output_dir: str) -> None:
    """PPTX ファイルを展開する。"""
    pptx = Path(pptx_path)
    out = Path(output_dir)

    if not pptx.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {pptx}")

    if out.exists():
        shutil.rmtree(out)

    out.mkdir(parents=True)

    with zipfile.ZipFile(pptx, "r") as zf:
        zf.extractall(out)

    xml_extensions = {".xml", ".rels"}
    xml_count = 0
    for filepath in out.rglob("*"):
        if filepath.is_file() and filepath.suffix in xml_extensions:
            raw = filepath.read_bytes()
            pretty = pretty_print_xml(raw)
            filepath.write_text(pretty, encoding="UTF-8")
            xml_count += 1

    print(f"✅ 展開完了: {out}")
    print(f"   XML ファイル数: {xml_count}")

    slides_dir = out / "ppt" / "slides"
    if slides_dir.exists():
        slide_files = sorted(slides_dir.glob("slide*.xml"))
        print(f"   スライド数: {len(slide_files)}")


def main() -> None:
    """エントリポイント。"""
    parser = argparse.ArgumentParser(description="PPTX ファイルを展開する")
    parser.add_argument("pptx", help="入力 PPTX ファイルのパス")
    parser.add_argument("output", help="出力ディレクトリのパス")
    args = parser.parse_args()
    unpack(args.pptx, args.output)


if __name__ == "__main__":
    main()
