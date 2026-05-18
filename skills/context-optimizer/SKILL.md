---
name: context-optimizer
description: Use this skill to compress long conversation threads into a compact checkpoint summary. Use when the session is getting long, the user says "チェックポイント作って", "これまでの内容まとめて", "context compaction", "セッションまとめて", or when important decisions and code changes risk being lost. Extracts decisions, code changes, TODOs, and learnings into a reusable Markdown document.
license: MIT
metadata:
  author: gon9a
  version: "1.0"
---

# Context Optimizer Skill

長いチャットセッションから重要情報だけを抽出し、compact な Markdown チェックポイントを生成する。

## いつ使うか

- セッションが長くなり、コンテキストウィンドウが圧迫されているとき
- 作業を別のセッション・別のエージェントに引き継ぐとき
- 「今日やったこと」を記録に残したいとき
- Windsurf の Checkpoint 機能の手動補完

## ワークフロー

### Step 1: セッションを振り返る

現在のチャット履歴全体を走査し、以下のカテゴリに該当するものを特定する:

| カテゴリ | 内容 |
|---------|------|
| **決断 (Decisions)** | アーキテクチャ選択、方針決定、却下した代替案 |
| **コード変更 (Changes)** | 作成・修正・削除したファイルと変更内容の要約 |
| **未完了タスク (TODOs)** | 「次回やること」「後で確認」として残っているもの |
| **学び・発見 (Learnings)** | バグの原因、ハマりポイント、新しく分かったこと |
| **重要なコンテキスト (Context)** | 次のエージェントが知っておくべき前提・制約 |

### Step 2: チェックポイントを生成する

以下のテンプレートに従って出力する:

```markdown
# Checkpoint — <YYYY-MM-DD HH:MM>

## 作業概要
[1-3文でセッション全体の目的と達成内容]

## 決断・方針
- **[決断内容]**: [理由・背景]
- **[却下した選択肢]**: [却下理由]

## コード変更
- `path/to/file.py`: [変更内容の要約]
- `scripts/install.sh`: [変更内容の要約]

## 未完了タスク (TODO)
- [ ] [タスク1] — [優先度・理由]
- [ ] [タスク2]

## 学び・Gotchas
- [発見したこと / ハマりポイント]

## 重要なコンテキスト
[次のエージェントが最初に読むべき前提情報]
```

### Step 3: 保存先を決める

ユーザーに保存先を確認する:

1. **Obsidian vault** — `{OBSIDIAN_VAULT_DIR}/00_Inbox/checkpoint_<date>.md` に保存
2. **プロジェクト内** — `progress.md` or `docs/checkpoint.md` に追記
3. **表示のみ** — ファイル保存せずチャットに出力

## 出力の品質基準

- **< 300 行** を目標とする（長すぎると次のコンテキストを圧迫する）
- **コードスニペットは最小限** — 変更した行や関数名を記載し、全文は入れない
- **結論だけを書く** — 議論のプロセスは省略する
- **次のエージェントが読んでも理解できる** — 固有名詞・略称は展開する

## Gotchas

- セッション内の「試行錯誤」は省略する。最終的に採用した方針だけを残す
- TODO は具体的に書く（「後で直す」ではなく「`update_index.py` の frontmatter 挿入ロジックを修正する」）
- このスキル自体のチェックポイントを作るときは再帰しない
