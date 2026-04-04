# Windsurf との統合

## 概要

ore-skills は **agentskills.io 仕様に準拠** しているため、Windsurf の **Skills 機能** とネイティブに統合できます。

Windsurf は以下の場所から Skills を自動検出します：
- **Workspace Skills**: `.windsurf/skills/<skill-name>/`
- **Global Skills**: `~/.codeium/windsurf/skills/<skill-name>/`

## 統合方法

### 方法1: シンボリックリンク（推奨）

ore-skills を Git Submodule として追加し、Windsurf Skills ディレクトリにシンボリックリンクを作成します。

#### Workspace Skills として統合

```bash
# プロジェクトに ore-skills を追加
cd /path/to/your-project
git submodule add https://github.com/gon9/ore-skills.git .ore-skills
git submodule update --init --recursive

# .windsurf/skills ディレクトリを作成
mkdir -p .windsurf/skills

# 各スキルをシンボリックリンク
ln -s ../../.ore-skills/skills/media .windsurf/skills/media
ln -s ../../.ore-skills/skills/spec .windsurf/skills/spec
```

**プロジェクト構成:**
```
your-project/
├── .ore-skills/              # Git submodule
│   └── skills/
│       ├── media/
│       │   ├── SKILL.md
│       │   └── references/
│       └── spec/
├── .windsurf/
│   └── skills/
│       ├── media -> ../../.ore-skills/skills/media
│       └── spec -> ../../.ore-skills/skills/spec
└── your_code/
```

#### Global Skills として統合

すべてのプロジェクトで ore-skills を使いたい場合：

```bash
# ore-skills をクローン
git clone https://github.com/gon9/ore-skills.git ~/ore-skills

# Global Skills ディレクトリを作成
mkdir -p ~/.codeium/windsurf/skills

# 各スキルをシンボリックリンク
ln -s ~/ore-skills/skills/media ~/.codeium/windsurf/skills/media
ln -s ~/ore-skills/skills/spec ~/.codeium/windsurf/skills/spec
```

### 方法2: セットアップスクリプト

ore-skills リポジトリにセットアップスクリプトを追加します。

#### `scripts/setup-windsurf.sh`

```bash
#!/bin/bash
set -e

# ore-skills を Windsurf Skills として統合するセットアップスクリプト

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORE_SKILLS_ROOT="$(dirname "$SCRIPT_DIR")"

# 統合タイプを選択
echo "ore-skills を Windsurf Skills として統合します"
echo ""
echo "統合タイプを選択してください:"
echo "1) Workspace Skills (現在のプロジェクトのみ)"
echo "2) Global Skills (すべてのプロジェクト)"
read -p "選択 (1 or 2): " choice

case $choice in
  1)
    # Workspace Skills として統合
    if [ ! -d ".git" ]; then
      echo "エラー: Gitリポジトリのルートで実行してください"
      exit 1
    fi
    
    SKILLS_DIR=".windsurf/skills"
    mkdir -p "$SKILLS_DIR"
    
    # ore-skills が submodule かどうかチェック
    if [ -d ".ore-skills" ]; then
      ORE_SKILLS_PATH=".ore-skills/skills"
    else
      echo "ore-skills を Git Submodule として追加しますか? (y/n)"
      read -p "> " add_submodule
      if [ "$add_submodule" = "y" ]; then
        git submodule add https://github.com/gon9/ore-skills.git .ore-skills
        git submodule update --init --recursive
        ORE_SKILLS_PATH=".ore-skills/skills"
      else
        echo "ore-skills のパスを入力してください:"
        read -p "> " ORE_SKILLS_PATH
      fi
    fi
    
    # シンボリックリンクを作成
    for skill in "$ORE_SKILLS_PATH"/*; do
      skill_name=$(basename "$skill")
      if [ "$skill_name" = "common" ]; then
        continue  # common はスキップ
      fi
      
      if [ -d "$skill" ] && [ -f "$skill/SKILL.md" ]; then
        relative_path=$(realpath --relative-to="$SKILLS_DIR" "$skill")
        ln -sf "$relative_path" "$SKILLS_DIR/$skill_name"
        echo "✓ $skill_name をリンクしました"
      fi
    done
    
    echo ""
    echo "✅ Workspace Skills として統合完了"
    echo "Windsurf を再起動してください"
    ;;
    
  2)
    # Global Skills として統合
    SKILLS_DIR="$HOME/.codeium/windsurf/skills"
    mkdir -p "$SKILLS_DIR"
    
    # シンボリックリンクを作成
    for skill in "$ORE_SKILLS_ROOT/skills"/*; do
      skill_name=$(basename "$skill")
      if [ "$skill_name" = "common" ]; then
        continue  # common はスキップ
      fi
      
      if [ -d "$skill" ] && [ -f "$skill/SKILL.md" ]; then
        ln -sf "$skill" "$SKILLS_DIR/$skill_name"
        echo "✓ $skill_name をリンクしました"
      fi
    done
    
    echo ""
    echo "✅ Global Skills として統合完了"
    echo "Windsurf を再起動してください"
    ;;
    
  *)
    echo "無効な選択です"
    exit 1
    ;;
esac
```

