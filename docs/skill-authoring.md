# Skill Authoring Guide

2026-06-13 時点の agentskills.io 仕様と、このリポジトリでの運用方針をまとめる。

## 結論

`SKILL.md` だけの Markdown 中心スキルは有効。ただし、純粋な Markdown ファイルではなく、先頭に YAML frontmatter が必要。

最小構成:

```text
skills/my-skill/
└── SKILL.md
```

最小 `SKILL.md`:

```markdown
---
name: my-skill
description: Does one clear thing. Use when the user asks for that workflow or mentions related keywords.
---

# My Skill

Follow these steps...
```

## 公式仕様の要点

参照元:

- https://agentskills.io/specification
- https://agentskills.io/skill-creation/best-practices
- https://agentskills.io/skill-creation/optimizing-descriptions

必須:

- `SKILL.md` は YAML frontmatter と Markdown 本文で構成する
- `name` は必須
- `description` は必須
- `name` はディレクトリ名と一致させる
- `name` は小文字英数字とハイフンのみを使う
- `description` は「何をするか」と「いつ使うか」を含める

任意:

- `license`
- `compatibility`
- `metadata`
- `allowed-tools`
- `scripts/`
- `references/`
- `assets/`

## Markdown-only でよいケース

次のようなスキルは `SKILL.md` だけでよい。

- 手順、判断基準、レビュー観点を渡すだけで十分
- 毎回の実行に deterministic なコードが不要
- 参照資料が短く、`SKILL.md` に収まる
- スキル本文が 500 行未満で、起動時に読まれても重すぎない

この repo の例:

- `skills/git-workflow`
- `skills/task-splitter`
- `skills/prompt-linter`
- `skills/obsidian-triage`

## scripts/references/assets を足すケース

`scripts/`:

- 同じ処理を毎回コード生成している
- 手順ミスが壊れた成果物につながる
- テスト可能な deterministic 処理にしたい

`references/`:

- 長い仕様、テンプレート、チェックリストがある
- タスクによって読むべき詳細が違う
- `SKILL.md` 本体を短く保ちたい

`assets/`:

- 生成物に使うテンプレート、画像、サンプル、フォントなどがある
- エージェントに読ませる説明ではなく、成果物の材料として使う

## Frontmatter の落とし穴

YAML の未クオート文字列に `: ` を含めると壊れる。

避ける:

```yaml
description: Triggers on keywords: prompt review, system prompt.
compatibility: Requires Node.js. Optional: Python 3.12+.
```

使う:

```yaml
description: "Triggers on keywords: prompt review, system prompt."
compatibility: "Requires Node.js. Optional: Python 3.12+."
```

## この repo の運用

ore-skills は複数エージェント向けスキルの一括置き場として扱う。

- 配置は `skills/<skill-name>/SKILL.md`
- 新規スキル名は hyphen-case にする
- Python 実装がないスキルでは `pyproject.toml` を作らない
- `skills/common/` は内部ライブラリであり、スキルとして登録しない
- 生成先エージェントには `scripts/install.sh` で symlink 配置する
- 新規スキル追加時は `scripts/validate-skills.py` を実行する
- `docs/skill-catalog.md` は自動生成なので直接編集しない

新規作成:

```bash
# Markdown-only skill
scripts/create-skill.sh my-skill "Does one clear thing. Use when that workflow is requested."

# Python 実装付き
scripts/create-skill.sh my-skill "Does one clear thing. Use when that workflow is requested." --python

# 必要な bundled resources だけ追加
scripts/create-skill.sh my-skill "Does one clear thing. Use when that workflow is requested." --resources=references,scripts
```

検証:

```bash
python3 scripts/validate-skills.py
python3 scripts/validate-skills.py --strict
python3 scripts/generate-skill-catalog.py
python3 scripts/generate-skill-catalog.py --check
bash scripts/check-skill-health.sh
uv run pytest
```

`validate-skills.py` の通常モードは、ロード不能な frontmatter 問題を失敗扱いにする。`--strict` は agentskills.io 互換性の警告も失敗扱いにする。

## 移行方針

スキルディレクトリと frontmatter の `name` は hyphen-case に揃える。Python import package は `youtube_summary` のように underscore を使ってよい。
