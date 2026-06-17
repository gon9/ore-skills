---
name: obsidian-triage
description: "Use this skill to organize, sort, or triage notes in an Obsidian vault inbox. Use when the user wants to clean up their inbox (00_Inbox), categorize notes, suggest appropriate folders or tags, or move notes to their permanent location. Triggers on keywords: Obsidian整理, 受信箱, inbox triage, ノート整理, vault整理, 00_Inbox, 積んでるノート, even if they don't explicitly mention Obsidian."
license: MIT
metadata:
  author: gon9a
  version: "1.0"
---

# Obsidian Triage Skill

Obsidian vault の `00_Inbox/` に溜まったノートを分析・整理するスキル。
`obsidian-utils`（インデックス管理）の補完として、**個別ノートの分類・移動**に特化する。

## ワークフロー

### Phase 1: Inbox を読み込む

1. `OBSIDIAN_VAULT_DIR` 環境変数からパスを取得。未設定なら確認する
2. `{vault}/00_Inbox/` のファイル一覧を取得する
3. 各ファイルの YAML frontmatter と冒頭 20 行を読み込む

### Phase 2: ノートを分析する

各ノートについて以下を判定する:

| 項目 | 確認内容 |
|------|---------|
| **トピック** | 何についてのノートか |
| **種別** | メモ / 日記 / リサーチ / プロジェクト / アイデア / リファレンス |
| **完成度** | 完成 / 草稿 / 断片 |
| **タグ** | 既存タグ or 推奨タグ |
| **移動先候補** | vault 内の適切なフォルダ |

### Phase 3: 提案をユーザーに提示する

各ノートの処理案を箇条書きで提示する:

```
📄 2026-05-10_ai-agent-notes.md
   種別: リサーチメモ
   推奨フォルダ: 03_Research/AI/
   追加タグ: #topic/ai-agent #type/research
   → 移動 or スキップ?
```

- **一括処理**: 問題ないものはまとめて確認する
- **個別確認**: 曖昧なものは 1 件ずつ判断を仰ぐ

### Phase 4: 実行する

ユーザーが確認したら:

1. frontmatter のタグを更新する（YAML の `tags:` フィールドを編集）
2. ファイルを適切なフォルダへ移動する（ファイル操作ツールを使用）
3. 処理結果をサマリーとして提示する

## フォルダ構成の参考（一般的な Obsidian 構成）

```
vault/
├── 00_Inbox/        ← 整理対象
├── 01_Projects/     ← 進行中のプロジェクト
├── 02_Areas/        ← 継続的な関心領域
├── 03_Resources/    ← リファレンス・リサーチ
├── 04_Archive/      ← 完了・非アクティブ
└── 05_Diary/        ← 日記（diary スキルで生成）
```

ユーザーの実際のフォルダ構成を確認してから提案すること。

## Gotchas

- **frontmatter を破壊しない**: YAML ブロック（`---` で囲まれた部分）は正確に編集する。特に `tags:` の形式（リスト形式 vs インライン）を保持する
- **Google Drive 同期中のファイル操作**: 移動は 1 ファイルずつ行う。大量一括移動はロックの原因になる
- **リンク切れに注意**: Obsidian の `[[wikilink]]` は移動後にパスが変わると切れる。`[[ファイル名]]`（ファイル名のみ）形式なら問題ないが、パス付きリンクは要確認
- **削除はしない**: 迷ったら移動しない。ユーザーに確認を取る
- **`obsidian-utils` との棲み分け**: インデックスファイル（MOC）の更新は `obsidian-utils` スキルに任せる
