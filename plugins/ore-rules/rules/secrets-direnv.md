---
description: "シークレット・環境変数の管理（direnv + .envrc。.env は作らない）"
trigger: always_on
---

## シークレット / 環境変数管理（direnv）

- 環境変数・API キーは **direnv + `.envrc`** で管理する
- **`.env` ファイルは作らない / 提案しない**
- 新しいシークレットが必要になったら `.envrc` に `export KEY=...` を追記し、ユーザーに `direnv allow` の実行を促す
- `.envrc` と `.direnv/` はグローバル gitignore で除外済み。リポジトリにコミットしない
- `.env.example` 相当が必要な場合は `.envrc.example`（値はダミー）を用意してコミットする
- コード内では通常どおり `os.environ["OPENAI_API_KEY"]` / `process.env.OPENAI_API_KEY` で読む（direnv が自動ロードする）
- API キーをコードにハードコーディングしない
