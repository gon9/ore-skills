# ore-skills

AIエージェント（LLM）のためのスキル（関数・クラス群）およびMCP（Model Context Protocol）サーバーを管理するリポジトリです。

## 概要

`ore-skills` は、AIエージェント（Claude等）が利用するスキルを管理するモノレポです。
**Progressive Disclosure（段階的開示）** の原則に基づき、必要な情報を必要な時に必要な分だけ提供する設計になっています。

各スキルは `SKILL.md` を核に独立したパッケージとして実装され、以下の方法で利用できます：
- **グローバル symlink (推奨)**: `scripts/install.sh` で `~/.agents/skills/`, `~/.claude/skills/`, `~/.codeium/windsurf/skills/` に symlink。どのプロジェクトのワークディレクトリでも同じスキルが認識される
- **MCP Server**: AIエージェントから直接利用
- **Python Library**: 必要な場合のみ直接 import

> **NOTE**: 過去のグローバルルール「Git Submodule で他リポジトリに組み込む」は **非推奨** に変更しました。
> Obsidian vault 配下などで submodule / 入れ子 repo を持つと、Google Drive 同期 / Antigravity / Windsurf の Source Control が壊れる事故が再現しました。
> 詳細: `docs_obsidian/00_Inbox/git同期トラブル_教訓_2026-05-11.md`

## コントリビュート

ore-skills への貢献を歓迎します！新しいスキルを追加する場合は、[CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## クイックスタート（推奨セットアップ）

ore-skills は **agentskills.io 仕様準拠** で、Windsurf / Claude Code / その他 cross-agent 互換ツールから同一の SKILL.md がそのまま利用できます。

```bash
# 1. 一度だけクローン (場所はどこでもよい — このリポジトリそのもの)
git clone https://github.com/gon9/ore-skills.git ~/workspace/ai-agent/ore-skills

# 2. 全エージェントから読まれる位置へ symlink を張る
bash ~/workspace/ai-agent/ore-skills/scripts/install.sh

# 3. 設置状態を確認
bash ~/workspace/ai-agent/ore-skills/scripts/doctor.sh
```

`install.sh` は以下3パスに symlink を作成します（既存 dangling symlink は対話確認のうえ修復、実体ディレクトリは `.bak.<timestamp>` に退避してから置換）:

| パス | 用途 |
|---|---|
| `~/.agents/skills/<name>` | **cross-agent** (Windsurf が公式に追加スキャン、将来の他エージェント互換用) |
| `~/.claude/skills/<name>` | Claude Code Personal Skills |
| `~/.codeium/windsurf/skills/<name>` | Windsurf Global Skills |

これだけで **どの作業リポジトリにいても、Windsurf / Claude Code 等から同じ skill が呼び出せます**。各作業リポジトリには何も追加しません（submodule なし、`.claude/` `.windsurf/` ディレクトリ追加なし）。

### よく使うコマンド

```bash
bash scripts/install.sh                     # 全3パスへ配置（既存と衝突したら対話確認）
bash scripts/install.sh --dry-run           # 変更内容だけ確認
bash scripts/install.sh --target=claude     # Claude Code だけ
bash scripts/install.sh --target=windsurf   # Windsurf だけ
bash scripts/install.sh --prune --yes       # 削除済み skill 由来の symlink も掃除

bash scripts/doctor.sh                       # 現状診断（dangling 等の検知）
bash scripts/uninstall.sh                    # ore-skills 由来の symlink を全解除（実体は触らない）
```

### 更新

```bash
git -C ~/workspace/ai-agent/ore-skills pull   # ore-skills を更新するだけ
# symlink 経由のため、各エージェント側の再設定は不要
```

## ⚠️ 非推奨パターン

以下の方法は **過去に事故が起きた** ため非推奨です。

- **Git submodule で各プロジェクトに ore-skills を取り込む**
  - Antigravity / Windsurf の Source Control / Google Drive 同期が gitlink を壊れた状態でキャッシュしやすい
  - 特に Obsidian vault 配下で実施すると `core.repositoryformatversion does not support extension: worktreeconfig` 等のエラーで vault のチャットが破壊された実績あり
- **vault や同期フォルダ内に ore-skills を clone する**
  - 同上。`.git/modules/` が同期対象に巻き込まれて壊れる
- **各プロジェクトの `.claude/skills/` `.windsurf/skills/` 配下に手動 symlink**
  - うっかり commit して衝突しやすい。グローバル配置のほうが境界が明確

## 詳細ドキュメント

- [docs/skill-authoring.md](docs/skill-authoring.md)
- [docs/windsurf_integration.md](docs/windsurf_integration.md)
- [docs/claude_code_integration.md](docs/claude_code_integration.md)
- [docs/claude-windsurf-fusion.md](docs/claude-windsurf-fusion.md)
- [docs/usage_patterns.md](docs/usage_patterns.md)

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
        "/Users/gon9a/workspace/ai-agent/ore-skills",
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
