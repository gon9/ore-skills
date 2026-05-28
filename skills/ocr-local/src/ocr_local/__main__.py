"""CLI エントリーポイント

使い方:
    # スクショ自動取得
    uv run -m ocr_local capture <URL> -o <output_dir> [--scroll] [--selector CSS]

    # OCR 実行
    uv run -m ocr_local ocr <input_dir> -o <output.md> [--title "タイトル"]

    # キャプチャ + OCR を一気通貫
    uv run -m ocr_local pipeline <URL> -o <output.md> [--title "タイトル"]
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from common import setup_logger

from .ocr import build_markdown, clean_japanese_ocr, find_images, run_tesseract

logger = setup_logger(__name__)


def _build_capture_opts(args: argparse.Namespace) -> object:
    """argparse の結果から CaptureOptions を構築する"""
    from .capture import CaptureOptions  # noqa: PLC0415

    return CaptureOptions(
        prefix=args.prefix,
        wait_sec=args.wait,
        viewport_width=args.width,
        viewport_height=args.height,
        selector=args.selector,
        scroll_capture=args.scroll,
        max_pages=args.max_pages,
    )


def _cmd_ocr(args: argparse.Namespace) -> int:
    """OCR サブコマンド: 画像ディレクトリ -> Markdown"""
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


def _cmd_capture(args: argparse.Namespace) -> int:
    """capture サブコマンド: URL -> スクショ画像群"""
    from .capture import capture_full_page  # noqa: PLC0415

    opts = _build_capture_opts(args)
    saved = capture_full_page(url=args.url, output_dir=args.output_dir, opts=opts)
    if not saved:
        sys.stderr.write("スクショが 0 枚でした\n")
        return 1
    return 0


def _cmd_pipeline(args: argparse.Namespace) -> int:
    """pipeline サブコマンド: URL -> スクショ -> OCR -> Markdown を一気通貫"""
    from .capture import capture_full_page  # noqa: PLC0415

    screenshots_dir = Path(args.screenshots_dir) if args.screenshots_dir else Path(tempfile.mkdtemp(prefix="ocr_"))

    sys.stderr.write(f"Step 1/2: スクショ取得 -> {screenshots_dir}\n")
    opts = _build_capture_opts(args)
    saved = capture_full_page(url=args.url, output_dir=screenshots_dir, opts=opts)
    if not saved:
        sys.stderr.write("スクショが 0 枚でした\n")
        return 1

    sys.stderr.write(f"Step 2/2: OCR 実行 ({len(saved)} 枚)\n")
    pages: list[tuple[str, str]] = []
    for idx, image in enumerate(saved, start=1):
        sys.stderr.write(f"[{idx}/{len(saved)}] OCR: {image.name}\n")
        text = run_tesseract(image, lang=args.lang, psm=args.psm)
        if not args.no_clean:
            text = clean_japanese_ocr(text)
        label = f"{idx:02d}. {image.stem}"
        pages.append((label, text))

    markdown = build_markdown(
        title=args.title,
        source=args.url,
        pages=pages,
        raw=not args.readable,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    sys.stderr.write(f"出力: {args.output}\n")
    logger.info("パイプライン完了: %s", args.output)
    return 0


def _add_ocr_options(parser: argparse.ArgumentParser) -> None:
    """OCR 関連の共通オプションを追加"""
    parser.add_argument("--title", default="OCR 文字起こし", help="ノートタイトル")
    parser.add_argument("--lang", default="jpn", help="Tesseract 言語 (デフォルト: jpn)")
    parser.add_argument("--psm", type=int, default=6, help="Tesseract PSM (デフォルト: 6)")
    parser.add_argument("--no-clean", action="store_true", help="日本語ノイズクリーニングを無効化")
    parser.add_argument("--readable", action="store_true", help="読み物版 (type/transcript) として保存")


def _add_capture_options(parser: argparse.ArgumentParser) -> None:
    """キャプチャ関連の共通オプションを追加"""
    parser.add_argument("--prefix", default="slide", help="ファイル名プレフィックス (デフォルト: slide)")
    parser.add_argument("--wait", type=float, default=2.0, help="ページ読み込み後の待機秒数 (デフォルト: 2.0)")
    parser.add_argument("--width", type=int, default=1920, help="ビューポート幅 (デフォルト: 1920)")
    parser.add_argument("--height", type=int, default=1080, help="ビューポート高 (デフォルト: 1080)")
    parser.add_argument("--selector", default=None, help="スクショ対象の CSS セレクタ")
    parser.add_argument("--scroll", action="store_true", help="スクロールしながら複数枚キャプチャ")
    parser.add_argument("--max-pages", type=int, default=100, help="スクロール時の最大ページ数 (デフォルト: 100)")


def main() -> int:
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="ローカル OCR: スクショ取得 + Tesseract OCR で Markdown 生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="サブコマンド")

    # ocr サブコマンド
    ocr_parser = subparsers.add_parser("ocr", help="画像ディレクトリから OCR -> Markdown")
    ocr_parser.add_argument("input_dir", type=Path, help="スクショ画像を含むディレクトリ")
    ocr_parser.add_argument("-o", "--output", type=Path, required=True, help="出力 Markdown パス")
    ocr_parser.add_argument("--source", default=None, help="frontmatter に書く出典 URL")
    _add_ocr_options(ocr_parser)

    # capture サブコマンド
    cap_parser = subparsers.add_parser("capture", help="URL からスクショを自動取得")
    cap_parser.add_argument("url", help="スクショ対象の URL")
    cap_parser.add_argument("-o", "--output-dir", type=Path, required=True, help="スクショ保存先ディレクトリ")
    _add_capture_options(cap_parser)

    # pipeline サブコマンド
    pipe_parser = subparsers.add_parser("pipeline", help="URL -> スクショ -> OCR -> Markdown を一気通貫")
    pipe_parser.add_argument("url", help="スクショ対象の URL")
    pipe_parser.add_argument("-o", "--output", type=Path, required=True, help="出力 Markdown パス")
    pipe_parser.add_argument("--screenshots-dir", default=None, help="スクショ保存先 (省略時は一時ディレクトリ)")
    _add_capture_options(pipe_parser)
    _add_ocr_options(pipe_parser)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    if args.command == "ocr":
        return _cmd_ocr(args)
    if args.command == "capture":
        return _cmd_capture(args)
    if args.command == "pipeline":
        return _cmd_pipeline(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
