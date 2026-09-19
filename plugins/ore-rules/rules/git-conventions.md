---
description: "Git 規約（ブランチ名 / Conventional Commits / commit 前の branch 確認）と対話言語"
trigger: always_on
---

## Git 規約

- ブランチ名は `feature/` `fix/` `docs/` プレフィックスを使う
- コミットメッセージは Conventional Commits 準拠
- **commit 直前に毎回 `git branch --show-current` を叩く。** 現在の branch / worktree を自分専用と推定しない

## リポジトリ構成

- Codex 等の他 AI ツール向けには、プロジェクトの `CLAUDE.md` から `AGENTS.md` へ
  シンボリックリンクを張る（規約の実体は1ファイルに保つ）

## コミュニケーション

- ユーザーとの対話は日本語で行う
- 調査・リサーチは英語ソースも含めて実施する
