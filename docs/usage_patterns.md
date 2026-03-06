# ore-skills 利用パターン

## 概要
`ore-skills` を他のプロジェクトから利用する方法を説明します。

## 利用パターンの比較

### パターン1: Git Submodule（推奨）
**用途**: 複数のプロジェクトで同じスキルセットを共有したい場合

#### メリット
- スキルの定義（SKILL.md, reference/）とコードを一緒に管理できる
- バージョン管理が容易（特定のコミットに固定可能）
- ローカルでの開発・テストが容易
- Progressive Disclosureの構造をそのまま利用可能

#### デメリット
- サブモジュールの更新が手動（`git submodule update`）
- 初回クローン時に `--recurse-submodules` が必要

#### セットアップ手順

```bash
# プロジェクトルートで ore-skills をサブモジュールとして追加
cd /path/to/your-project
git submodule add https://github.com/gon9/ore-skills.git .ore-skills

# サブモジュールを初期化・更新
git submodule update --init --recursive
```

#### プロジェクト構成例
```
your-project/
├── .ore-skills/          # Git submodule
│   └── skills/
│       ├── media/
│       │   ├── SKILL.md
│       │   └── reference/
│       └── spec/
├── your_code/
└── pyproject.toml
```

#### Pythonパッケージとしての利用

```toml
# your-project/pyproject.toml
[project]
dependencies = [
    "media @ file:///${PROJECT_ROOT}/.ore-skills/skills/media",
    "spec @ file:///${PROJECT_ROOT}/.ore-skills/skills/spec",
]

[tool.uv.sources]
media = { path = ".ore-skills/skills/media", editable = true }
spec = { path = ".ore-skills/skills/spec", editable = true }
```

```python
# your_code/main.py
from media import get_youtube_transcript
from spec import check_spec_file

transcript = get_youtube_transcript("video_id")
```

#### AIエージェント（Claude等）からの利用
AIエージェントは `.ore-skills/skills/*/SKILL.md` を読み込むことで、スキルを発見・利用できます。

---

### パターン2: Python Package（PyPI公開）
**用途**: 広く公開して誰でも利用できるようにしたい場合

#### メリット
- `pip install ore-skills-media` で簡単にインストール可能
- バージョン管理が明確（セマンティックバージョニング）
- 依存関係の解決が自動

#### デメリット
- SKILL.md や reference/ の配置が難しい（パッケージに含める必要がある）
- Progressive Disclosureの構造を維持するには工夫が必要
- 公開・更新の手間がかかる

#### セットアップ（将来的な選択肢）
```bash
pip install ore-skills-media
pip install ore-skills-spec
```

---

### パターン3: MCP Server経由（推奨 for AIエージェント）
**用途**: AIエージェントからのみ利用する場合

#### メリット
- AIエージェントに最適化されたインターフェース
- スキルの実装詳細を隠蔽できる
- リモートサーバーとしても動作可能

#### デメリット
- Python APIとしての直接利用は不可
- MCPクライアント（Claude Desktop等）が必要

#### セットアップ手順

```bash
# ore-skills-server をインストール
cd /path/to/ore-skills
uv sync
```

```json
// Claude Desktop の設定ファイル
// ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
{
  "mcpServers": {
    "ore-skills": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/ore-skills",
        "run",
        "ore-skills-server"
      ]
    }
  }
}
```

---

## 推奨アプローチ

### ケース1: AIエージェント + Python開発の両方で使う
**Git Submodule + MCP Server**

1. プロジェクトに ore-skills をサブモジュールとして追加
2. Python コードからは直接 import
3. AIエージェントには MCP Server 経由で公開

```bash
# サブモジュール追加
git submodule add https://github.com/gon9/ore-skills.git .ore-skills

# MCP Server 起動（開発時）
cd .ore-skills
uv run ore-skills-server
```

### ケース2: AIエージェントのみで使う
**MCP Server のみ**

ore-skills リポジトリをクローンして、MCP Server として起動するだけ。

```bash
git clone https://github.com/gon9/ore-skills.git
cd ore-skills
uv sync
uv run ore-skills-server
```

### ケース3: Python開発のみで使う（AIエージェント不要）
**Git Submodule または pip install（将来）**

現時点では Git Submodule が最適。将来的に PyPI に公開すれば `pip install` も可能。

---

## まとめ

| 利用ケース | 推奨方法 | 理由 |
|-----------|---------|------|
| AI + Python開発 | Git Submodule + MCP | 両方のメリットを享受 |
| AIのみ | MCP Server | シンプル |
| Pythonのみ | Git Submodule | SKILL.md も含めて管理可能 |
| 広く公開 | PyPI（将来） | インストールが容易 |

**現時点での最推奨**: Git Submodule
- Progressive Disclosure の構造を保ったまま利用可能
- バージョン管理が容易
- ローカル開発がスムーズ
