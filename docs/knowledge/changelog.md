# Knowledge Base Changelog

コーディングエージェントのベストプラクティス更新履歴です。

## [2026-03-29]

### Added
- 初期Knowledge Base構築。以下のカテゴリを追加。
  - `context-engineering.md`: コンテキストの関連性維持、腐敗防止、段階的開示。
  - `rules-files.md`: `CLAUDE.md`, `AGENTS.md` の運用と階層化。
  - `prompt-patterns.md`: ペルソナ指定、自己防衛プロンプト、Few-Shot。
  - `workflow-patterns.md`: Plan-First推進、Atomic Tasks分割の重要性。
  - `tool-integration.md`: agentskills.io 仕様を用いた段階的開示とMCP連携。

### Derived Skills
- `skill-catalog.md` へ抽出されたスキル候補：
  - Context Optimizer（コンテキスト要約）
  - Rules Generator（プロジェクト解析と雛形生成）
  - Task Splitter（Atomic Task への分解）
  - Prompt Linter（プロンプトの構成チェック）