#### 使い方

```bash
# ore-skills リポジトリで実行
cd /path/to/ore-skills
chmod +x scripts/setup-windsurf.sh
./scripts/setup-windsurf.sh
```

### 方法3: 手動コピー

シンボリックリンクが使えない環境（Windows等）では、手動でコピーします。

```bash
# Workspace Skills としてコピー
mkdir -p .windsurf/skills
cp -r .ore-skills/skills/media .windsurf/skills/
cp -r .ore-skills/skills/spec .windsurf/skills/

# Global Skills としてコピー
mkdir -p ~/.codeium/windsurf/skills
cp -r ~/ore-skills/skills/media ~/.codeium/windsurf/skills/
cp -r ~/ore-skills/skills/spec ~/.codeium/windsurf/skills/
```

**注意:** コピーの場合、ore-skills の更新を反映するには再度コピーが必要です。

## Windsurf での使い方

### 自動起動

Windsurf は SKILL.md の `description` を読んで、適切なタイミングで自動的にスキルを起動します。

```
User: YouTubeの動画 dQw4w9WgXcQ の文字起こしを取得して
Cascade: [media スキルを自動起動]
```

### 手動起動 (@mention)

```
@media YouTubeの動画 dQw4w9WgXcQ の文字起こしを取得して
```

### Skills 一覧の確認

1. Cascade パネルを開く
2. 右上の三点メニューをクリック
3. `Skills` セクションを選択

## Python コードとしても利用

Windsurf Skills として統合しても、Python コードとして直接 import することも可能です。

```python
# pyproject.toml
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

## MCP Server との併用

Windsurf は **MCP (Model Context Protocol)** もサポートしています。

ore-skills-server を MCP として起動すれば、Windsurf から MCP 経由でも利用できます。

### mcp_config.json

```json
{
  "mcpServers": {
    "ore-skills": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/ore-skills",
        "ore-skills-server"
      ]
    }
  }
}
```

**配置場所:**
- macOS: `~/.codeium/windsurf/mcp_config.json`
- Windows: `%APPDATA%\Codeium\windsurf\mcp_config.json`
- Linux: `~/.codeium/windsurf/mcp_config.json`

## 推奨構成

### 個人開発

**Global Skills + シンボリックリンク**

```bash
git clone https://github.com/gon9/ore-skills.git ~/ore-skills
ln -s ~/ore-skills/skills/media ~/.codeium/windsurf/skills/media
ln -s ~/ore-skills/skills/spec ~/.codeium/windsurf/skills/spec
```

- ✅ すべてのプロジェクトで利用可能
- ✅ ore-skills の更新が自動反映
- ✅ セットアップが簡単

### チーム開発

**Workspace Skills + Git Submodule**

```bash
cd /path/to/your-project
git submodule add https://github.com/gon9/ore-skills.git .ore-skills
mkdir -p .windsurf/skills
ln -s ../../.ore-skills/skills/media .windsurf/skills/media
ln -s ../../.ore-skills/skills/spec .windsurf/skills/spec
git add .windsurf .gitmodules .ore-skills
git commit -m "Add ore-skills as Windsurf Skills"
```

- ✅ チーム全体で同じスキルを共有
- ✅ バージョン管理が容易
- ✅ プロジェクト固有の設定が可能

## 比較表

| 統合方法 | メリット | デメリット | 推奨用途 |
|---------|---------|-----------|---------|
| **Global Skills + シンボリックリンク** | すべてのプロジェクトで利用可能、更新が自動反映 | プロジェクト固有の設定不可 | 個人開発 |
| **Workspace Skills + Git Submodule** | チーム共有、バージョン管理 | プロジェクトごとにセットアップ必要 | チーム開発 |
| **MCP Server** | リモート実行可能、言語非依存 | セットアップが複雑 | リモート環境 |
| **Python Package** | 直接import可能 | Windsurf Skills として使えない | Python開発のみ |

## トラブルシューティング

### Skills が表示されない

1. Windsurf を再起動
2. `SKILL.md` のフロントマターが正しいか確認
3. シンボリックリンクが正しいか確認: `ls -la .windsurf/skills/`

### Skills が起動されない

1. `description` フィールドに具体的なキーワードを含める
2. 手動で `@skill-name` で起動してみる
3. Cascade パネルの三点メニュー → Skills で確認

### シンボリックリンクが作成できない（Windows）

管理者権限で実行するか、手動コピーを使用してください。

```powershell
# 管理者権限で実行
mklink /D .windsurf\skills\media ..\..\ore-skills\skills\media
```

## まとめ

ore-skills は agentskills.io 仕様に準拠しているため、Windsurf の Skills 機能とシームレスに統合できます。

**推奨アプローチ:**
1. **個人開発**: Global Skills + シンボリックリンク
2. **チーム開発**: Workspace Skills + Git Submodule
3. **リモート環境**: MCP Server

これにより、ore-skills を Windsurf から直接利用でき、より使いやすくなります。
