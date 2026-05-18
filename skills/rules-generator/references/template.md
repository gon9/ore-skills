# ルールファイル テンプレート

生成するルールファイルの雛形。プロジェクト解析結果で `{{...}}` を置き換える。

---

## AGENTS.md テンプレート

```markdown
# Project Rules — {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION（1-3行）}}

## コマンド

```bash
{{BUILD_COMMAND}}       # ビルド
{{LINT_COMMAND}}        # Lint
{{FORMAT_COMMAND}}      # Format
{{TEST_COMMAND}}        # テスト
```

## 技術スタック

- **言語**: {{LANGUAGE}} {{LANGUAGE_VERSION}}
- **フレームワーク**: {{FRAMEWORK}}
- **パッケージマネージャ**: {{PACKAGE_MANAGER}}

## ディレクトリ構造

```
{{DIRECTORY_TREE}}
```

## コーディング規約

- {{LINTER}} の設定に従うこと
- {{NAMING_CONVENTION}}
- Docstring / コメントは日本語で記述すること

## 境界 (Boundaries)

### Always
- Lint が clean になってからテストを実行すること
- {{ALWAYS_RULES}}

### Ask First
- 新しい依存パッケージの追加
- {{ASK_FIRST_RULES}}

### Never
- `.env` にシークレットを直接書く
- {{NEVER_RULES}}

## Git 規約

- コミットメッセージは日本語で簡潔に
- `.env` は `.gitignore` に含め、`.env.example` を提供すること
```

---

## スタック別の Boundaries 例

### Python (uv + ruff + pytest)

```markdown
### Always
- ruff が clean になるまで pytest を実行しないこと
- 型ヒントを必ず付けること

### Never
- グローバルパッケージのインストール（uv を使用）
- `any` 型の使用
```

### Node.js / TypeScript (React)

```markdown
### Always
- 関数コンポーネントで実装すること

### Ask First
- 新しい npm パッケージの追加

### Never
- `console.log` を本番コードに残す
- クラスコンポーネントの使用
```

### Unity (C#)

```markdown
### Always
- SerializeField に [Header] を付与
- ScriptableObject でデータ駆動設計を維持

### Ask First
- 新しい Singleton の追加
- GameState フローの変更

### Never
- Update() 内で Find 系メソッドを使用
- DontDestroyOnLoad は GameManager 以外で使用しない
```

### Go

```markdown
### Always
- エラーは必ずチェックすること

### Never
- `_ = err` (エラー握りつぶし)
- `unsafe` パッケージの使用
```

### Rust

```markdown
### Always
- clippy の警告を全て解消

### Never
- 本番コードで `unwrap()` を使用
- `unsafe` ブロックにコメントなしで使用
```

---

## Progressive Disclosure の分割例

150行を超える場合:

```
project/
├── AGENTS.md              # 概要 + コマンド + 境界 (150行以内)
└── docs/agents/
    ├── architecture.md    # アーキテクチャ詳細
    ├── testing.md         # テスト方針詳細
    └── api-design.md      # API 設計ルール
```

AGENTS.md には概要だけ書き、詳細は参照:

```markdown
## 詳細

- テスト方針: `docs/agents/testing.md` を参照
- API 設計: `docs/agents/api-design.md` を参照
```
