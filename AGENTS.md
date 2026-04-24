# AGENTS.md — ore-skills プロジェクトルール

このファイルはベンダー非依存のプロジェクトルールです。
Claude Code, Windsurf, Cursor, その他すべてのAIコーディングエージェントが参照します。

## プロジェクト概要

ore-skills は AIエージェント向けスキルを管理するモノレポです。
agentskills.io 仕様に準拠した SKILL.md を核に、Windsurf と Claude Code の両方から利用可能な共通スキル基盤を提供します。

## 技術スタック

- **言語**: Python 3.12
- **パッケージマネージャ**: uv (Workspace機能)
- **Linter/Formatter**: ruff
- **テスト**: pytest
- **インターフェース**: MCP (Model Context Protocol)
- **スキル仕様**: agentskills.io 準拠

## ディレクトリ構造

```
ore-skills/
├── skills/          # スキルパッケージ（SKILL.md + Python実装）
├── servers/         # MCPサーバー実装
├── scripts/         # セットアップ・メンテナンススクリプト
└── docs/            # ドキュメント・ナレッジベース
```

## コーディング規約

- Docstringは日本語で記述すること
- 型ヒントを可能な限り使用すること
- ハードコーディング禁止 — 設定値は環境変数で管理すること
- テストはモジュール単位で正常系・異常系を実装すること

## 品質チェックの順序

コードを変更したら以下の順序で必ず実行すること:

1. `uv run ruff check --fix src/ tests/` — Lintエラーの自動修正
2. `uv run ruff format src/ tests/` — フォーマット適用
3. `uv run pytest` — テスト実行

ruff が clean になるまで pytest を実行しないこと。

## よくある ruff エラーと対処

- **W293**: 空行に空白文字 → 空行は完全に空にする
- **F401**: 未使用import → import は必要なものだけ書く
- **UP028**: for+yield → `yield from` に置き換える

## スキル追加の手順

1. `scripts/create-skill.sh` でスキル雛形を生成
2. `skills/<name>/SKILL.md` を agentskills.io 仕様に従って作成
3. 実装コードを `skills/<name>/src/<name>/` に配置
4. テストを `skills/<name>/tests/` に追加
5. ルートの `pyproject.toml` の `workspace.members` と `tool.uv.sources` を更新
6. `docs/skill-catalog.md` のステータスを更新

## SKILL.md の必須要件

- **name**: 小文字英数字とハイフンのみ、ディレクトリ名と一致
- **description**: 「何をするか」と「いつ使うか」を含む（1-1024文字）
- **本文**: < 5000 tokens 推奨、詳細は `references/` に分離

## Git 規約

- ブランチ: `feature/`, `fix/`, `docs/` プレフィックス
- コミット: Conventional Commits 準拠
- `.env` は `.gitignore` に含める、`.env.example` を提供すること

## 禁止事項

- グローバルパッケージのインストールをしないこと
- `.env` ファイルにシークレットを直接書かないこと
- `skills/common/` ディレクトリを Windsurf/Claude Code のスキルとして登録しないこと（内部ライブラリ用）
- コメントやドキュメントに絵文字を追加しないこと（ユーザーが明示的に要求した場合を除く）
