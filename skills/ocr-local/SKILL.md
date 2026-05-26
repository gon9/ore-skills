---
name: ocr-local
description: ローカル Tesseract OCR でスクリーンショット画像群を Markdown に文字起こしする。社外秘ドキュメントを外部 API に出さずに処理したいときに使う。
license: MIT
compatibility: Python 3.12+, Tesseract OCR 4.x+
---

# ocr-local

## Overview
社外秘 PDF や Web 閲覧専用ドキュメントのスクリーンショットを、外部 API を一切介さずローカルの Tesseract だけで Markdown に文字起こしするスキル。

## Capabilities

### ローカル OCR
スクリーンショット画像群を入力に、自然順ソートで処理し、frontmatter 付き Markdown を生成する。

- **Implementation**: `src/ocr_local/ocr.py`
- **Reference**: See [references/ocr-usage.md](references/ocr-usage.md) for HITL workflow and CLI details.

### 日本語 OCR ノイズクリーニング
日本語テキストにありがちな文字間スペースや余分な改行を自動で整理する。

## Usage

### CLI 実行

```bash
uv run -m ocr_local <input_dir> -o <output.md> --title "タイトル" --source "URL"
```

### オプション

| オプション | 説明 | デフォルト |
|---|---|---|
| `--lang` | Tesseract 言語コード。縦書きなら `jpn_vert`、英日混在なら `jpn+eng` | `jpn` |
| `--psm` | Tesseract PSM。表が多い資料は `6`、1 ブロック資料は `4` | `6` |
| `--no-clean` | 日本語ノイズクリーニングを無効化 | (有効) |
| `--readable` | frontmatter タグを `type/transcript` にする | (`type/raw`) |

## Prerequisites

- Tesseract OCR (4.x 以上) + 日本語データ
  - macOS: `brew install tesseract tesseract-lang`
  - Ubuntu: `sudo apt-get install -y tesseract-ocr tesseract-ocr-jpn tesseract-ocr-jpn-vert`
