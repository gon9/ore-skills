# Skills / MCP 構成に関する調査報告と方針

Anthropic公式の「Skills」の思想、およびModel Context Protocol (MCP) のベストプラクティスを調査しました。
これを踏まえ、`ore-skills` のあるべき姿を再定義します。

## 1. Anthropicにおける「Skills」の定義・思想

Anthropic公式リポジトリ (`anthropics/skills`) では、Skillsは以下のように定義されています。

> **"Skills are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks."**

つまり、Skillとは単なるPythonコード（関数）だけではなく、**「AIに特定のタスクを遂行させるための包括的なパッケージ」** です。

### 構成要素
1.  **SKILL.md**: スキルの定義ファイル（必須）。
    *   **YAML Frontmatter**: 名前 (`name`)、説明 (`description`)。
    *   **Instructions**: AIへの具体的な指示、ガイドライン、使用例。
2.  **Code/Scripts**: 実際の処理を行うプログラム（Pythonスクリプト等）。

**重要な示唆**:
AIエージェントのためのスキル開発では、**「Pythonコードの品質」と同等に、「AIへのインストラクション（SKILL.md）の品質」が重要**になります。

## 2. MCP (Model Context Protocol) との関係

MCPは、これらのSkillsをAI（Claude等）と接続するための標準プロトコルです。
調査の結果、MCPサーバーの実装には以下のパターンが推奨されます。

*   **ドメイン駆動**: 関連するツール群を1つの「MCP Server」としてまとめる。
*   **FastMCP**: Python SDKの `FastMCP` クラスを使用することで、アノテーション (`@mcp.tool`) ベースで簡単にツール定義が可能。

## 3. `ore-skills` への適用方針（再設計案）

現状の `packages/media-skills` といった構成を、より「Skills」の思想に近づけ、かつ管理しやすくするために、以下の変更を提案します。

### A. ディレクトリ構成の変更

`packages/` という汎用的な名前ではなく、**`skills/`** ディレクトリを採用します。
また、パッケージ名は `media-skills` のように冗長にせず、`skills/` 配下であることを活かしてシンプルにします。

```text
ore-skills/
├── pyproject.toml        # Workspace Root
├── skills/               # Skills格納ディレクトリ (旧 packages/)
│   ├── media/            # メディア処理スキル
│   │   ├── pyproject.toml
│   │   ├── SKILL.md      # ★AI向け説明書 (Anthropic流)
│   │   └── src/media/
│   │       ├── tools.py  # MCP Tool定義
│   │       └── core.py   # ロジック
│   ├── spec/             # 仕様書開発スキル
│   │   ├── pyproject.toml
│   │   ├── SKILL.md
│   │   └── src/spec/
│   └── common/           # 共通ライブラリ
└── server/               # 統合MCPサーバー
    └── pyproject.toml
```

### B. 管理方針のアップデート

1.  **SKILL.md の導入**:
    各スキルディレクトリに `SKILL.md` を配置し、そのスキルが「何をするものか」「どのような場面で使うべきか」を自然言語で記述します。これは将来的にAIが自己検索してスキルを発見する際にも役立ちます。

2.  **uv Workspace の維持**:
    `skills/media`, `skills/spec` をWorkspaceメンバーとして管理し、依存関係を一元管理する方針は維持します（ベストプラクティス通り）。

3.  **MCPサーバーの粒度**:
    *   開発時: `server/` ディレクトリの統合サーバーから全スキルを利用可能にする。
    *   配布時: 各スキル単体でも利用可能なように、依存関係を整理する。

## 4. 結論

「管理のしやすさ」と「Skillsとしての再利用性」を高めるため、**`packages/` → `skills/` への移行**と、**`SKILL.md` によるメタデータ管理の導入**を推奨します。
