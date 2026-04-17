---
name: rules-generator
description: "Analyze a project's source code, dependency files, and directory structure to generate CLAUDE.md, AGENTS.md, or .cursorrules files. Use when the user mentions rules file generation, project setup for AI agents, CLAUDE.md creation, AGENTS.md scaffolding, or wants to bootstrap AI agent configuration for a new or existing project."
license: MIT
compatibility: Requires Python 3.12+
metadata:
  author: gon9a
  version: "1.0"
---

# Rules Generator Skill

プロジェクトのソースコードや依存関係ファイルを解析し、AIエージェント向けのルールファイル（`CLAUDE.md`, `AGENTS.md`, `.cursorrules`）の雛形を自動生成する。

## ワークフロー

### 1. プロジェクト解析

以下のファイル・ディレクトリを調査し、プロジェクトの技術スタックを特定する:

| 解析対象 | 検出内容 |
|---------|---------|
| `pyproject.toml` / `setup.py` / `setup.cfg` | Python バージョン、依存パッケージ、ツール設定 (ruff, pytest, mypy 等) |
| `package.json` / `package-lock.json` | Node.js フレームワーク、ビルドツール、lint 設定 |
| `Cargo.toml` | Rust プロジェクト |
| `go.mod` | Go プロジェクト |
| `Dockerfile` / `docker-compose.yml` | コンテナ化戦略 |
| `.github/workflows/` | CI/CD パイプライン |
| `tsconfig.json` | TypeScript 設定 |
| `.eslintrc*` / `biome.json` | Lint / Formatter 設定 |
| `Makefile` / `justfile` | ビルド・タスクランナー |
| ディレクトリ構造 | `src/`, `tests/`, `app/`, `pages/` 等からアーキテクチャを推測 |

### 2. 出力フォーマット選択

ユーザーに出力先を確認する:

- **`CLAUDE.md`** — Claude Code 向け（推奨）
- **`AGENTS.md`** — ベンダー非依存の標準フォーマット
- **`.cursorrules`** — Cursor 向け
- **複数同時生成** — `AGENTS.md` をベースに各ツール向けファイルを生成

### 3. ルールファイル生成

[references/template.md](references/template.md) のテンプレートに従い、検出した情報を埋め込む。

#### 生成ルール

- **命令形で書く**: 「Python 3.12 を使用すること」（「使っています」ではない）
- **否定の制約を明記する**: 「ハードコーディング禁止」「`any` 型の使用禁止」
- **テスト可能なルールにする**: 「良いコードを書く」ではなく「型推論に頼らず明示的に型定義をする」
- **Progressive Disclosure**: ルートファイルには概要のみ。詳細は `.claude/rules/*.md` 等に分割

#### セクション構成

以下のセクションを含めること（[references/template.md](references/template.md) 参照）:

1. **プロジェクト概要** — 一文で目的を説明
2. **技術スタック** — 言語、フレームワーク、ツールチェイン
3. **ディレクトリ構成** — 主要ディレクトリの役割
4. **コーディング規約** — Lint/Formatter 設定、命名規則
5. **テスト** — テストフレームワーク、実行コマンド、カバレッジ方針
6. **エラーハンドリング** — ログ形式、例外の扱い
7. **Git 規約** — ブランチ命名、コミットメッセージ形式
8. **禁止事項** — 明示的な制約リスト

### 4. 検証

生成後、以下を確認:

- [ ] プロジェクトの `pyproject.toml` / `package.json` と矛盾がないか
- [ ] 命令形で書かれているか
- [ ] 曖昧な表現がないか
- [ ] 過度に長くないか（ルートファイルは 200 行以内を目安）

### 5. 配置

```bash
# Claude Code の場合
cp CLAUDE.md /path/to/project/CLAUDE.md

# ベンダー非依存の場合
cp AGENTS.md /path/to/project/AGENTS.md

# Cursor の場合
cp .cursorrules /path/to/project/.cursorrules
```

## 注意事項

- 既存のルールファイルがある場合は **上書きせず差分を提案** する
- プロジェクト固有のドメイン知識（ビジネスロジック等）はユーザーに確認してから追記する
- API キーや秘密情報をルールファイルに含めないこと
