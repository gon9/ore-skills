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

## 他のプロジェクトからの利用

### Git Submodule として利用（推奨）

```bash
# あなたのプロジェクトに ore-skills を追加
cd /path/to/your-project
git submodule add https://github.com/gon9/ore-skills.git .ore-skills
git submodule update --init --recursive
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
