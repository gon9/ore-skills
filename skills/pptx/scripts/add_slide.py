#!/usr/bin/env python3
"""展開済み PPTX 内でスライドを複製するスクリプト。"""

import argparse
import re
import shutil
from pathlib import Path


def find_next_slide_number(slides_dir: Path) -> int:
    """次に使えるスライド番号を返す。"""
    existing = [
        int(m.group(1))
        for f in slides_dir.glob("slide*.xml")
        if (m := re.match(r"slide(\d+)\.xml", f.name))
    ]
    return max(existing, default=0) + 1


def duplicate_slide(unpacked_dir: str, source_slide: str) -> None:
    """スライドを複製する。"""
    src = Path(unpacked_dir)
    slides_dir = src / "ppt" / "slides"
    rels_dir = slides_dir / "_rels"

    source_path = slides_dir / source_slide
    if not source_path.exists():
        raise FileNotFoundError(f"スライドが見つかりません: {source_path}")

    next_num = find_next_slide_number(slides_dir)
    new_name = f"slide{next_num}.xml"
    new_path = slides_dir / new_name

    # スライド XML をコピー
    shutil.copy2(source_path, new_path)

    # リレーションファイルもコピー
    source_rels = rels_dir / f"{source_slide}.rels"
    if source_rels.exists():
        new_rels = rels_dir / f"{new_name}.rels"
        shutil.copy2(source_rels, new_rels)

    print(f"✅ スライドを複製しました: {source_slide} → {new_name}")
    print()
    print("次のステップ:")
    print("1. ppt/presentation.xml の <p:sldIdLst> に以下を追加:")
    print('   <p:sldId id="NEW_ID" r:id="rIdNEW"/>')
    print("2. ppt/_rels/presentation.xml.rels に以下を追加:")
    print(f'   <Relationship Id="rIdNEW" Type="...slide" Target="slides/{new_name}"/>')
    print("3. [Content_Types].xml に以下を追加:")
    print(f'   <Override PartName="/ppt/slides/{new_name}" ContentType="...slide+xml"/>')


def main() -> None:
    """エントリポイント。"""
    parser = argparse.ArgumentParser(description="展開済み PPTX 内でスライドを複製する")
    parser.add_argument("unpacked_dir", help="展開ディレクトリのパス")
    parser.add_argument("source_slide", help="複製元のスライドファイル名 (例: slide2.xml)")
    args = parser.parse_args()
    duplicate_slide(args.unpacked_dir, args.source_slide)


if __name__ == "__main__":
    main()
