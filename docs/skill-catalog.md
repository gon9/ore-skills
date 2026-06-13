# Skill Catalog

このファイルは `scripts/generate-skill-catalog.py` で自動生成されます。手動編集せず、由来などの補助情報は `docs/skill-catalog.toml` を更新してください。

## ステータス凡例

- `実装済`: `skills/` に `SKILL.md` が存在し、配布対象として扱う

## 現在のカタログ

| スキル名 | ステータス | 由来 | 構成 | description |
|---|---|---|---|---|
| [context-optimizer](../skills/context-optimizer/SKILL.md) | 実装済 | context-engineering | markdown | Use this skill to compress long conversation threads into a compact checkpoint summary. Use when the session is getting long, the user says "チェックポイント作って", "これまでの内容まとめて", "context compaction", "セッションまとめて", or when important decisions and code changes risk being lost. Extracts decisions, code changes, TODOs, and learnings into a reusable Markdown document. |
| [diary](../skills/diary/SKILL.md) | 実装済 | 新規作成 | python, scripts, references | Interactive diary writing assistant that guides users through journal entries using interview-style questions. Supports technical research when topics require investigation. Use when the user wants to write a diary, journal entry, or daily reflection. |
| [git-workflow](../skills/git-workflow/SKILL.md) | 実装済 | git-convention | markdown | Use this skill when creating git commit messages, branch names, or pull request descriptions. Generates Conventional Commits-compliant messages, kebab-case branch names with feature/fix/docs/ prefixes, and structured PR templates. Use when the user says "commit", "コミット", "PR作って", "ブランチ作って", "コミットメッセージ考えて", or when staged changes need to be committed, even if they don't explicitly mention Conventional Commits. |
| [media](../skills/media/SKILL.md) | 実装済 | 既存・手動抽出 | python, references | Fetches and processes YouTube video transcripts for analysis, summarization, and content extraction. Use when working with YouTube videos, video transcripts, or when the user mentions YouTube, video content analysis, or transcript extraction. |
| [obsidian-triage](../skills/obsidian-triage/SKILL.md) | 実装済 | obsidian | markdown | Use this skill to organize, sort, or triage notes in an Obsidian vault inbox. Use when the user wants to clean up their inbox (00_Inbox), categorize notes, suggest appropriate folders or tags, or move notes to their permanent location. Triggers on keywords: Obsidian整理, 受信箱, inbox triage, ノート整理, vault整理, 00_Inbox, 積んでるノート, even if they don't explicitly mention Obsidian. |
| [obsidian-utils](../skills/obsidian-utils/SKILL.md) | 実装済 | 既存・手動抽出 | python | Manage and update personal indexes in an Obsidian Vault. Use to automatically compile index links from a vault directory into a single note. |
| [pptx](../skills/pptx/SKILL.md) | 実装済 | Anthropic公式参考 | python, scripts, references | Generate PowerPoint presentations (.pptx) using Node.js and PptxGenJS. Use this skill any time a .pptx file needs to be created, read, edited, or analyzed. Triggers on keywords: deck, slides, presentation, pptx, スライド, プレゼン, 発表資料. |
| [prompt-linter](../skills/prompt-linter/SKILL.md) | 実装済 | prompt-patterns | markdown | Use this skill to review, diagnose, or improve AI prompts. Use when the user wants to analyze a prompt for clarity, check if it uses best practices (defensive prompting, few-shot examples, output format constraints, role assignment), or when a prompt isn't working as expected. Triggers on keywords: プロンプト改善, プロンプト診断, prompt review, プロンプトエンジニアリング, プロンプトが効かない, system prompt, few-shot. |
| [rules-generator](../skills/rules-generator/SKILL.md) | 実装済 | rules-files | python, references | プロジェクトのソースコード・依存関係・ディレクトリ構造を解析し、AGENTS.md を生成する。新規プロジェクトのセットアップ時、または既存の AGENTS.md の品質チェック・更新時に使用する。 |
| [spec](../skills/spec/SKILL.md) | 実装済 | workflow-patterns | python, references | Validates specification documents to ensure they contain required sections (概要, 要件, 構成). Use when checking design documents, specification files, or when the user mentions spec validation, document format checking, or requirements verification. |
| [task-splitter](../skills/task-splitter/SKILL.md) | 実装済 | workflow-patterns | markdown | Use this skill to decompose large features, epics, or complex requirements into small atomic tasks (10-15 minutes each). Use when the user has a big feature to build, wants to create Linear issues, needs a sprint plan, or says "タスク分解して", "issueに切って", "どこから始めればいい", "小さく分けて", even if they don't explicitly mention task decomposition. |
| [video-summary](../skills/video-summary/SKILL.md) | 実装済 | 既存・手動抽出 | scripts, references | Extracts audio from video files, transcribes speech using Whisper API, and summarizes the content. Use when the user wants to summarize a video, transcribe audio, or extract key points from video content. |
| [youtube-summary](../skills/youtube-summary/SKILL.md) | 実装済 | 既存・手動抽出 | python | Extracts YouTube video transcripts and manages fallback to whisper-based transcription. Use when you need to summarize or extract text from a YouTube video. |

## 新規スキルの追加プロセス

1. `scripts/create-skill.sh` で最小雛形を生成する
2. 必要な場合だけ `--python` または `--resources=` を指定する
3. `SKILL.md` を agentskills.io 仕様に従って執筆する
4. `python3 scripts/validate-skills.py --strict` を実行する
5. `python3 scripts/generate-skill-catalog.py` で本カタログを更新する
