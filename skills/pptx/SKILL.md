---
name: pptx
description: "Generate PowerPoint presentations (.pptx) using Node.js and PptxGenJS. Use this skill any time a .pptx file needs to be created, read, edited, or analyzed. Triggers on keywords: deck, slides, presentation, pptx, スライド, プレゼン, 発表資料."
license: MIT
compatibility: Requires Node.js 18+ and npm. Optional: Python 3.12+ for editing existing files.
metadata:
  author: gon9a
  version: "1.0"
---

# PPTX Skill

## Quick Reference

| タスク | 方法 |
|--------|------|
| 新規作成 | [references/pptxgenjs.md](references/pptxgenjs.md) を読んで PptxGenJS で生成 |
| 既存ファイルの読み取り | `python -m markitdown presentation.pptx` |
| 既存ファイルの編集 | [references/editing.md](references/editing.md) を読んで XML 操作 |
| サムネイル確認 | `python scripts/thumbnail.py presentation.pptx` |

---

## 新規作成ワークフロー（PptxGenJS）

**詳細は [references/pptxgenjs.md](references/pptxgenjs.md) を参照。**

1. ユーザーの要望からスライド構成（アウトライン）を作成する
2. スライドごとにレイアウトを決定する（単調にしない）
3. カラーパレットとフォントを選定する
4. PptxGenJS で Node.js スクリプトを書いて実行する
5. QA を実施する（後述）

```bash
# 依存関係のインストール（初回のみ）
npm install pptxgenjs

# スクリプトの実行
node generate-slides.js
```

---

## 既存ファイルの編集ワークフロー

**詳細は [references/editing.md](references/editing.md) を参照。**

1. `markitdown` でテキスト抽出、`thumbnail.py` でレイアウト確認
2. `unpack.py` で PPTX を展開
3. XML を直接編集
4. `pack.py` で再パック
5. QA を実施

---

## デザインガイドライン

### カラーパレット選定

トピックに合ったパレットを選ぶこと。デフォルトの青は避ける。

| テーマ | Primary | Secondary | Accent |
|--------|---------|-----------|--------|
| **ダーク・エグゼクティブ** | `1E2761` (紺) | `CADCFC` (氷青) | `FFFFFF` (白) |
| **フォレスト** | `2C5F2D` (深緑) | `97BC62` (苔) | `F5F5F5` (クリーム) |
| **コーラル** | `F96167` (珊瑚) | `F9E795` (金) | `2F3C7E` (紺) |
| **テラコッタ** | `B85042` (煉瓦) | `E7E8D1` (砂) | `A7BEAE` (セージ) |
| **オーシャン** | `065A82` (深青) | `1C7293` (ティール) | `21295C` (深夜) |
| **チャコール** | `36454F` (炭) | `F2F2F2` (オフ白) | `212121` (黒) |

### レイアウトの原則

- **毎スライドにビジュアル要素を入れる** — テキストだけのスライドは退屈
- **レイアウトを変える** — 同じレイアウトの繰り返しは避ける
- **サンドイッチ構造** — タイトル・結論スライドはダーク背景、コンテンツはライト背景

### レイアウトのバリエーション

- 2カラム（左テキスト、右画像）
- アイコン + テキストの行
- 大きな数字の統計コールアウト（60-72pt）
- タイムライン・プロセスフロー
- 引用・コールアウトスライド
- 2x2 / 2x3 グリッド

### タイポグラフィ

| 要素 | サイズ |
|------|--------|
| スライドタイトル | 36-44pt bold |
| セクションヘッダー | 20-24pt bold |
| 本文 | 14-16pt |
| キャプション | 10-12pt muted |

### 避けるべきこと

- タイトル下のアクセントライン（AI生成感が出る）
- Unicode の箇条書き記号（`•`）— PptxGenJS の `bullet: true` を使う
- `#` 付きの16進数カラー — ファイル破損の原因
- 同じレイアウトの反復
- テキストのみのスライド
- コントラスト不足の要素

---

## QA（必須）

**最初のレンダリングはほぼ間違いなく問題がある。** QA はバグハントとして取り組むこと。

### コンテンツ QA

- スライド枚数がアウトラインと一致するか
- テキストの切れや溢れがないか
- データ・数字に誤りがないか

### ビジュアル QA

- 要素の重なりがないか
- フォントサイズとカラーの一貫性
- 余白（マージン 0.5" 以上）が確保されているか
- レイアウトのバリエーションがあるか

### 確認方法

```bash
# PDF に変換して画像化（LibreOffice + Poppler が必要）
soffice --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

---

## 依存関係

| パッケージ | 用途 | インストール |
|-----------|------|-------------|
| **pptxgenjs** | 新規作成 | `npm install pptxgenjs` |
| **markitdown[pptx]** | テキスト抽出 | `pip install "markitdown[pptx]"` |
| **Pillow** | サムネイル生成 | `pip install Pillow` |
| **LibreOffice** | PDF 変換 | OS のパッケージマネージャ |
| **Poppler** | PDF→画像 | `brew install poppler` (macOS) |
