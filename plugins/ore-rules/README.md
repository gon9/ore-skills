# ore-rules

gon9a の**共通開発規約**を Devin の always-on ルールとして配布する plugin バンドル。

`plugins/ore-skills-stable`（Codex 向けスキル束）と同じ考え方で、こちらは
**ルールだけ**を Devin に配る。スキルは含まない。

## なぜリポジトリ直下ではなくサブフォルダなのか

Devin の plugin は **plugin root の `AGENTS.md` を always-on ルールとして自動ロードする**。
ore-skills 直下を plugin root にすると、リポジトリ自身のプロジェクトルール
（`/AGENTS.md` = 「ore-skills をどう開発するか」）が、無関係なプロジェクトの
セッションにまで注入されてしまう。

サブフォルダに分けることで、配布するのは `rules/` 配下の共通規約だけになる。

## 収録ルール

| ファイル | 内容 |
|---|---|
| `python-standards.md` | Python 3.12 / uv / ruff / pytest、ruff→pytest の実行順序 |
| `code-quality.md` | ハードコーディング禁止、日本語 Docstring、正常系・異常系テスト |
| `secrets-direnv.md` | direnv + `.envrc`。`.env` は作らない |
| `git-conventions.md` | ブランチ prefix、Conventional Commits、commit 前の branch 確認 |
| `dev-environment.md` | Docker で統一、ローカルを汚さない、スモールスタート |
| `architecture-defaults.md` | FastAPI / REST+OpenAPI / **LLM はモデル名を固定せず選定基準で書く** |
| `project-governance.md` | Linear が正典、lane:1/2/3、ready label、CI で自動実行 |
| `model-routing.md` | Fusion 型のモデル配分（指揮はフロンティア、サブエージェントは安価階層）とコンテキスト予算 |

すべて `trigger: always_on`。

## インストール

```bash
devin plugins install https://github.com/gon9/ore-skills.git#plugins/ore-rules
```

## Devin UI 側との関係

同じ8本が Devin の Organization Rules（Customize → Rules）にも手入力されている。
**このリポジトリを正典とし、UI 側は複製として扱う。**
内容を変えるときはここを直して plugin を更新し、UI 側の手編集はしない。

> 進行状態・担当・blocker は Linear だけが持つ。規約の本文はこのリポジトリだけが持つ。
> — 「正典を一つに決め、二重に持たない」

## 元ネタ

`~/.claude/CLAUDE.md`（グローバル設定、git 管理外）から起こした。
将来的にはこのリポジトリを正典にして、`~/.claude/CLAUDE.md` を symlink に
置き換えるのが望ましい。
