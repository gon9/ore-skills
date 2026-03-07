# アーキテクチャ設計書 (v2)

調査結果に基づき、Anthropicの思想を取り入れた新しいアーキテクチャ定義です。

## 1. コンセプト

- **Skills as a Package**: 各スキルは独立したPythonパッケージであり、かつAIへのインストラクションを持つ単位である。
- **Monorepo Management**: `uv` workspaceにより、複数のスキルを単一リポジトリで効率的に管理する。
- **Unified Interface**: MCP (Model Context Protocol) を通じて、全てのスキルに統一的なインターフェースでアクセスする。
- **Progressive Disclosure（段階的開示）**: AIエージェントに対して、すべての情報を一度に与えるのではなく、必要になった段階で必要な情報だけを提示する設計思想です。

## 2. Progressive Disclosure (段階的開示) とは
AIエージェントに対して、すべての情報を一度に与えるのではなく、必要になった段階で必要な情報だけを提示する設計思想です。

**agentskills.io 仕様に準拠:**

- **Level 1: Metadata (~100 tokens)**
    - エージェントが最初に認識する情報。
    - `SKILL.md` のフロントマター (name, description) のみ。
    - 起動時にすべてのスキルの metadata が読み込まれる。
- **Level 2: Instructions (< 5000 tokens 推奨)**
    - スキルが起動された時に読み込む情報。
    - `SKILL.md` の本文。
    - スキルの使い方、主要な機能のリスト、次のステップへのポインタ。
- **Level 3: Resources (必要に応じて)**
    - 具体的なタスク実行時に必要に応じて読み込む情報。
    - `references/` ディレクトリ内のドキュメント（API仕様、詳細な例、データスキーマなど）。
    - `scripts/` 内の実行可能スクリプト（読み込まずに実行）。
    - `assets/` 内のテンプレートやデータファイル。

## 3. ディレクトリ構成

```text
ore-skills/
├── pyproject.toml          # [Workspace Root] 全体の設定、Linter/Test設定
├── uv.lock                 # 依存関係のロックファイル
├── skills/                 # [Skills Domain] 各スキルパッケージの格納場所
│   ├── common/             # 共通ユーティリティ (ロガー、設定管理など)
│   ├── media/              # メディア処理スキルセット
│   │   ├── pyproject.toml  # 依存関係定義 (e.g. youtube-transcript-api)
│   │   ├── SKILL.md        # [Level 1 & 2] Entry point (< 5000 tokens)
│   │   ├── references/     # [Level 3] Detailed documentation
│   │   │   └── youtube.md  # Detailed usage of YouTube functions
│   │   ├── scripts/        # [Level 3] Executable scripts (optional)
│   │   ├── src/            # Implementation code
│   │   │   └── media/
│   │   └── tests/
│   └── spec/               # 仕様書作成・チェックスキルセット
│       ├── pyproject.toml
│       ├── SKILL.md        # [Level 1 & 2] Entry point (< 5000 tokens)
│       ├── references/     # [Level 3] Detailed documentation
│       │   └── format.md   # Specification format guide
│       ├── scripts/        # [Level 3] Executable scripts (optional)
│       ├── src/            # Implementation code
│       │   └── spec/
│       └── tests/
├── server/                 # [Application Layer] MCPサーバー実装
│   └── ore-skills-server/  # 統合MCPサーバー
│       ├── pyproject.toml
│       └── src/ore_skills_server/
│           └── main.py     # 各Skillsをimportし、MCP Toolとして登録する
└── docs/                   # Project documentation
```

## 4. SKILL.md 設計ガイドライン (agentskills.io 準拠)

### Frontmatter (必須)
- **`name`**: 1-64文字、小文字英数字とハイフン (`a-z`, `-`) のみ、親ディレクトリ名と一致必須
- **`description`**: 1-1024文字、「何をするか」と「いつ使うか」を明確に記述、具体的なキーワードを含める
- **`license`** (オプション): ライセンス情報
- **`compatibility`** (オプション): 環境要件（1-500文字）
- **`metadata`** (オプション): 追加プロパティ（key-value マップ）
- **`allowed-tools`** (オプション): 事前承認ツールのリスト（実験的機能）

### Body Content (< 5000 tokens 推奨)
- ステップバイステップの手順
- 入出力の例
- よくあるエッジケース
- **Navigation**: 詳細な情報は `references/*.md` へのリンクとして記述
- **Execution**: スクリプトの実行方法を具体的に示す（例: `scripts/extract.py`）

### SKILL.md Template (agentskills.io 準拠)
```markdown
---
name: skill-name
description: What this skill does and when to use it. Include specific keywords for agent discovery.
license: MIT
compatibility: Requires Python 3.12+
metadata:
  author: your-org
  version: "1.0"
---

# Skill Name

## Overview
Brief explanation of the skill capabilities.

## Capabilities
- **Feature A**: Description. See [references/feature_a.md](references/feature_a.md) for details.
- **Feature B**: Description. See [references/feature_b.md](references/feature_b.md) for details.

## Usage
### Feature A
Step-by-step instructions:
1. Prepare input data
2. Run the script: `scripts/process.py`
3. Check output

Example:
\`\`\`bash
scripts/process.py --input data.json
\`\`\`

## References
- [API Reference](references/REFERENCE.md)
- [Examples](references/examples.md)
```

## 5. 技術スタック
- **Package Manager**: `uv` (Workspace機能)
- **Language**: Python 3.12
- **Linter/Formatter**: `ruff`
- **Testing**: `pytest`
- **Interface**: MCP (Model Context Protocol) via `ore-skills-server`

## 6. 開発フロー

1. **スキルの追加**:
   - `skills/` 配下にディレクトリ作成 (`uv init --lib`)
   - `pyproject.toml` (Root) の `workspace.members` に追加
   - ロジック実装 & `SKILL.md` 作成
2. **MCPへの登録**:
   - `server/ore-skills-server` の依存関係に新スキルを追加
   - `main.py` でツールとして登録
3. **テスト**:
   - `uv run pytest` で全体テスト実行

## 7. 依存関係管理

```toml
# Root pyproject.toml
[tool.uv.sources]
common = { workspace = true }
media = { workspace = true }
spec = { workspace = true }
```

このようにWorkspace機能を使うことで、ローカルの最新コードを常に参照しながら開発が可能。
