---
name: rules-generator
description: "プロジェクトのソースコード・依存関係・ディレクトリ構造を解析し、AGENTS.md を生成する。新規プロジェクトのセットアップ時、または既存の AGENTS.md の品質チェック・更新時に使用する。"
license: MIT
compatibility: Requires Python 3.12+
metadata:
  author: gon9a
  version: "2.0"
---

# Rules Generator Skill

プロジェクト解析 → AGENTS.md 生成・品質チェックを行うスキル。

## 重要な原則

AGENTS.md は [agents.md](https://agents.md) 仕様 (Linux Foundation / Agentic AI Foundation 管轄) に準拠するオープン標準。
Cursor, Windsurf, GitHub Copilot, Gemini CLI, Claude Code, VS Code, JetBrains Junie がネイティブ対応。

**IDE固有のコピーファイル (.windsurfrules, .cursorrules 等) は生成しない。**
AGENTS.md 1ファイルで全IDEに効く。

## ワークフロー

### 1. プロジェクト解析

[references/detection-rules.md](references/detection-rules.md) に従い、技術スタックを検出する。

### 2. AGENTS.md 生成

[references/template.md](references/template.md) のテンプレートに従って生成する。

#### 品質基準

- **150行以内** — 長いとエージェントの精度が下がる
- **ツールで強制できるルールは書かない** — eslint/ruff があるならそちらで
- **エージェントが発見できる情報は書かない** — package.json を読めばわかることは不要
- **コード例 > 文章** — 1つのコードスニペットは3段落の説明に勝る
- **命令形で書く** — 「使用すること」（「使っています」ではない）

#### 必須セクション

1. **プロジェクト概要** — 1-3行で「何をするか」
2. **コマンド** — build/test/lint の実行可能コマンド（コードブロックで記述）
3. **境界 (Boundaries)** — 3段階モデル:
   - **Always** — 必ずやること
   - **Ask First** — 確認してからやること
   - **Never** — 絶対やらないこと

#### 推奨セクション

- ディレクトリ構造
- コーディング規約（コード例付き）
- テスト
- Git ワークフロー

### 3. 品質チェック

既存の AGENTS.md に対して以下を検証:

- [ ] 150行以内か
- [ ] コマンドセクションがあるか
- [ ] 境界 (Boundaries) セクションがあるか
- [ ] 不要なコピーファイル (.windsurfrules, .cursorrules) が存在しないか
- [ ] CLAUDE.md がある場合、AGENTS.md を参照しているか
- [ ] 命令形で書かれているか
- [ ] プロジェクトの実態と矛盾がないか

### 4. CLAUDE.md との関係

CLAUDE.md は Claude Code 固有の設定（サブエージェント、hooks、MCP等）のみに使う。
共通ルールは AGENTS.md に書き、CLAUDE.md の先頭に以下を記載:

```markdown
共通ルールは [AGENTS.md](AGENTS.md) を参照すること。
```

### 5. Progressive Disclosure

AGENTS.md が 150行を超える場合は分割する:

```
project/
├── AGENTS.md              # 概要 + コマンド + 境界
└── docs/agents/
    ├── architecture.md    # アーキテクチャ詳細
    └── testing.md         # テスト戦略詳細
```

## ワークスペースメタルール

`~/workspace/AGENTS.md` にメタルール（AGENTS.md の書き方ルール自体）を配置している。
新しいプロジェクトの AGENTS.md を生成する際は、このメタルールの品質基準に従うこと。

## 注意事項

- 既存のルールファイルがある場合は上書きせず差分を提案する
- プロジェクト固有のドメイン知識はユーザーに確認してから追記する
- API キーや秘密情報をルールファイルに含めないこと
- 失敗パターン: AIが同じミスを2回したら AGENTS.md に追加するよう提案する
