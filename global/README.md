# global — マシン全体に効く設定の正典

`~/.claude/CLAUDE.md`（Claude Code のユーザースコープ設定）の**中身**をここで版管理する。

## 設計

規約の本文は **1か所にだけ**置き、各ツールはそこを参照する。

```
plugins/ore-rules/rules/*.md   ← 共通規約（7本）= 正典
        ├─ Devin      : plugin として install（always_on ルール）
        └─ Claude Code: ~/.claude/CLAUDE.md から @import

global/claude-code/*.md        ← Claude Code 固有（/clear・スキル・サブエージェント）
        └─ Claude Code: ~/.claude/CLAUDE.md から @import
```

`~/.claude/CLAUDE.md` 自身は **import を並べただけの薄いインデックス**にする。
本文を持たないので、このリポジトリを直せば両方のツールに反映される。

## なぜ symlink にしないのか

`~/.claude/CLAUDE.md` を symlink にすると、**Cowork セッションでスキップされる**。

> In Cowork sessions on your desktop, Claude Code ... skips a `~/.claude/CLAUDE.md`
> that is itself a symlink or hard link
> — [Claude Code docs / memory](https://code.claude.com/docs/en/memory)

そのため実体ファイルのまま残し、中身を `@path` import にする。
user-scope のファイルからの import は承認ダイアログなしで読み込まれる。

**既知の制約**: Cowork セッションでは、作業ディレクトリ外を指す import もスキップされる。
Cowork を使う場合、これらの規約は効かない。

## セットアップ（新しい Mac / 再構築時）

1. このリポジトリを `~/workspace/ai-agent/ore-skills` に clone する
2. `~/.claude/CLAUDE.md` を以下の内容で作成する（パスは clone 先に合わせる）

```markdown
# グローバルルール

共通の開発規約は ore-skills リポジトリを正典とする。
このファイルは import を並べるだけで、本文を持たない。
規約を変えるときは ore-skills 側を直すこと。

https://github.com/gon9/ore-skills

## 共通規約（Devin にも plugin として配布される）

@~/workspace/ai-agent/ore-skills/plugins/ore-rules/rules/dev-environment.md
@~/workspace/ai-agent/ore-skills/plugins/ore-rules/rules/secrets-direnv.md
@~/workspace/ai-agent/ore-skills/plugins/ore-rules/rules/python-standards.md
@~/workspace/ai-agent/ore-skills/plugins/ore-rules/rules/code-quality.md
@~/workspace/ai-agent/ore-skills/plugins/ore-rules/rules/git-conventions.md
@~/workspace/ai-agent/ore-skills/plugins/ore-rules/rules/architecture-defaults.md
@~/workspace/ai-agent/ore-skills/plugins/ore-rules/rules/project-governance.md

## Claude Code 固有

@~/workspace/ai-agent/ore-skills/global/claude-code/context-separation.md
```

3. Devin 側は plugin を install する

```bash
devin plugins install https://github.com/gon9/ore-skills.git#plugins/ore-rules
```

## 確認方法

Claude Code の新しいセッションで `/memory` を実行し、7本の共通規約と
`context-separation.md` が展開されていることを確認する。
