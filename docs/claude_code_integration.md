# Claude Code との統合

## 概要

ore-skills は **agentskills.io 仕様に準拠** しているため、Claude Code の **Skills 機能** とネイティブに統合できます。

Claude Code は以下の場所から Skills を自動検出します：
- **Personal Skills**: `~/.claude/skills/<skill-name>/`
- **Project Skills**: `.claude/skills/<skill-name>/`

SKILL.md の形式は Windsurf と完全互換です。同じ ore-skills のクローンから両方に統合できます。

## Windsurf との比較

| | Windsurf | Claude Code |
|--|----------|-------------|
| **Global/Personal** | `~/.codeium/windsurf/skills/<name>/` | `~/.claude/skills/<name>/` |
| **Workspace/Project** | `.windsurf/skills/<name>/` | `.claude/skills/<name>/` |
| **SKILL.md形式** | agentskills.io 準拠 | agentskills.io 準拠（同一） |
| **自動起動** | `description` に基づき自動判断 | `description` に基づき自動判断 |
| **手動起動** | `@skill-name` | `/skill-name` |
| **セットアップスクリプト** | `scripts/setup-windsurf.sh` | `scripts/setup-claude-code.sh` |

## 統合方法

### 方法1: セットアップスクリプト（推奨）

`scripts/setup-claude-code.sh` を使って自動セットアップできます。

#### 動作の概要

スクリプトは実行場所に応じて自動的に動作を切り替えます:

- **ore-skills リポジトリ内で実行** → Personal Skills として自動統合（循環防止のため Project は不可）
- **外部プロジェクトのルートで実行** → Personal / Project を選択可能

#### 使い方

```bash
# パターン A: Personal Skills（ore-skills を直接クローンした場合）
~/ore-skills/scripts/setup-claude-code.sh

# パターン B: Project Skills（ore-skills をサブモジュールとして追加した場合）
cd /path/to/your-project
./.ore-skills/scripts/setup-claude-code.sh
# → 「2) Project Skills」を選択
```

### 方法2: シンボリックリンク（手動）

#### Personal Skills として統合

```bash
# ore-skills をクローン
git clone https://github.com/gon9/ore-skills.git ~/ore-skills

# Personal Skills ディレクトリを作成
mkdir -p ~/.claude/skills

# 各スキルをシンボリックリンク
ln -s ~/ore-skills/skills/media ~/.claude/skills/media
ln -s ~/ore-skills/skills/spec ~/.claude/skills/spec
ln -s ~/ore-skills/skills/diary ~/.claude/skills/diary
```

#### Project Skills として統合

```bash
# プロジェクトに ore-skills を追加
cd /path/to/your-project
git submodule add https://github.com/gon9/ore-skills.git .ore-skills
git submodule update --init --recursive

# .claude/skills ディレクトリを作成
mkdir -p .claude/skills

# 各スキルをシンボリックリンク
ln -s ../../.ore-skills/skills/media .claude/skills/media
ln -s ../../.ore-skills/skills/spec .claude/skills/spec
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
├── .claude/
│   └── skills/
│       ├── media -> ../../.ore-skills/skills/media
│       └── spec -> ../../.ore-skills/skills/spec
└── your_code/
```

### 方法3: 手動コピー

シンボリックリンクが使えない環境では、手動でコピーします。

```bash
# Personal Skills としてコピー
mkdir -p ~/.claude/skills
cp -r ~/ore-skills/skills/media ~/.claude/skills/
cp -r ~/ore-skills/skills/spec ~/.claude/skills/

# Project Skills としてコピー
mkdir -p .claude/skills
cp -r .ore-skills/skills/media .claude/skills/
cp -r .ore-skills/skills/spec .claude/skills/
```

**注意:** コピーの場合、ore-skills の更新を反映するには再度コピーが必要です。

## Windsurf と Claude Code の両方で使う

ore-skills のクローンは1つで両方に対応できます：

```bash
# 1回クローンするだけ
git clone https://github.com/gon9/ore-skills.git ~/ore-skills

# Windsurf に統合
~/ore-skills/scripts/setup-windsurf.sh

# Claude Code に統合
~/ore-skills/scripts/setup-claude-code.sh
```

スキルを更新する際も `git pull` 一回で両方に反映されます（シンボリックリンクのため）。

## Claude Code での使い方

### 自動起動

Claude Code は SKILL.md の `description` を読んで、適切なタイミングで自動的にスキルを起動します。

```
User: YouTubeの動画の文字起こしを取得して
Claude: [media スキルを自動起動]
```

### 手動起動（/コマンド）

```
/media YouTubeの動画 dQw4w9WgXcQ の文字起こしを取得して
```

### インストール済みスキルの確認

```bash
ls ~/.claude/skills/
```

## トラブルシューティング

### Skills が認識されない

1. Claude Code のセッションを再起動（新しいセッションを開始）
2. `SKILL.md` が正しいパスにあるか確認: `ls ~/.claude/skills/<name>/SKILL.md`
3. シンボリックリンクが正しいか確認: `ls -la ~/.claude/skills/`

### よくあるミス

- ディレクトリが二重にネストされている: `~/.claude/skills/skill-name/another-folder/SKILL.md` ではなく `~/.claude/skills/skill-name/SKILL.md`
- `SKILL.md` が存在しないフォルダは無視される

## 推奨構成

| 用途 | 推奨方法 |
|------|---------|
| **個人開発** | Personal Skills + シンボリックリンク |
| **チーム開発** | Project Skills + Git Submodule |
| **Windsurf と併用** | 両方のセットアップスクリプトを実行 |
