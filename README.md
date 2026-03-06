# ore-skills

AIエージェント（LLM）のためのスキル（関数・クラス群）およびMCP（Model Context Protocol）サーバーを管理するリポジトリです。

## 概要

このプロジェクトは、AIエージェントが利用可能なツール群を「Skills」として定義し、再利用可能な形で管理することを目的としています。
`uv` を使用した Workspace 機能（Monorepo構成）を採用し、複数のスキルパッケージを一元管理します。

## 構成

このリポジトリは Monorepo 構成を採用しており、`packages/` ディレクトリ配下に各機能ごとのパッケージを配置します。

- **packages/common**: 共通ユーティリティ、基底クラスなど
- **packages/spec-skills**: Spec（仕様書・要件定義書）開発支援ツール
- **packages/media-skills**: YouTube文字起こし・要約などのメディア処理ツール

## 環境

- **OS**: macOS
- **Language**: Python 3.12+
- **Package Manager**: uv
- **Linter/Formatter**: ruff
- **Test**: pytest

## 利用方法

### MCPサーバーとして利用する場合

Claude DesktopなどのMCPクライアントから利用するには、以下の設定を `claude_desktop_config.json` 等に追加してください。

```json
{
  "mcpServers": {
    "ore-skills": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/gon9a/workspace/ai_agent/ore-skills",
        "ore-skills-server"
      ]
    }
  }
}
```

### ライブラリとして利用する場合

```bash
# uvを使用して依存関係に追加
uv add git+https://github.com/your-username/ore-skills --subdirectory packages/spec-skills
```
