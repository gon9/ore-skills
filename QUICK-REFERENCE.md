# ore-skills Quick Reference

このリポジトリは、コーディングエージェント（AIアシスタント）のベストプラクティスを集約した「ナレッジベース」と、それを具体化した「スキル群」を提供するモノレポです。

`scripts/install.sh` でグローバル位置 (`~/.agents/skills/`, `~/.claude/skills/`, `~/.codeium/windsurf/skills/`) に symlink を張ると、どのプロジェクトでも Windsurf / Claude Code 等からこの skill 群が見えるようになります。

> Git Submodule で他リポジトリに組み込む方式は **非推奨** に変更しました (Obsidian vault 上の git 同期と Antigravity の Source Control が壊れる事故が再現したため)。詳細は README.md 参照。

## 📚 1. Knowledge Base (`docs/knowledge/`)
コーディングエージェントを使いこなすためのベストプラクティス集です。
プロジェクト固有の `CLAUDE.md` や `.cursorrules` を作成・チューニングする際のベースラインとして活用してください。

- [Context Engineering](docs/knowledge/context-engineering.md)
- [Rules & Instructions Files](docs/knowledge/rules-files.md)
- [Prompt Patterns](docs/knowledge/prompt-patterns.md)
- [Workflow Patterns](docs/knowledge/workflow-patterns.md)
- [Tool Integration (MCP/Skills)](docs/knowledge/tool-integration.md)

## 🔧 2. Available Skills (`skills/`)
各ディレクトリ内の `SKILL.md` をAIエージェントに読み取らせることで、プロジェクト固有の機能として活用できます。

| スキル | 説明 |
|-------|------|
| [media](skills/media/SKILL.md) | YouTube文字起こし等のメディア処理 |
| [spec](skills/spec/SKILL.md) | 要件定義・基本設計・API仕様書のフォーマット検証 |
| [obsidian-utils](skills/obsidian-utils/SKILL.md) | Obsidian Vault のインデックス（MOC）を自動更新 |
| [youtube-summary](skills/youtube-summary/SKILL.md) | yt-dlp/whisper フォールバック付きのYouTube文字起こし |
| [video-summary](skills/video-summary/README.md) | （開発中）動画コンテンツの要約・抽出 |

★ 今後の実装予定（候補）リストは [Skill Catalog](docs/skill-catalog.md) を参照してください。

## 🔄 最新化とメンテナンス

```bash
# ore-skills を更新する (symlink 経由なのでこれだけで全エージェントに反映)
git -C ~/workspace/ai-agent/ore-skills pull

# 現状診断 (dangling symlink などを検知)
bash ~/workspace/ai-agent/ore-skills/scripts/doctor.sh
```
