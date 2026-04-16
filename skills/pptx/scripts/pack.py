#!/usr/bin/env python3
"""展開されたディレクトリから PPTX ファイルを再構築するスクリプト。"""

import argparse
import zipfile
from pathlib import Path
from xml.dom import minidom


def condense_xml(xml_text: str) -> bytes:
    """整形された XML を圧縮して返す。"""
    try:
        dom = minidom.parseString(xml_text.encode("UTF-8"))
        condensed = dom.toxml(encoding="UTF-8")
        return condensed
    except Exception:
        return xml_text.encode("UTF-8")


def pack(input_dir: str, output_path: str) -> None:
    """展開ディレクトリから PPTX を再構築する。"""
    src = Path(input_dir)
    out = Path(output_path)

    if not src.exists():
        raise FileNotFoundError(f"ディレクトリが見つかりません: {src}")

    content_types = src / "[Content_Types].xml"
    if not content_types.exists():
        raise FileNotFoundError(
            f"[Content_Types].xml が見つかりません。有効な PPTX 展開ディレクトリではありません: {src}"
        )

    xml_extensions = {".xml", ".rels"}

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        file_count = 0
        for filepath in sorted(src.rglob("*")):
            if filepath.is_file():
                arcname = str(filepath.relative_to(src))

                if filepath.suffix in xml_extensions:
                    xml_text = filepath.read_text(encoding="UTF-8")
                    data = condense_xml(xml_text)
                    zf.writestr(arcname, data)
                else:
                    zf.write(filepath, arcname)

                file_count += 1

    print(f"✅ パック完了: {out}")
    print(f"   ファイル数: {file_count}")
    print(f"   サイズ: {out.stat().st_size:,} bytes")


def main() -> None:
    """エントリポイント。"""
    parser = argparse.ArgumentParser(description="展開ディレクトリから PPTX を再構築する")
    parser.add_argument("input", help="展開ディレクトリのパス")
    parser.add_argument("output", help="出力 PPTX ファイルのパス")
    args = parser.parse_args()
    pack(args.input, args.output)


if __name__ == "__main__":
    main()
