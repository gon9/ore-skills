# アーキテクチャ設計書 (v2)

調査結果に基づき、Anthropicの思想を取り入れた新しいアーキテクチャ定義です。

## 1. コンセプト

- **Skills as a Package**: 各スキルは独立したPythonパッケージであり、かつAIへのインストラクションを持つ単位である。
- **Monorepo Management**: `uv` workspaceにより、複数のスキルを単一リポジトリで効率的に管理する。
- **Unified Interface**: MCP (Model Context Protocol) を通じて、全てのスキルに統一的なインターフェースでアクセスする。

## 2. ディレクトリ構成

```text
ore-skills/
├── pyproject.toml          # [Workspace Root] 全体の設定、Linter/Test設定
├── uv.lock                 # 依存関係のロックファイル
├── skills/                 # [Skills Domain] 各スキルパッケージの格納場所
│   ├── common/             # 共通ユーティリティ (ロガー、設定管理など)
│   ├── media/              # メディア処理スキルセット
│   │   ├── pyproject.toml  # 依存関係定義 (e.g. youtube-transcript-api)
│   │   ├── SKILL.md        # AI向けスキル定義書 (名前、説明、使用例)
│   │   └── src/media/      # 実装コード
│   │       ├── __init__.py # エクスポート定義
│   │       └── youtube.py  # 実装ロジック
│   └── spec/               # 仕様書作成・チェックスキルセット
│       ├── pyproject.toml
│       ├── SKILL.md
│       └── src/spec/
└── server/                 # [Application Layer] MCPサーバー実装
    └── ore-skills-server/  # 統合MCPサーバー
        ├── pyproject.toml
        └── src/ore_skills_server/
            └── main.py     # 各Skillsをimportし、MCP Toolとして登録する
```

## 3. 各コンポーネントの役割

### A. Skills (`skills/*`)
具体的な機能（ビジネスロジック）の実装場所。
- **命名規則**: `skills/<category>` (例: `skills/media`)
- **SKILL.md**: そのスキルが提供する機能のAI向け要約。
    ```yaml
    ---
    name: media-skills
    description: YouTube動画の文字起こしや要約を行うスキルセット
    ---
    # ガイドライン
    ユーザーから動画の要約を依頼された場合は、まず get_transcript ツールを使用してください...
    ```

### B. Common (`skills/common`)
全スキルで共通して使われる基盤機能。
- ロギング設定 (`setup_logger`)
- エラーハンドリング共通化
- MCP用のヘルパー関数

### C. Server (`server/ore-skills-server`)
各スキルを束ねて、外部（Claude Desktop等）に公開するためのエントリーポイント。
各スキルパッケージをライブラリとしてインポートし、`@mcp.tool` でラップして公開する。

## 4. 開発フロー

1. **スキルの追加**:
   - `skills/` 配下にディレクトリ作成 (`uv init --lib`)
   - `pyproject.toml` (Root) の `workspace.members` に追加
   - ロジック実装 & `SKILL.md` 作成
2. **MCPへの登録**:
   - `server/ore-skills-server` の依存関係に新スキルを追加
   - `main.py` でツールとして登録
3. **テスト**:
   - `uv run pytest` で全体テスト実行

## 5. 依存関係管理

```toml
# Root pyproject.toml
[tool.uv.sources]
common = { workspace = true }
media = { workspace = true }
spec = { workspace = true }
```

このようにWorkspace機能を使うことで、ローカルの最新コードを常に参照しながら開発が可能。
