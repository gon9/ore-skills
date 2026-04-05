# Contributing to ore-skills

ore-skills へのコントリビュートありがとうございます！このドキュメントでは、新しいスキルを追加する際のガイドラインを説明します。

## 目次

- [新しいスキルの追加](#新しいスキルの追加)
- [agentskills.io 仕様への準拠](#agentskillsio-仕様への準拠)
- [コーディング規約](#コーディング規約)
- [テスト](#テスト)
- [プルリクエストのプロセス](#プルリクエストのプロセス)

## 新しいスキルの追加

### 1. ディレクトリ構成

新しいスキルは `skills/` ディレクトリ配下に作成してください。

```bash
skills/
└── your-skill-name/          # スキル名（小文字英数字とハイフンのみ）
    ├── pyproject.toml        # パッケージ定義
    ├── SKILL.md              # スキルの説明（必須）
    ├── references/           # 詳細ドキュメント（オプション）
    │   └── REFERENCE.md
    ├── scripts/              # 実行可能スクリプト（オプション）
    ├── src/                  # 実装コード
    │   └── your_skill_name/
    │       ├── __init__.py
    │       └── main.py
    └── tests/                # テストコード
        └── test_main.py
```

### 2. スキル名の命名規則

**agentskills.io 仕様に準拠:**

- 1-64文字
- 小文字英数字とハイフン (`a-z`, `-`) のみ
- ハイフンで開始・終了不可
- 連続ハイフン (`--`) 不可
- **ディレクトリ名と `SKILL.md` の `name` フィールドが一致必須**

✅ **良い例:**
- `pdf-processing`
- `data-analysis`
- `code-review`

❌ **悪い例:**
- `PDF-Processing` (大文字不可)
- `-pdf` (ハイフンで開始不可)
- `pdf--processing` (連続ハイフン不可)

### 3. SKILL.md の作成（必須）

すべてのスキルには `SKILL.md` が必要です。

```markdown
---
name: your-skill-name
description: このスキルが何をするか、いつ使うかを明確に記述。AIが発見しやすい具体的なキーワードを含めること。
license: MIT
compatibility: Python 3.12+
metadata:
  author: your-name
  version: "1.0"
---

# Your Skill Name

## Overview
スキルの機能の簡潔な説明。

## Capabilities
- **機能A**: 説明。詳細は [references/feature-a.md](references/feature-a.md) を参照。
- **機能B**: 説明。

## Usage
### 機能Aの使い方
ステップバイステップの手順:
1. 入力データを準備
2. スクリプトを実行: `uv run -m your_skill_name.main`
3. 出力を確認

例:
\`\`\`bash
uv run -m your_skill_name.main --input data.json
\`\`\`

## References
- [API Reference](references/REFERENCE.md)
```

#### SKILL.md の要件

- **Frontmatter (必須)**:
  - `name`: スキル名（ディレクトリ名と一致）
  - `description`: 1-1024文字、「何をするか」と「いつ使うか」を含む
  
- **Body Content (< 5000 tokens 推奨)**:
  - ステップバイステップの手順
  - 入出力の例
  - よくあるエッジケース
  - 詳細ドキュメントへのリンク

### 4. pyproject.toml の設定

```toml
[project]
name = "your-skill-name"
version = "0.1.0"
description = "Your skill description"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "common",
    # 必要な外部依存関係を追加
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/your_skill_name"]

[tool.uv.sources]
common = { workspace = true }
```

### 5. ルートの pyproject.toml を更新

新しいスキルを追加したら、ルートの `pyproject.toml` を更新してください:

```toml
[tool.uv.sources]
common = { workspace = true }
media = { workspace = true }
spec = { workspace = true }
your-skill-name = { workspace = true }  # 追加

[dependency-groups]
dev = [
    "common",
    "media",
    "spec",
    "your-skill-name",  # 追加
    "mypy>=1.19.1",
    "pytest>=9.0.2",
    "ruff>=0.15.1",
]
```

## agentskills.io 仕様への準拠

### 仕様の自動アップデート（AIワークフロー）

ore-skills は AI自身が最新の動向を調査し、リポジトリをアップデートできる自律的なワークフローを備えています。
仕様の変更が疑われる場合や、定期的なメンテナンスとして、Windsurf 上で以下のコマンドをAIに指示してください。

```text
/update-spec
```

このコマンドにより、AIは最新の `agentskills.io` の仕様やベストプラクティスをWeb検索し、必要に応じて `CONTRIBUTING.md` や既存スキルの `SKILL.md`、チェックツール群を自律的にアップデートする計画を提案・実行します。

### 検証ツールの使用

PRを出す前に、必ず `skills-ref` ツールで検証してください:

```bash
# skills-ref のインストール
npm install -g @agentskills/skills-ref

# スキルの検証
skills-ref validate ./skills/your-skill-name
```

### Progressive Disclosure の実践

- **Level 1 (Metadata)**: `name` と `description` は ~100 tokens
- **Level 2 (Instructions)**: `SKILL.md` の本文は < 5000 tokens 推奨
- **Level 3 (Resources)**: 詳細は `references/` に分離

## コーディング規約

### Python コード

- **バージョン**: Python 3.12+
- **Linter/Formatter**: `ruff`
- **Docstring**: 日本語で記述
- **型ヒント**: 可能な限り使用

```python
def process_data(input_path: str, output_path: str) -> dict[str, any]:
    """
    データを処理します。
    
    Args:
        input_path (str): 入力ファイルのパス
        output_path (str): 出力ファイルのパス
        
    Returns:
        dict[str, any]: 処理結果
        
    Raises:
        FileNotFoundError: 入力ファイルが見つからない場合
    """
    pass
```

### コードフォーマット

PRを出す前に、必ず `ruff` でフォーマットしてください:

```bash
# フォーマットチェック
uv run ruff check .

# 自動修正
uv run ruff check --fix .

# フォーマット適用
uv run ruff format .
```

## テスト

### テストの作成（必須）

すべての新機能には、正常系と異常系のテストを作成してください。

```python
# tests/test_main.py
import pytest
from your_skill_name.main import process_data

def test_process_data_success():
    """正常系: データ処理が成功する"""
    result = process_data("input.json", "output.json")
    assert result["status"] == "success"

def test_process_data_file_not_found():
    """異常系: ファイルが見つからない場合"""
    with pytest.raises(FileNotFoundError):
        process_data("nonexistent.json", "output.json")
```

### テストの実行

```bash
# すべてのテストを実行
uv run pytest

# 特定のスキルのテストのみ実行
uv run pytest skills/your-skill-name/tests/

# カバレッジ付きで実行
uv run pytest --cov=skills/your-skill-name
```

## プルリクエストのプロセス

### 1. ブランチの作成

```bash
git checkout -b feature/add-your-skill-name
```

### 2. 変更のコミット

コミットメッセージは [Conventional Commits](https://www.conventionalcommits.org/) に従ってください:

```bash
git commit -m "feat(skills): Add your-skill-name for [purpose]

- Implemented core functionality
- Added comprehensive tests
- Created SKILL.md with agentskills.io compliance"
```

### 3. PRを出す前のチェックリスト

- [ ] `skills-ref validate` が成功する
- [ ] `uv run ruff check .` がエラーなし
- [ ] `uv run pytest` がすべて成功
- [ ] `SKILL.md` が agentskills.io 仕様に準拠
- [ ] テストカバレッジが十分（正常系・異常系）
- [ ] ルートの `pyproject.toml` を更新
- [ ] Docstring が日本語で記述されている

### 4. PRの作成

PRテンプレート:

```markdown
## 概要
このPRは [目的] のために [スキル名] を追加します。

## 変更内容
- [ ] 新しいスキル `your-skill-name` を追加
- [ ] SKILL.md を作成（agentskills.io 準拠）
- [ ] テストを追加（正常系・異常系）
- [ ] ドキュメントを更新

## 検証
- `skills-ref validate ./skills/your-skill-name`: ✅ 成功
- `uv run pytest`: ✅ すべて成功
- `uv run ruff check .`: ✅ エラーなし

## スクリーンショット（該当する場合）
```

### 5. レビュー対応

- レビューコメントには迅速に対応してください
- 変更を求められた場合は、同じブランチにコミットを追加してください
- レビュー完了後、メンテナーがマージします

## 質問・サポート

質問がある場合は、以下の方法でお問い合わせください:

- GitHub Issues: バグ報告や機能リクエスト
- GitHub Discussions: 一般的な質問や議論

## ライセンス

このプロジェクトに貢献することで、あなたのコントリビューションが MIT ライセンスの下でライセンスされることに同意したものとみなされます。
