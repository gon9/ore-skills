# CLAUDE.md — Claude Code 固有設定

共通ルールは [AGENTS.md](AGENTS.md) を参照すること。
このファイルには Claude Code でのみ有効な設定と方針を記述する。

## サブエージェントの活用方針

- 調査タスクには `Explore` エージェント（Haiku, 読み取り専用）を優先的に使用すること
- 実装計画の立案には `Plan` エージェント（読み取り専用）を使用すること
- コード修正を伴う複雑なタスクには汎用エージェント（全ツール利用可能）を使用すること
- `.claude/agents/` にカスタムエージェントが定義されている場合は、タスクに応じて活用すること

## スキルの実行コンテキスト

- 長時間かかるスキル（調査、ドキュメント生成等）は `context: fork` でサブエージェント実行を検討すること
- 短いスキル（バリデーション、フォーマット等）はメインコンテキストで直接実行してよい

## Hooks による自動化

コード変更時の品質チェックは以下の順序で自動実行される:

1. ruff check --fix（PostToolUse: Write/Edit）
2. ruff format（PostToolUse: Write/Edit）
3. skill-health check（スキル関連ファイル変更時）

## MCP Server

ore-skills-server を MCP 経由で利用する場合:

```json
{
  "mcpServers": {
    "ore-skills": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/gon9a/workspace/ai_agent/ore-skills", "ore-skills-server"]
    }
  }
}
```

## Agent Teams パターン

大規模タスク（全スキルの一斉チェック、リファクタリング等）では Agent Teams を検討すること:

- 各スキルディレクトリを独立したセッションに割り当て
- 共通の成果物（skill-catalog.md 等）への書き込みは調整して競合を避ける
- worktree isolation を活用してブランチ分離

## Permission 方針

- スキル開発時: 全ツール許可
- スキル利用時: 読み取り + スクリプト実行のみ推奨
