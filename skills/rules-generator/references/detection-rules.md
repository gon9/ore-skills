# 技術スタック検出ルール

プロジェクト解析時にファイルの存在と内容から技術スタックを検出するためのルール。

## 言語・ランタイム検出

| ファイル | 検出対象 | 抽出情報 |
|---------|---------|---------|
| `pyproject.toml` | Python | `requires-python`, `[tool.ruff]`, `[tool.pytest]`, `[tool.mypy]` |
| `setup.py` / `setup.cfg` | Python (レガシー) | `python_requires`, `install_requires` |
| `package.json` | Node.js | `engines.node`, `dependencies`, `devDependencies`, `scripts` |
| `tsconfig.json` | TypeScript | `target`, `strict`, `module` |
| `Cargo.toml` | Rust | `edition`, `dependencies` |
| `go.mod` | Go | `go` version, `require` |
| `Gemfile` | Ruby | `ruby` version |
| `pom.xml` / `build.gradle` | Java/Kotlin | JDK version, dependencies |

## フレームワーク検出

### Python

| 依存パッケージ | フレームワーク | 追加ルール |
|--------------|--------------|----------|
| `fastapi` | FastAPI | 非同期処理、OpenAPI 自動生成、Pydantic モデル |
| `django` | Django | ORM、テンプレート、admin |
| `flask` | Flask | 軽量、Blueprint |
| `streamlit` | Streamlit | デモ用 UI |

### Node.js / TypeScript

| 依存パッケージ | フレームワーク | 追加ルール |
|--------------|--------------|----------|
| `react` / `next` | React / Next.js | 関数コンポーネント、SSR/SSG |
| `vue` / `nuxt` | Vue / Nuxt | Composition API |
| `svelte` / `@sveltejs/kit` | Svelte / SvelteKit | リアクティブ宣言 |
| `express` | Express | ミドルウェアパターン |

## ツールチェイン検出

### Linter / Formatter

| ファイル | ツール |
|---------|-------|
| `[tool.ruff]` in `pyproject.toml` | ruff |
| `.eslintrc*` / `eslint.config.*` | ESLint |
| `biome.json` | Biome |
| `.prettierrc*` | Prettier |
| `rustfmt.toml` | rustfmt |

### テストフレームワーク

| ファイル / 設定 | ツール | コマンド |
|---------------|-------|---------|
| `[tool.pytest]` in `pyproject.toml` | pytest | `uv run pytest` / `pytest` |
| `jest.config.*` / `"jest"` in `package.json` | Jest | `npm test` / `npx jest` |
| `vitest.config.*` | Vitest | `npx vitest` |
| `_test.go` files | Go testing | `go test ./...` |

### パッケージマネージャ

| ファイル | マネージャ |
|---------|----------|
| `uv.lock` | uv |
| `poetry.lock` | Poetry |
| `Pipfile.lock` | Pipenv |
| `pnpm-lock.yaml` | pnpm |
| `yarn.lock` | Yarn |
| `package-lock.json` | npm |
| `bun.lockb` | Bun |

## CI/CD 検出

| パス | サービス |
|------|---------|
| `.github/workflows/*.yml` | GitHub Actions |
| `.gitlab-ci.yml` | GitLab CI |
| `Jenkinsfile` | Jenkins |
| `.circleci/config.yml` | CircleCI |

## コンテナ検出

| ファイル | 内容 |
|---------|------|
| `Dockerfile` | Docker イメージ定義 |
| `docker-compose.yml` / `compose.yml` | マルチコンテナ構成 |
| `.dockerignore` | ビルドコンテキスト除外設定 |
