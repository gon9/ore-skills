# ルールファイル テンプレート

生成するルールファイルの雛形。プロジェクト解析結果で `{{...}}` を置き換える。

---

## CLAUDE.md / AGENTS.md テンプレート

```markdown
# {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}

## 技術スタック

- **言語**: {{LANGUAGE}} {{LANGUAGE_VERSION}}
- **フレームワーク**: {{FRAMEWORK}}
- **パッケージマネージャ**: {{PACKAGE_MANAGER}}
- **Linter / Formatter**: {{LINTER}}
- **テストフレームワーク**: {{TEST_FRAMEWORK}}
- **コンテナ**: {{CONTAINER}} (該当する場合)

## ディレクトリ構成

```
{{DIRECTORY_TREE}}
```

各ディレクトリの役割:
- `{{SRC_DIR}}/` — {{SRC_DESCRIPTION}}
- `{{TEST_DIR}}/` — {{TEST_DESCRIPTION}}

## コーディング規約

- {{LINTER}} の設定に従うこと
- {{NAMING_CONVENTION}}
- Docstring は {{DOCSTRING_LANG}} で記述すること
- import は常にファイルの先頭に配置すること

## テスト

- テストフレームワーク: {{TEST_FRAMEWORK}}
- テスト実行コマンド: `{{TEST_COMMAND}}`
- Lint 実行コマンド: `{{LINT_COMMAND}}`
- **順序: Lint → テスト** (Lint が clean になってからテストを実行すること)

## エラーハンドリング

- 例外は適切な粒度でキャッチし、握りつぶさないこと
- ログは {{LOG_FORMAT}} を推奨
- API エラーレスポンスは統一フォーマットを使用すること

## Git 規約

- ブランチ: `feature/`, `fix/`, `docs/` プレフィックス
- コミットメッセージ: Conventional Commits 準拠
- `.env` は `.gitignore` に含め、`.env.example` を提供すること

## 禁止事項

- ハードコーディング禁止（API キー、URL、マジックナンバー等）
- `any` 型の使用禁止 (TypeScript の場合)
- テストなしでのマージ禁止
- {{ADDITIONAL_CONSTRAINTS}}
```

---

## スタック別の追加ルール例

### Python (uv + ruff + pytest)

```markdown
## Python 固有ルール

- パッケージマネージャは uv を使用すること（pip 直接使用禁止）
- コードを書いたら必ず `uv run ruff check --fix` を pytest より先に実行すること
- pytest は ruff が clean になってから実行すること
- よく発生する ruff エラーと対処:
  * W293: 空行に空白文字 → 空行は完全に空にする
  * F401: 未使用 import → import は必要なものだけ書く
  * UP028: for+yield は yield from に置き換える
- 型ヒントを必ず付けること（`def func(x: int) -> str:`）
- Dockerfile はマルチステージビルドを使用すること
```

### Node.js / TypeScript (React + TailwindCSS)

```markdown
## フロントエンド固有ルール

- コンポーネントは関数コンポーネントで実装すること（クラスコンポーネント禁止）
- スタイリングは TailwindCSS のユーティリティクラスを使用すること（CSS ファイル禁止）
- `useEffect` の依存配列は必ず正確に指定すること
- API 呼び出しは専用の hooks (`useQuery`, `useMutation`) を使用すること
- `console.log` はデバッグ完了後に必ず削除すること
```

### Go

```markdown
## Go 固有ルール

- エラーは必ずチェックすること（`_ = err` 禁止）
- `go fmt` と `go vet` を CI で必ず実行すること
- パッケージ名は短く、小文字のみ使用すること
- インタフェースは利用側で定義すること（Accept interfaces, return structs）
```

### Rust

```markdown
## Rust 固有ルール

- `unwrap()` は本番コードで使用禁止（テストコードのみ許可）
- `clippy` の警告はすべて解消すること
- `unsafe` ブロックにはコメントで安全性の根拠を記述すること
```

---

## Progressive Disclosure の分割例

ルートファイルが 200 行を超える場合、以下のように分割する:

```
project/
├── CLAUDE.md                  # 概要 + 技術スタック + 基本規約
├── .claude/
│   └── rules/
│       ├── testing.md         # テスト方針の詳細
│       ├── api-design.md      # API 設計のルール
│       └── deployment.md      # デプロイ手順
```

ルートの `CLAUDE.md` には概要だけを書き、詳細は分割ファイルへの参照を記述する:

```markdown
## 詳細ルール

- テスト方針: `.claude/rules/testing.md` を参照
- API 設計: `.claude/rules/api-design.md` を参照
- デプロイ: `.claude/rules/deployment.md` を参照
```
