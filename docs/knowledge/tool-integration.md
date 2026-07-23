# Tool Integration

AIコーディングエージェントの能力を、外部ツールの統合によって拡張するための技術と設計のベストプラクティスです。

## Last Updated: 2026-06-28

## 現在のベストプラクティス

### 1. 段階的開示 (Progressive Disclosure)
- **agentskills.io 仕様**: スキルのすべてを最初から読み込ませない。
  1. Metadata: 名前と説明文から使うかどうか判断させる
  2. Instructions (`SKILL.md`): 詳細な指示をロード
  3. Resources (`references/*`): 必要に応じて具体例などを参照
- 這い回るような大規模なディレクトリ構造や不要なファイルをコンテキストに詰め込ませないために必須。

### 2. Model Context Protocol (MCP) の活用
- エージェントとローカル環境・リモートリソースをセキュアに繋ぐプロトコル。
- 単一のターミナルコマンドやスクリプトを個別にツールとして登録するのではなく、MCPサーバー経由で統合されたツール群（機能群）を透過的に呼び出せるようにする。

### 3. 確定的ロジックの隔離
- LLMは非決定的な推論エンジンであるため、「必ず一字一句違わず同じ出力をすべきフォーマット変換」や「特定のパラメータに基づく厳密なバリデーション」といった処理をプロンプト内で行わせるのは不適。
- このような確定的（Deterministic）なロジックはスクリプト化し、`scripts/` に格納してAIにこれを実行（Run）させる運用がベスト。

## 変化の兆候・注目トピック
- Codex の現行ガイダンスは `AGENTS.md` を durable なリポジトリ規約として明示し、skills / MCP / automations を組み合わせる方向に寄っている。
- `~/.agents/skills` のような共有配布面が、Codex / Antigravity / Devin 互換の cross-agent レイヤーとして実用的になってきている。
- エージェント向けに最適化された軽量な CLI ツール群のオープン化と標準化競争が続いている。

## ore-skills への示唆
- **実験的MCP**: `ore-skills-server` は、外部・動的能力だけを公開する試験実装。
- `skills` の機能は可能な限り「推論」と「確定的実行」を分け、「確定的実行」はCLIスクリプトで提供する設計を徹底する。
- 配布面は `scripts/install.sh` の `--target=agents` を基準に、Codex / Antigravity / Devin 系の cross-agent 面へ寄せる。
