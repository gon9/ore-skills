---
name: git-workflow
description: Use this skill when creating git commit messages, branch names, or pull request descriptions. Generates Conventional Commits-compliant messages, kebab-case branch names with feature/fix/docs/ prefixes, and structured PR templates. Use when the user says "commit", "コミット", "PR作って", "ブランチ作って", "コミットメッセージ考えて", or when staged changes need to be committed, even if they don't explicitly mention Conventional Commits.
license: MIT
metadata:
  author: gon9a
  version: "1.0"
---

# Git Workflow Skill

Conventional Commits 準拠の git 操作をサポートするスキル。

## コミットメッセージ生成

### フォーマット

```
<type>(<scope>): <subject>

<body> (任意)

<footer> (任意)
```

### type 一覧

| type | 用途 |
|------|------|
| `feat` | 新機能 |
| `fix` | バグ修正 |
| `docs` | ドキュメントのみの変更 |
| `refactor` | リファクタリング（機能変更なし） |
| `test` | テスト追加・修正 |
| `chore` | ビルドツール・依存関係・設定等の変更 |
| `perf` | パフォーマンス改善 |
| `ci` | CI/CD の変更 |

### scope（任意）

変更箇所を括弧内に記述する。例: `skills`, `scripts`, `docs`, `api`, `ui`

### subject の規則

- 命令形（過去形・現在進行形は避ける）
- 先頭大文字不要
- 末尾ピリオドなし
- 50文字以内
- 英語推奨（body は日本語 OK）

### 例

```
feat(skills): add git-workflow skill for commit generation

fix(install): resolve dangling symlink on Cursor target

docs: update CONTRIBUTING.md with script best practices

chore(deps): bump ruff to 0.15.1
```

## ブランチ命名

```
<prefix>/<kebab-case-description>
```

| prefix | 用途 |
|--------|------|
| `feature/` | 新機能 |
| `fix/` | バグ修正 |
| `docs/` | ドキュメント |
| `refactor/` | リファクタリング |
| `chore/` | 設定・依存関係 |

例:
```
feature/add-git-workflow-skill
fix/resolve-symlink-dangling
docs/update-contributing-guidelines
```

## PR Description テンプレート

ユーザーが PR description を求めた場合、以下の構造で生成する:

```markdown
## 概要
[このPRの目的を1-2文で説明]

## 変更内容
- [ ] [変更点1]
- [ ] [変更点2]

## 動作確認
- `[確認コマンド]`: ✅ 成功 / ❌ 失敗

## 関連 Issue / チケット
- Closes #[issue番号]
```

## ワークフロー

1. `git diff --staged` でステージングされた変更を確認する
2. 変更の種別・スコープを判定する
3. subject を生成する（50文字以内）
4. body が必要かを判断する（破壊的変更・背景説明が必要な場合）
5. ユーザーに提示して確認する
6. OKなら `git commit -m "..."` を実行する

## Gotchas

- 絵文字は使わない（Gitmoji 不使用）
- `BREAKING CHANGE:` は footer に記載し、subject に `!` を付ける（例: `feat!: ...`）
- body と footer は空行で区切る
- 複数の変更を1コミットにまとめない（atomic commits）
- ステージングされていない変更は `git add` を提案してから進める
