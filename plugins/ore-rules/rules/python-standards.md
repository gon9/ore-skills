---
description: "Python プロジェクトの言語バージョン・ツールチェーン・ruff/pytest の実行順序"
trigger: always_on
---

## 言語・ツールチェーン

- **Python は最新の stable を使う。** 特定バージョンをここに固定しない
- パッケージマネージャは `uv`（pip / poetry は使わない）
- Linter / Formatter は `ruff`
- テストフレームワークは `pytest`
- Dockerfile はマルチステージビルドにする

### バージョンは規約でなくプロジェクトで固定する

**規約にバージョン番号を書くと陳腐化する。** 実際この規約は「3.12 を使う」と書いたまま
放置され、2026-09-21 時点で owlclaw は 1 リポジトリの中で 4 つの Python が動いていた。

| 場所 | 実際のバージョン |
|---|---|
| CI | 3.12.3（未固定・runner の `/usr/bin/python3`） |
| ローカル | 3.12.11 |
| 本番 venv | 3.14.5 |
| 本番の常駐サービス | 3.12.4（pyenv） |

`requires-python = ">=3.12"` は**下限しか決めない**ので、環境ごとに違うものが選ばれる。
patch リリースにはセキュリティ修正が入るため、古い patch に固まるのは避ける。

各プロジェクトで次の3つを揃える。

- `.python-version` に最新 stable を **patch まで**書く（`uv python pin <version>`）
- `pyproject.toml` の `requires-python` をその minor に合わせる
- CI でも同じものを使う（`.python-version` を読ませる。runner 既定の python を使わない）

### uv 自体も更新する

**uv が古いと、新しい Python の stable を知らない。** `uv python install 3.14` が
beta を掴むことがある（ローカルの uv 0.7.13 が 3.14.0b2 を入れた。stable の
3.14.7 は 0.12.17 で初めて見えた）。バージョンを上げる前に `uv` を上げること。

```bash
brew upgrade uv     # または uv self update
uv python install <latest-stable>
uv python pin <latest-stable>
```

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
