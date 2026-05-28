# ocr-local リファレンス: 運用ガイド

## サブコマンド一覧

| コマンド | 入力 | 出力 | 用途 |
|---|---|---|---|
| `capture` | URL | スクショ画像群 | Web ページの自動スクショ取得 |
| `ocr` | 画像ディレクトリ | Markdown | Tesseract OCR でテキスト抽出 |
| `pipeline` | URL | Markdown | capture + ocr を一気通貫 |

## pipeline ワークフロー (推奨)

手動スクショ不要。URL を渡すだけで Markdown まで自動生成する。

```bash
# 基本: スクロールキャプチャで全ページ取得 + OCR
uv run -m ocr_local pipeline \
  https://share.app.knowledgework.cloud/share/<ID> \
  -o output/文字起こし.md \
  --title "評価指標 -- 文字起こし" \
  --scroll

# CSS セレクタでスライド要素だけキャプチャ
uv run -m ocr_local pipeline \
  https://example.com/slides \
  -o output/slides.md \
  --selector ".slide-content" \
  --title "スライド文字起こし"

# スクショを残したい場合
uv run -m ocr_local pipeline \
  https://example.com \
  -o output/result.md \
  --screenshots-dir ./screenshots/ \
  --scroll
```

## capture 単体

スクショだけ取得したいとき:

```bash
# 全ページスクショ (full_page)
uv run -m ocr_local capture https://example.com -o ./screenshots/

# スクロールしながら複数枚
uv run -m ocr_local capture https://example.com -o ./screenshots/ --scroll

# 特定要素だけ
uv run -m ocr_local capture https://example.com -o ./screenshots/ --selector ".main-content"
```

## ocr 単体

既存のスクショ画像から OCR する場合:

```bash
# 原文版 (type/raw)
uv run -m ocr_local ocr ~/screenshots -o output/原文.md --title "原文"

# 読み物版 (type/transcript)
uv run -m ocr_local ocr ~/screenshots -o output/読み物版.md --readable --title "読み物版"
```

## キャプチャモードの選び方

| モード | 使いどころ |
|---|---|
| デフォルト (full_page) | 1 ページに全コンテンツが収まる場合 |
| `--scroll` | 長いページをビューポート単位で分割キャプチャ |
| `--selector` | スライドビューアなど、特定の DOM 要素ごとにキャプチャ |

## Tesseract PSM の選び方

| PSM | 用途 |
|---|---|
| `4` | 1 カラムの可変サイズテキスト |
| `6` | 均一ブロック (デフォルト、スライド向き) |
| `11` | 疎なテキスト (図中の散らばったテキスト) |

## OCR 精度のメモ

Tesseract 4 系での実測:

- 大きい見出し・本文: 9 割以上正確
- ブラウザ URL バー: ノイズとして混入 --> `--selector` でコンテンツ部分だけ切り取ると改善
- 表 / 図 / アイコン横の細字: 段組崩れあり --> 目視校正推奨
- 装飾フォント (英字ロゴ等): 誤認識多め

## セットアップ

```bash
# Tesseract (OCR エンジン)
brew install tesseract tesseract-lang        # macOS
sudo apt-get install -y tesseract-ocr tesseract-ocr-jpn  # Ubuntu

# Playwright (自動スクショ)
uv pip install 'ocr-local[capture]'
playwright install chromium
```
