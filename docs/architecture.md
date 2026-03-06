# アーキテクチャ設計・管理方針

Skillsの管理方法として、Git Submodule、Python Package、Monorepo構成などを比較検討した結果、以下の構成を採用します。

## 1. 採用する構成: uv Workspace (Monorepo)

**理由**:
ユーザーは `uv` を使用しており、Python 3.12 環境です。`uv` の Workspace 機能を使用することで、複数の関連するパッケージを単一のリポジトリで効率的に管理できます。

### 構成図
```
ore-skills/
├── pyproject.toml        # Workspace Root (全体管理)
├── uv.lock               # 全体の依存関係ロック
├── packages/
│   ├── common/           # 共通ライブラリ
│   │   └── pyproject.toml
│   ├── spec-skills/       # Spec開発用スキル
│   │   └── pyproject.toml
│   └── media-skills/      # メディア処理スキル
│       └── pyproject.toml
└── servers/              # MCPサーバーエントリーポイント
    └── ore-skills-server/
        └── pyproject.toml
```

## 2. 他のプロジェクトからの利用方法（ベストプラクティス）

### A. 別のPythonプロジェクトで利用する場合 (推奨)
`uv` や `pip` のVCSサポート機能を利用して、必要なパッケージのみをインストールします。

```bash
# uvの場合
uv add "spec-skills @ git+https://github.com/user/ore-skills#subdirectory=packages/spec-skills"
```
これにより、Git Submoduleを使わずにバージョン管理ができ、更新も `uv lock --upgrade` 等で制御可能です。

### B. Git Submodule を利用する場合
もし、開発中のSkillsをリアルタイムで修正しながら利用したい場合（密結合な開発）は、Git Submoduleも有効です。

1. プロジェクトにSubmoduleとして追加:
   ```bash
   git submodule add https://github.com/user/ore-skills libs/ore-skills
   ```
2. Editable install で依存追加:
   ```bash
   uv add -e ./libs/ore-skills/packages/spec-skills
   ```
   
**結論**: 基本は **A案 (Git依存インストール)** を推奨しますが、頻繁にSkills側のコードも同時に修正する場合は **B案 (Submodule + Editable install)** も `uv` ならスムーズに扱えます。

## 3. MCP (Model Context Protocol) 対応
各スキルは単なる関数ライブラリとして実装し、`servers/` 配下のMCPサーバー実装がそれをラップして公開する形をとります。
これにより、「単にPythonスクリプトから使いたい場合」と「AIエージェントから使いたい場合」の両方に対応できます。

## 4. CI/CD & 品質管理
- **Ruff**: 全パッケージに統一した設定を適用。
- **Pytest**: パッケージごとにテストを実行。
