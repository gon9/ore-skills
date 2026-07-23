# ore-skills 利用パターン

## 基本方針

`ore-skills` は **Skill-first** で運用します。知識、判断基準、手順、ローカルで実行できる補助スクリプトは `SKILL.md` と付属リソースで配布します。MCP は Skill の代替ではなく、外部サービス、認証、動的データ、長時間プロセスなど、実行時の接続が必要な能力だけを公開する実験的な境界です。

| 用途 | 推奨経路 | 状態 |
|---|---|---|
| 個人のローカル開発 | グローバル symlink | 推奨 |
| Codex のチーム配布 | `ore-skills-stable` Plugin | 推奨 |
| 外部・動的な実行能力 | MCP | 実験的 |
| Pythonコードから直接利用 | 明示的なローカル path 依存 | 必要な場合のみ |
| 各プロジェクトへのGit submodule | 使用しない | 非推奨 |

## 配布チャネル

スキルは `docs/skill-catalog.toml` で次のチャネルに分類します。

- `stable`: 通常利用するレビュー済みスキル。インストーラーの既定値。
- `experimental`: 試験運用中のスキル。明示指定した場合だけ配布。

```bash
# stableのみ。通常はこちら
bash scripts/install.sh --channel=stable

# experimentalのみ
bash scripts/install.sh --channel=experimental

# 両方
bash scripts/install.sh --channel=all

# 配置状態も同じチャネル単位で確認
bash scripts/doctor.sh --channel=stable
```

未分類のスキルは安全側に倒して `experimental` として扱います。

## パターン1: グローバル symlink

リポジトリを1か所にcloneし、各エージェントのグローバルSkillディレクトリから参照します。編集内容が即座に反映されるため、個人環境での作成・検証に向いています。

```bash
git clone https://github.com/gon9/ore-skills.git ~/workspace/ai-agent/ore-skills
cd ~/workspace/ai-agent/ore-skills
bash scripts/install.sh --channel=stable
bash scripts/doctor.sh --channel=stable
```

各作業リポジトリに `ore-skills` を埋め込む必要はありません。

## パターン2: Codex Plugin

チームで同じレビュー済みセットを導入する場合は、`plugins/ore-skills-stable/` を使います。Pluginには、外部Python依存を持たず単体配布しやすい `stable` のcoreスキルだけを収録します。

```bash
# 正本からPlugin bundleを再生成
python3 scripts/sync-stable-plugin.py

# 差分がないことをCIやレビューで確認
python3 scripts/sync-stable-plugin.py --check
```

Pluginのスキルを直接編集せず、必ず `skills/<name>/` を編集して同期します。配布対象は `docs/skill-catalog.toml` の `plugin_bundle = "core"` で管理します。

## パターン3: MCP（実験的）

MCPは次の場合に限って検討します。

- 外部APIや認証済みサービスへ実行時に接続する
- 結果が実行時まで確定しない動的データを取得する
- 長時間処理や共有状態をサーバー側で管理する
- クライアントへ安定したツール契約を公開する必要がある

現在の `ore-skills-server` は実験的なstdioサーバーで、公開ツールは `get_transcript` と `check_spec` の2つだけです。全SkillをMCP化する方針ではありません。

```json
{
  "mcpServers": {
    "ore-skills-experimental": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/ore-skills",
        "ore-skills-server"
      ]
    }
  }
}
```

MCPへツールを追加する場合は、ツール名・引数・返却値を固定する契約テストも追加します。

## パターン4: Pythonから直接利用

アプリケーションコードがスキル実装を直接必要とする場合だけ、clone済みリポジトリへの明示的なpath依存を使います。submoduleは使いません。

```toml
[tool.uv.sources]
media = { path = "/absolute/path/to/ore-skills/skills/media", editable = true }
spec = { path = "/absolute/path/to/ore-skills/skills/spec", editable = true }
```

再現可能なチーム配布が必要になった時点で、個別パッケージのversioningとregistry公開を検討します。

## 選び方

1. 手順や知識をエージェントへ渡すだけならSkillを使う。
2. 個人環境ではsymlink、Codexチーム配布ではPluginを使う。
3. 外部接続や動的実行が本当に必要な能力だけMCPにする。
4. Pythonの直接依存はアプリケーションコードが必要とする場合に限定する。
