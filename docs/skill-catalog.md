# Skill Catalog

`docs/knowledge/` に蓄積されたベストプラクティスから導出された、AIエージェントのスキル候補と実装状況を管理するカタログです。

## ステータス凡例
- 🟢 Implemented — 実装済み
- 🟡 Planned — 実装予定（調査完了）
- ⚪ Candidate — 候補（未調査）

## 現在のカタログ

| スキル名 | ステータス | 由来（カテゴリ） | 概要 |
|---------|----------|----------------|------|
| **media** | 🟢 実装済 | 既存・手動抽出 | YouTube文字起こし |
| **obsidian_utils** | 🟢 実装済 | 既存・手動抽出 | Obsidian Vault インデックス管理 |
| **spec** | 🟢 実装済 | workflow-patterns | 仕様書バリデーション（Plan-Firstと親和性高） |
| **video_summary** | 🟢 実装済 | 既存・手動抽出 | 動画要約・テキスト抽出 |
| **youtube_summary** | 🟢 実装済 | 既存・手動抽出 | yt-dlp/whisper フォールバック付き文字起こし |
| **context-optimizer** | ⚪ 候補 | context-engineering | スレッドの長大なログから重要な結論のみを抽出要約 |
| **rules-generator** | ⚪ 候補 | rules-files | ソースや package.json を解析して `AGENTS.md` 雛形を自動生成 |
| **task-splitter** | ⚪ 候補 | workflow-patterns | 大きな要件を 10〜15分の Atomic Task リストに自動分解 |
| **prompt-linter** | ⚪ 候補 | prompt-patterns | 対象のプロンプトが Defensive や Few-Shot を含んでいるか診断 |

## 新規スキルの追加プロセス

1. `create-skill.sh` スクリプトを使用して雛形を生成
2. `skills/<skill-name>/SKILL.md` を agentskills.io 仕様に従って執筆
3. 実装とテストを追加
4. 本カタログのステータスを `🟢 実装済` に更新
