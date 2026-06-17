---
name: ocr-local
description: ローカル Tesseract OCR でスクリーンショット画像群を Markdown に文字起こしする。Playwright による自動スクショ取得も可能。社外秘ドキュメントを外部 API に出さずに処理したいときに使う。
license: MIT
compatibility: Python 3.12+, Tesseract OCR 4.x+, Playwright (optional)
---

# ocr-local

## Overview
社外秘 PDF や Web 閲覧専用ドキュメントのスクリーンショットを、外部 API を一切介さずローカルだけで Markdown に文字起こしするスキル。Playwright による Web ページの自動スクショ取得にも対応。

## Capabilities

### 自動スクショ取得 (capture)
Playwright (headless Chromium) で URL にアクセスし、ページ/スライドのスクショを自動保存する。手動スクショ不要。

- **Implementation**: `src/ocr_local/capture.py`
- 3 つのキャプチャモード: 全ページ / スクロール / CSS セレクタ指定

### ローカル OCR (ocr)
スクリーンショット画像群を入力に、自然順ソートで処理し、frontmatter 付き Markdown を生成する。

- **Implementation**: `src/ocr_local/ocr.py`

### 一気通貫パイプライン (pipeline)
URL -> スクショ取得 -> OCR -> Markdown 生成をワンコマンドで実行。

- **Reference**: See [references/ocr-usage.md](references/ocr-usage.md) for details.

## Usage

### キャプチャ + OCR を一気通貫 (推奨)

```bash
uv run -m ocr_local pipeline https://example.com/slides -o output.md --title "文字起こし" --scroll
```

### スクショだけ取得

```bash
uv run -m ocr_local capture https://example.com/slides -o ./screenshots/ --scroll
```

### 既存画像から OCR だけ実行

```bash
uv run -m ocr_local ocr ./screenshots/ -o output.md --title "文字起こし"
```

### キャプチャオプション

| オプション | 説明 | デフォルト |
|---|---|---|
| `--scroll` | スクロールしながら複数枚キャプチャ | (無効) |
| `--selector` | CSS セレクタで要素ごとにキャプチャ | (全体) |
| `--width` / `--height` | ビューポートサイズ | 1920x1080 |
| `--wait` | ページ読み込み後の待機秒数 | 2.0 |
| `--prefix` | ファイル名プレフィックス | slide |
| `--max-pages` | スクロール時の最大ページ数 | 100 |

### OCR オプション

| オプション | 説明 | デフォルト |
|---|---|---|
| `--lang` | Tesseract 言語コード。縦書きなら `jpn_vert` | `jpn` |
| `--psm` | Tesseract PSM。表が多い資料は `6` | `6` |
| `--no-clean` | 日本語ノイズクリーニングを無効化 | (有効) |
| `--readable` | frontmatter タグを `type/transcript` にする | (`type/raw`) |

## Prerequisites

- Tesseract OCR (4.x 以上) + 日本語データ
  - macOS: `brew install tesseract tesseract-lang`
  - Ubuntu: `sudo apt-get install -y tesseract-ocr tesseract-ocr-jpn tesseract-ocr-jpn-vert`
- Playwright (capture / pipeline サブコマンド使用時のみ)
  - `uv pip install 'ocr-local[capture]' && playwright install chromium`
