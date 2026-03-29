# ore-skills Quick Reference

このリポジトリは、コーディングエージェント（AIアシスタント）のベストプラクティスを集約した「ナレッジベース」と、それを具体化した「スキル群」を提供するモノレポです。

Git Submodule として他のプロジェクトに組み込むことで、AIエージェントに高度なコンテキストとツールセットを提供します。

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
| [obsidian_utils](skills/obsidian_utils/SKILL.md) | Obsidian Vault のインデックス（MOC）を自動更新 |
| [youtube_summary](skills/youtube_summary/SKILL.md) | yt-dlp/whisper フォールバック付きのYouTube文字起こし |
| [video_summary](skills/video_summary/README.md) | （開発中）動画コンテンツの要約・抽出 |

★ 今後の実装予定（候補）リストは [Skill Catalog](docs/skill-catalog.md) を参照してください。

## 🔄 最新化とメンテナンス

他のプロジェクトで `.ore-skills` として組み込んでいる場合、定期的に以下のコマンドで最新のベストプラクティスとスキルを取得してください。

```bash
# サブモジュールの更新
git submodule update --remote .ore-skills
```
