# Windsurf との統合

## 方針

Windsurfには `SKILL.md` をGlobal Skillsとして配布します。各プロジェクトへのGit submoduleやWorkspace symlinkは、同期・gitlink事故を避けるため使用しません。

## セットアップ

```bash
git clone https://github.com/gon9/ore-skills.git ~/workspace/ai-agent/ore-skills
cd ~/workspace/ai-agent/ore-skills

# 既定はstable
bash scripts/install.sh --target=windsurf --channel=stable
bash scripts/doctor.sh --channel=stable
```

配置先は `~/.codeium/windsurf/skills/<name>/` です。symlinkなので、リポジトリを `git pull` すると内容が反映されます。試験中のスキルが必要な場合だけ `--channel=experimental` または `--channel=all` を明示します。

## 使い方

Windsurfは `SKILL.md` の `description` を読み、タスクに合うスキルを選択します。認識されない場合は次を確認します。

1. Windsurfを再起動する。
2. `bash scripts/doctor.sh --channel=stable` を実行する。
3. `SKILL.md` のfrontmatterとディレクトリ名が一致することを確認する。

## Pythonコードとの併用

アプリケーションコードが実装を直接必要とする場合だけ、clone済みリポジトリへの明示的なpath依存を設定します。

```toml
[tool.uv.sources]
media = { path = "/absolute/path/to/ore-skills/skills/media", editable = true }
spec = { path = "/absolute/path/to/ore-skills/skills/spec", editable = true }
```

## MCPとの併用

MCPは外部サービス、認証、動的データなど実行時接続が必要な能力だけに使用します。現在の `ore-skills-server` は実験的なstdioサーバーで、`get_transcript` と `check_spec` のみを公開します。通常の手順・知識を使うためにMCPを設定する必要はありません。

詳細は [usage_patterns.md](usage_patterns.md) を参照してください。
