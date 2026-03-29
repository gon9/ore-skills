# Coding Agent Knowledge Base

コーディングエージェント（AIアシスタント）を最大限に活用するためのベストプラクティス集です。
`ore-skills` は、これらのベストプラクティスを具体的な「スキル（機能）」として実装するためのリポジトリです。

## 📚 カテゴリ

1. **[Context Engineering](context-engineering.md)**
   - エージェントに適切な文脈（コンテキスト）を与えるための戦略
   - 関連情報の渡し方、ノイズの削り方
2. **[Rules & Instructions](rules-files.md)**
   - `CLAUDE.md`, `AGENTS.md`, `.cursorrules` 等の書き方
   - プロジェクト固有のルール設定のベストプラクティス
3. **[Prompt Patterns](prompt-patterns.md)**
   - エージェントに意図通りに動いてもらうためのプロンプトの型
   - Few-Shot プロンプティング、思考プロセスの制御
4. **[Workflow Patterns](workflow-patterns.md)**
   - エージェントと協働する際の進め方
   - Plan-First（計画先行）、Atomic Tasks（小さなタスク分割）など
5. **[Tool Integration](tool-integration.md)**
   - MCP (Model Context Protocol), Agent Skills などの外部ツール連携
   - ツール設計のベストプラクティスとトレンド

---

## 🔄 更新フロー（月1回推奨）

1. コーディングエージェントの最新動向（Medium, X, 公式ブログ等）を調査
2. 該当するカテゴリの Markdown を更新
3. 新たに「スキル化（自動化・ツール化）」できそうなアイデアがあれば、`../skill-catalog.md` に追記
4. `changelog.md` に変更内容を記録
