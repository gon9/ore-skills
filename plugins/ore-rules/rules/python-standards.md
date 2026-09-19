---
description: "Python プロジェクトの言語バージョン・ツールチェーン・ruff/pytest の実行順序"
trigger: always_on
---

## 言語・ツールチェーン

- Python 3.12 を使う
- パッケージマネージャは `uv`（pip / poetry は使わない）
- Linter / Formatter は `ruff`
- テストフレームワークは `pytest`
- Dockerfile はマルチステージビルドにする

## 実行規律

コードを書いたら必ずこの順序で実行する:

1. `uv run ruff check --fix src/ tests/`
2. `uv run pytest`（ruff が clean になってから）

テストファイルも同様に ruff check を通すこと。
コミット前チェックリスト: ruff clean → pytest 全パス → git commit

## よく出るエラーと対処

- `W293` 空行に空白文字 → 空行は完全に空にする（スペース・タブ禁止）
- `F401` 未使用 import → 必要なものだけ import し、書いたら必ず使う
- `UP028` `for` + `yield` → `yield from` に置き換える
