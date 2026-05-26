# ocr-local リファレンス: HITL ワークフローと運用ガイド

## HITL (Human-in-the-Loop) ワークフロー

| 担当 | 作業 |
|---|---|
| ヒト | 1. Web ビューアで PDF を開く |
| ヒト | 2. スライドごとにスクショを取り、ディレクトリに連番で保存 (`slide_01.png`, `slide_02.png`, ...) |
| LLM (スクリプト) | 3. `uv run -m ocr_local` を実行し OCR テキストを Markdown 化 |
| ヒト | 4. 出力 Markdown をエディタで開いて目視校正 (誤認識の修正、見出し付与) |
| ヒト | 5. 整形が完了したら別ファイル (`_読み物版.md`) として保存 |
| ヒト | 6. 社外秘判断に従い、コミット可否を決定 |

## CLI 使用例

### 原文版 (type/raw) を生成

```bash
uv run -m ocr_local \
  ~/screenshots \
  -o output/文字起こし原文.md \
  --title "評価指標 -- 文字起こし原文" \
  --source "https://example.com/source-url"
```

### 読み物版 (type/transcript) を生成

```bash
uv run -m ocr_local \
  ~/screenshots \
  -o output/読み物版.md \
  --readable \
  --title "評価指標 -- 読み物版"
```

## Tesseract PSM (Page Segmentation Mode) の選び方

| PSM | 用途 |
|---|---|
| `4` | 1 カラムの可変サイズテキスト |
| `6` | 均一ブロック (デフォルト、スライド向き) |
| `11` | 疎なテキスト (図中の散らばったテキスト) |

## OCR 精度のメモ

Tesseract 4 系での実測:

- 大きい見出し・本文: 9 割以上正確
- ブラウザ URL バー / chrome: ノイズとして混入 --> スクショ時にスライド部分のみ切り取ると良い
- 表 / 図 / アイコン横の細字: 段組崩れあり --> HITL 校正必須
- 装飾フォント (英字ロゴ等): 誤認識多め

## 精度を上げるコツ

1. PDF ビューアを画面いっぱいに拡大してから 1 スライド = 1 スクショで撮る
2. スライドの枠線でクロップする (例: macOS なら `Cmd+Shift+4` で範囲指定)
3. PSM を変えて再実行 (`--psm 4` や `--psm 11`)
4. 縦書きが多い場合は `--lang jpn_vert`
