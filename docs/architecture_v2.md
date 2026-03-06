# アーキテクチャ設計書 (v2)

調査結果に基づき、Anthropicの思想を取り入れた新しいアーキテクチャ定義です。

## 1. コンセプト

- **Skills as a Package**: 各スキルは独立したPythonパッケージであり、かつAIへのインストラクションを持つ単位である。
- **Monorepo Management**: `uv` workspaceにより、複数のスキルを単一リポジトリで効率的に管理する。
- **Unified Interface**: MCP (Model Context Protocol) を通じて、全てのスキルに統一的なインターフェースでアクセスする。
- **Progressive Disclosure（段階的開示）**: AIエージェントに対して、すべての情報を一度に与えるのではなく、必要になった段階で必要な情報だけを提示する設計思想です。

## 2. Progressive Disclosure (段階的開示) とは
AIエージェントに対して、すべての情報を一度に与えるのではなく、必要になった段階で必要な情報だけを提示する設計思想です。

- **Level 1: Discovery (発見)**
    - エージェントが最初に認識する情報。
    - `SKILL.md` のフロントマター (name, description) のみ。
    - 常にコンテキストに含まれる（非常に軽量）。
- **Level 2: Overview (概要)**
    - スキルを使用すると判断した時に読み込む情報。
    - `SKILL.md` の本文。
    - スキルの使い方、主要な機能のリスト、次のステップへのポインタ。
- **Level 3: Details (詳細)**
    - 具体的なタスク実行時に必要に応じて読み込む情報。
    - `reference/` ディレクトリ内のドキュメント（API仕様、詳細な例、データスキーマなど）。
    - 実行可能なスクリプト (`src/` 内のコード) は読み込まずに実行する。

## 3. ディレクトリ構成

```text
ore-skills/
├── pyproject.toml          # [Workspace Root] 全体の設定、Linter/Test設定
├── uv.lock                 # 依存関係のロックファイル
├── skills/                 # [Skills Domain] 各スキルパッケージの格納場所
│   ├── common/             # 共通ユーティリティ (ロガー、設定管理など)
│   ├── media/              # メディア処理スキルセット
│   │   ├── pyproject.toml  # 依存関係定義 (e.g. youtube-transcript-api)
│   │   ├── SKILL.md        # [Level 1 & 2] Entry point
│   │   ├── reference/      # [Level 3] Detailed documentation
│   │   │   ├── youtube.md  # Detailed usage of YouTube functions
│   │   │   └── examples.md # Code examples
│   │   ├── src/            # Implementation code
│   │   │   └── media/
│   │   └── tests/
│   └── spec/               # 仕様書作成・チェックスキルセット
│       ├── pyproject.toml
│       ├── SKILL.md        # [Level 1 & 2] Entry point
│       ├── reference/      # [Level 3] Detailed documentation
│       │   └── format.md   # Specification format guide
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

## 4. SKILL.md 設計ガイドライン
- **500行以内**: ファイルサイズを小さく保つ。
- **YAML Frontmatter**: `name` と `description` を正確に記述する。
- **Navigation**: 詳細な情報は `reference/*.md` へのリンク（ファイルパスの提示）として記述し、AIが必要な時に `read_file` ツールで読めるようにする。
- **Execution**: コードの実行方法を具体的に示す（例: `uv run -m media.youtube ...`）。

### SKILL.md Template
```markdown
---
name: skill-name
description: A short description of what this skill does.
---

# Skill Name

## Overview
Brief explanation of the skill capabilities.

## Capabilities
- **Feature A**: Description. See [reference/feature_a.md](reference/feature_a.md) for details.
- **Feature B**: Description. See [reference/feature_b.md](reference/feature_b.md) for details.

## Usage
### Feature A
Command to run feature A:
\`\`\`bash
uv run ...
\`\`\`

## References
- [API Reference](reference/api.md)
- [Examples](reference/examples.md)
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
