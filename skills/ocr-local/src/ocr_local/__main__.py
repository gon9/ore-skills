"""CLI エントリーポイント

使い方:
    uv run -m ocr_local <input_dir> -o <output.md> [--title "タイトル"] [--source URL]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from common import setup_logger

from .ocr import build_markdown, clean_japanese_ocr, find_images, run_tesseract

logger = setup_logger(__name__)


def main() -> int:
    """メイン処理"""
    parser = argparse.ArgumentParser(description="ローカル OCR で Markdown を生成する")
    parser.add_argument("input_dir", type=Path, help="スクショ画像を含むディレクトリ")
    parser.add_argument("-o", "--output", type=Path, required=True, help="出力 Markdown パス")
    parser.add_argument("--title", default="OCR 文字起こし", help="ノートタイトル")
    parser.add_argument("--source", default=None, help="frontmatter に書く出典 URL")
    parser.add_argument("--lang", default="jpn", help="Tesseract 言語 (デフォルト: jpn)")
    parser.add_argument("--psm", type=int, default=6, help="Tesseract PSM (デフォルト: 6)")
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="日本語 OCR ノイズの簡易クリーニングを無効化する",
    )
    parser.add_argument(
        "--readable",
        action="store_true",
        help="読み物版として保存する (frontmatter tag を type/transcript にする)",
    )
    args = parser.parse_args()

    if not args.input_dir.is_dir():
        sys.stderr.write(f"入力ディレクトリが見つかりません: {args.input_dir}\n")
        return 1

    images = find_images(args.input_dir)
    if not images:
        sys.stderr.write(f"画像ファイルが見つかりません: {args.input_dir}\n")
        return 1

    logger.info("OCR 開始: %d 枚の画像を処理", len(images))
    pages: list[tuple[str, str]] = []
    for idx, image in enumerate(images, start=1):
        sys.stderr.write(f"[{idx}/{len(images)}] OCR: {image.name}\n")
        text = run_tesseract(image, lang=args.lang, psm=args.psm)
        if not args.no_clean:
            text = clean_japanese_ocr(text)
        label = f"{idx:02d}. {image.stem}"
        pages.append((label, text))

    markdown = build_markdown(
        title=args.title,
        source=args.source,
        pages=pages,
        raw=not args.readable,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    sys.stderr.write(f"出力: {args.output}\n")
    logger.info("OCR 完了: %s", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
