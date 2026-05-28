"""ローカル OCR モジュール

社外秘 PDF / Web 閲覧専用ドキュメントのスクリーンショット (PNG/JPG) を
ローカルの Tesseract で OCR して Markdown を生成する。

外部 API は呼ばない(社外秘要件)。Tesseract と日本語言語データ (jpn) が
インストールされていることが前提。
"""

from __future__ import annotations

import datetime
import re
import subprocess
import sys
from pathlib import Path

from common import setup_logger

logger = setup_logger(__name__)

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}


def natural_key(path: Path) -> list:
    """ファイル名の数値部分を考慮した自然順ソート用キー"""
    parts = re.split(r"(\d+)", path.stem)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def find_images(input_dir: Path) -> list[Path]:
    """指定ディレクトリ内の画像ファイルを自然順ソートで返す"""
    files = [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
    files.sort(key=natural_key)
    return files


def run_tesseract(image: Path, lang: str = "jpn", psm: int = 6) -> str:
    """Tesseract を呼び出してテキストを取得する"""
    cmd = [
        "tesseract",
        str(image),
        "-",
        "-l",
        lang,
        "--psm",
        str(psm),
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, check=True, text=True, encoding="utf-8")
    except FileNotFoundError as exc:
        logger.error("tesseract コマンドが見つかりません")
        sys.stderr.write(
            "tesseract コマンドが見つかりません。"
            "`sudo apt-get install tesseract-ocr tesseract-ocr-jpn` を実行してください。\n"
        )
        raise SystemExit(1) from exc
    except subprocess.CalledProcessError as exc:
        logger.error("Tesseract 実行に失敗: %s", image)
        sys.stderr.write(f"Tesseract 実行に失敗: {image}\n{exc.stderr}\n")
        return ""
    return out.stdout


def clean_japanese_ocr(text: str) -> str:
    """日本語 OCR でありがちなノイズを軽く整理する"""
    text = re.sub(r"(?<=[\u3040-\u30ff\u4e00-\u9fff])[ \t]+(?=[\u3040-\u30ff\u4e00-\u9fff])", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def build_markdown(
    title: str,
    source: str | None,
    pages: list[tuple[str, str]],
    raw: bool,
) -> str:
    """OCR 結果から frontmatter 付き Markdown を組み立てる"""
    today = datetime.date.today().isoformat()
    note_type = "type/raw" if raw else "type/transcript"
    lines: list[str] = []
    lines.append("---")
    lines.append(f"creation_date: {today}")
    lines.append("tags:")
    lines.append(f"  - {note_type}")
    lines.append("  - status/inprogress")
    if source:
        lines.append(f"source: {source}")
    lines.append(f'title: "{title}"')
    lines.append("---")
    lines.append("")
    lines.append(f"# {title}")
    lines.append("")
    if raw:
        lines.append("> 本ファイルは Tesseract による OCR 原文。誤認識を含むため、整形版は別ファイル参照。")
    else:
        lines.append("> OCR 結果を整形した読み物版。原文は `_文字起こし原文.md` を参照。")
    lines.append("")
    for page_label, text in pages:
        lines.append(f"## {page_label}")
        lines.append("")
        if text.strip():
            lines.append(text)
        else:
            lines.append("(空ページ / OCR 結果なし)")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
