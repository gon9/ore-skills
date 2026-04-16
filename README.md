# ore-skills

AIエージェント（LLM）のためのスキル（関数・クラス群）およびMCP（Model Context Protocol）サーバーを管理するリポジトリです。

## 概要

`ore-skills` は、AIエージェント（Claude等）が利用するスキルを管理するモノレポです。
**Progressive Disclosure（段階的開示）** の原則に基づき、必要な情報を必要な時に必要な分だけ提供する設計になっています。

各スキルは独立したPythonパッケージとして実装され、以下の方法で利用できます：
- **Git Submodule**: 他のプロジェクトに組み込んで利用（推奨）
- **MCP Server**: AIエージェントから直接利用
- **Python Library**: 直接importして利用

## コントリビュート

ore-skills への貢献を歓迎します！新しいスキルを追加する場合は、[CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## Windsurf との統合（最も簡単）

ore-skills は **agentskills.io 仕様に準拠** しているため、Windsurf の **Skills 機能** とネイティブに統合できます。

### クイックスタート（Global Skills）

```bash
# ore-skills をクローン
git clone https://github.com/gon9/ore-skills.git ~/ore-skills

# セットアップスクリプトを実行（Global Skills として自動統合されます）
~/ore-skills/scripts/setup-windsurf.sh
```

> **Note:** ore-skills リポジトリ内で実行すると、自動的に Global Skills として統合されます。
> Workspace Skills として統合したい場合は、対象プロジェクトのルートから実行してください（下記「Git Submodule として利用」参照）。

詳細は [docs/windsurf_integration.md](docs/windsurf_integration.md) を参照してください。

## Claude Code との統合

ore-skills は **agentskills.io 仕様に準拠** しているため、Claude Code の Skills 機能とも互換性があります。
SKILL.md の形式は Windsurf と共通で、同じスキルがそのまま動作します。

### クイックスタート（Personal Skills）

```bash
# ore-skills をクローン（Windsurf と共用可能）
git clone https://github.com/gon9/ore-skills.git ~/ore-skills

# セットアップスクリプトを実行（Personal Skills として自動統合されます）
~/ore-skills/scripts/setup-claude-code.sh
```

> **Note:** Windsurf と Claude Code の両方で使う場合は、両方のセットアップスクリプトを実行してください。
> ore-skills は一つのクローンを共有できます。

詳細は [docs/claude_code_integration.md](docs/claude_code_integration.md) を参照してください。

## 他のプロジェクトからの利用

### Git Submodule として利用

```bash
# あなたのプロジェクトに ore-skills を追加
cd /path/to/your-project
git submodule add https://github.com/gon9/ore-skills.git .ore-skills
git submodule update --init --recursive

# プロジェクトルートでセットアップスクリプトを実行
./.ore-skills/scripts/setup-windsurf.sh
```

### スキルのアップデート

ore-skills を最新のバージョンに更新するには、以下のスクリプトを実行します。

```bash
# ore-skills 本体の更新
cd ~/ore-skills
./scripts/update-skills.sh

# サブモジュールとして組み込んでいる場合（プロジェクトルートで実行）
cd /path/to/your-project
./.ore-skills/scripts/update-skills.sh
```

詳細は [docs/usage_patterns.md](docs/usage_patterns.md) を参照してください。

## 構成

```
ore-skills/
├── skills/                 # スキルパッケージ（Progressive Disclosure構造）
│   ├── common/             # 共通ユーティリティ
│   ├── media/              # メディア処理スキル（YouTube文字起こし等）
│   │   ├── SKILL.md        # [Level 1 & 2] スキルの概要
│   │   ├── references/     # [Level 3] 詳細ドキュメント
│   │   └── src/media/      # 実装コード（CLI実行可能）
│   └── spec/               # 仕様書作成・チェックスキル
│       ├── SKILL.md
│       ├── references/
│       └── src/spec/
├── servers/                # MCPサーバー実装
│   └── ore-skills-server/  # 統合MCPサーバー
└── docs/                   # ドキュメント
    ├── architecture_v2.md  # アーキテクチャ設計
    └── usage_patterns.md   # 利用パターン
```

## 環境

- **OS**: macOS
- **Language**: Python 3.12+
- **Package Manager**: uv
- **Linter/Formatter**: ruff
- **Test**: pytest

## 利用方法

### MCPサーバーとして利用する場合

#### ローカル利用 (stdio)

Claude DesktopなどのMCPクライアントから**ローカルで**利用するには、以下の設定を `claude_desktop_config.json` 等に追加してください。

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

#### リモート利用 (SSE)

EC2などでホストして**他のPCから**利用する場合は、SSE (Server-Sent Events) トランスポートを使用します。
詳細は [docs/remote_mcp_server.md](docs/remote_mcp_server.md) を参照してください。

**注意:** 現在はstdio版のみ実装されています。SSE版は設計ドキュメントのみ提供しています。

### Pythonライブラリとして利用する場合

ore-skills をサブモジュールとして追加後、プロジェクトの `pyproject.toml` で参照します。

```toml
# your-project/pyproject.toml
[tool.uv.sources]
media = { path = ".ore-skills/skills/media", editable = true }
spec = { path = ".ore-skills/skills/spec", editable = true }
```

```python
# your_code/main.py
from media import get_youtube_transcript
from spec import check_spec_file

transcript = get_youtube_transcript("video_id")
issues = check_spec_file(content)
```

詳細は [docs/usage_patterns.md](docs/usage_patterns.md) を参照してください。
