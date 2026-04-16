#!/usr/bin/env python3
"""PPTX ファイルからスライドのサムネイルグリッドを生成するスクリプト。"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌ Pillow が必要です: pip install Pillow")
    sys.exit(1)


def _convert_pptx_to_images(pptx: Path, tmp: Path) -> list[Path]:
    """PPTX を PDF 経由で JPEG 画像に変換する。"""
    try:
        subprocess.run(
            [
                "soffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(tmp),
                str(pptx),
            ],
            check=True,
            capture_output=True,
        )
    except FileNotFoundError:
        print("❌ LibreOffice (soffice) が見つかりません")
        print("   macOS: brew install --cask libreoffice")
        sys.exit(1)

    pdf_file = tmp / f"{pptx.stem}.pdf"
    if not pdf_file.exists():
        print("❌ PDF 変換に失敗しました")
        sys.exit(1)

    try:
        subprocess.run(
            ["pdftoppm", "-jpeg", "-r", "150", str(pdf_file), str(tmp / "slide")],
            check=True,
            capture_output=True,
        )
    except FileNotFoundError:
        print("❌ pdftoppm (Poppler) が見つかりません")
        print("   macOS: brew install poppler")
        sys.exit(1)

    slide_images = sorted(tmp.glob("slide-*.jpg"))
    if not slide_images:
        print("❌ スライド画像が生成されませんでした")
        sys.exit(1)

    return slide_images


THUMB_WIDTH = 400
THUMB_HEIGHT = 225
PADDING = 10
LABEL_HEIGHT = 20


def _build_grid(slide_images: list[Path], cols: int, output_prefix: str) -> None:
    """スライド画像からグリッド画像を生成して保存する。"""
    rows = (len(slide_images) + cols - 1) // cols
    grid_width = cols * (THUMB_WIDTH + PADDING) + PADDING
    grid_height = rows * (THUMB_HEIGHT + LABEL_HEIGHT + PADDING) + PADDING

    grid = Image.new("RGB", (grid_width, grid_height), "white")
    draw = ImageDraw.Draw(grid)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    except OSError:
        font = ImageFont.load_default()

    for i, img_path in enumerate(slide_images):
        row = i // cols
        col = i % cols

        x = PADDING + col * (THUMB_WIDTH + PADDING)
        y = PADDING + row * (THUMB_HEIGHT + LABEL_HEIGHT + PADDING)

        img = Image.open(img_path)
        img = img.resize((THUMB_WIDTH, THUMB_HEIGHT), Image.LANCZOS)
        grid.paste(img, (x, y))

        label = f"slide{i + 1}.xml"
        draw.text((x, y + THUMB_HEIGHT + 2), label, fill="black", font=font)

    output_file = f"{output_prefix}.jpg"
    grid.save(output_file, quality=85)
    print(f"✅ サムネイル生成完了: {output_file}")
    print(f"   スライド数: {len(slide_images)}")
    print(f"   グリッド: {rows} 行 x {cols} 列")


def generate_thumbnails(
    pptx_path: str, output_prefix: str = "thumbnails", cols: int = 3
) -> None:
    """PPTX からサムネイルグリッドを生成する。"""
    pptx = Path(pptx_path)
    if not pptx.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {pptx}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        slide_images = _convert_pptx_to_images(pptx, tmp)
        _build_grid(slide_images, cols, output_prefix)


def main() -> None:
    """エントリポイント。"""
    parser = argparse.ArgumentParser(description="PPTX のサムネイルグリッドを生成する")
    parser.add_argument("pptx", help="入力 PPTX ファイルのパス")
    parser.add_argument("output", nargs="?", default="thumbnails", help="出力ファイル名のプレフィックス")
    parser.add_argument("--cols", type=int, default=3, help="グリッドの列数")
    args = parser.parse_args()
    generate_thumbnails(args.pptx, args.output, args.cols)


if __name__ == "__main__":
    main()
