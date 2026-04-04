---
name: diary
description: Interactive diary writing assistant that guides users through journal entries using interview-style questions. Supports technical research when topics require investigation. Use when the user wants to write a diary, journal entry, or daily reflection.
license: MIT
compatibility: Python 3.12+
metadata:
  author: gon9a
  version: "1.0"
---

# Diary — 日記執筆支援スキル

## Overview

ユーザーの「日記を書きたい」という意図を検出したら、このスキルの手順に従って日記の執筆を対話的にサポートする。
エージェントは**インタビュアー**として振る舞い、質問を通じてユーザー自身の言葉を引き出す。
技術的な話題が出た場合は軽い調査を行い、最終的に Obsidian フォーマットの Markdown ファイルとして保存する。

## Workflow

以下の 5 つのフェーズを順に実行する。**各フェーズ間でユーザーの応答を必ず待つこと。**

---

### Phase 1: ウォームアップ（最初の質問）

ユーザーに以下のような質問を **2〜3 問** 投げかける。一度に全部聞かず、1 問ずつ会話する。

1. 「今日はどんな一日だった？ or 何かあった？」
2. 「それについてどう感じた？」
3. 「一番印象に残っていることは？」

> 💡 質問はテンプレ通りでなくてOK。ユーザーの回答に合わせて自然にアレンジする。

---

### Phase 2: テクニカル判定 & リサーチ

ユーザーの回答を分析し、**技術的なキーワード**（ライブラリ名、フレームワーク、設計パターン、プロトコル名など）が含まれているか判定する。

**技術的な内容が含まれている場合:**

1. `search_web` でトピックを調査する（概要レベル — Wikipedia 的な説明 + 公式ドキュメントへのリンク）
2. 調査結果を簡潔にユーザーに共有する
3. 「この理解であってる？何か補足ある？」と確認する

**技術的な内容がない場合:** Phase 3 に進む。

---

### Phase 3: 深掘り質問

Phase 1 の回答を踏まえて、**2〜3 問** の深掘り質問をする。これもユーザーの回答に合わせて自然にアレンジする。

質問例:
- 「なぜそう思った？何がきっかけ？」
- 「それを通じて何か気づいたことは？」
- 「次はどうしたい？何かアクションある？」

---

### Phase 4: ドラフト生成

ここまでの会話内容をもとに日記のドラフトを生成する。

**重要なルール:**
- ユーザーの **原文の言葉をできるだけそのまま活かす**。AI が勝手に言い換えない。
- フォーマットは [references/format.md](references/format.md) に従う。
- タグは会話内容から自動推定する（`#topic/xxx` は内容に応じて付与）。
- ドラフトをユーザーに提示し、「これでOK？修正したいところある？」と確認する。
- フィードバックがあれば反映して再提示する。

---

### Phase 5: ファイル保存

ユーザーが OK したら、Obsidian Vault に保存する。

1. 保存先を決定:
   - 環境変数 `OBSIDIAN_VAULT_DIR` が設定されていれば `{OBSIDIAN_VAULT_DIR}/00_Inbox/` に保存
   - 未設定の場合、ユーザーに保存先パスを確認する
2. ファイル名: `YYYY-MM-DD_<slug>.md`（slug はタイトルからローマ字 or 英語で短く生成）
3. `write_to_file` ツールでファイルを作成する
4. 保存完了をユーザーに通知する

```bash
# ファイル名の生成ユーティリティ（必要に応じて使用）
uv run -m diary.main filename --date 2026-04-04 --title "AIエージェントの可能性"
# => 2026-04-04_ai-agent-potential.md
```

## References

- [日記フォーマット仕様](references/format.md)
