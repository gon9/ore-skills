# Claude Code との統合

## 方針

Claude Codeには `SKILL.md` をPersonal Skillsとして配布します。各プロジェクトへのGit submoduleやProject symlinkは、同期・gitlink事故を避けるため使用しません。

## セットアップ

```bash
git clone https://github.com/gon9/ore-skills.git ~/workspace/ai-agent/ore-skills
cd ~/workspace/ai-agent/ore-skills

# 既定はstable
bash scripts/install.sh --target=claude --channel=stable
bash scripts/doctor.sh --channel=stable
```

配置先は `~/.claude/skills/<name>/` です。symlinkなので、リポジトリを `git pull` すると内容が反映されます。試験中のスキルが必要な場合だけ `--channel=experimental` または `--channel=all` を明示します。

## Windsurfと併用する

同じcloneからまとめて配布できます。

```bash
bash scripts/install.sh --channel=stable
bash scripts/doctor.sh --channel=stable
```

## 使い方

Claude Codeは `SKILL.md` の `description` を読み、タスクに合うスキルを選択します。認識されない場合は次を確認します。

1. Claude Codeで新しいセッションを開始する。
2. `bash scripts/doctor.sh --channel=stable` を実行する。
3. `~/.claude/skills/<name>/SKILL.md` が解決できることを確認する。
4. frontmatterの `name` とディレクトリ名が一致することを確認する。

## MCPとの境界

通常の知識・手順はSkillで配布します。MCPは外部サービス、認証、動的データなど実行時接続が必要な能力だけに使用し、Python実装があるという理由だけではMCP化しません。

詳細は [usage_patterns.md](usage_patterns.md) を参照してください。
