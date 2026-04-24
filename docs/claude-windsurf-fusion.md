# Claude Code × Windsurf 融合戦略

## エグゼクティブサマリー

Claude Code と Windsurf は**競合ではなく補完関係**にある。両者の強みを理解し、ore-skills を「どちらからでも最大限に活用できる共通スキル基盤」として再設計することで、開発者体験を劇的に向上させる。

**結論: ore-skills は "Write Once, Run Anywhere for AI Agents" を実現するハブになる。**

---

## 1. 両者の本質的な違い

### Claude Code: ターミナルネイティブなエージェント

| 特性 | 詳細 |
|------|------|
| **実行環境** | ターミナル（IDE非依存） |
| **モデル** | Claude 専用（Opus/Sonnet 切替可能） |
| **拡張軸** | CLAUDE.md, Skills, Subagents, Hooks, Agent Teams, Plugins |
| **固有の強み** | サブエージェント（Explore/Plan/汎用）、Agent Teams（複数セッション並列）、Hooks（確定的スクリプト）、Git worktree isolation |
| **スキル起動** | `/skill-name` (スラッシュコマンド) |
| **スキル配置** | `~/.claude/skills/` (Personal), `.claude/skills/` (Project) |
| **MCP** | サポート（stdio + SSE） |
| **コンテキスト管理** | Compaction（自動要約）、`context: fork` でサブエージェント分離 |

### Windsurf (Cascade): AI-First IDE

| 特性 | 詳細 |
|------|------|
| **実行環境** | VS Code フォーク IDE |
| **モデル** | マルチモデル（Claude, GPT, 等） |
| **拡張軸** | Skills, Workflows, MCP, Memories |
| **固有の強み** | リアルタイムコード補完、IDE統合（ファイルツリー、ターミナル、プレビュー）、Memories（永続的学習）、ブラウザプレビュー |
| **スキル起動** | `@skill-name` (メンション) or 自動起動 |
| **スキル配置** | `~/.codeium/windsurf/skills/` (Global), `.windsurf/skills/` (Workspace) |
| **MCP** | サポート（stdio） |
| **コンテキスト管理** | IDE コンテキスト自動収集、アクティブファイル連動 |

---

## 2. 補完関係マトリクス — なぜ融合が必要か

```
┌─────────────────────────────────────────────────────────────────┐
│                    開発ワークフロー全体                           │
│                                                                 │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │     Windsurf          │    │    Claude Code        │          │
│  │                      │    │                      │          │
│  │  • コード編集         │    │  • 大規模リファクタ   │          │
│  │  • UI/UX作業          │    │  • 複雑な調査・分析   │          │
│  │  • クイック修正        │    │  • CI/CD統合          │          │
│  │  • プレビュー確認     │    │  • マルチエージェント │          │
│  │  • リアルタイム補完   │    │  • バッチ処理         │          │
│  │                      │    │  • Git操作            │          │
│  └──────────┬───────────┘    └──────────┬───────────┘          │
│             │                           │                       │
│             └─────────┬─────────────────┘                       │
│                       │                                         │
│              ┌────────▼────────┐                                │
│              │   ore-skills    │                                │
│              │  (共通スキル基盤) │                                │
│              │                 │                                │
│              │  • SKILL.md     │                                │
│              │  • references/  │                                │
│              │  • scripts/     │                                │
│              │  • MCP Server   │                                │
│              └─────────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

### 使い分けの原則

| シナリオ | 最適ツール | 理由 |
|---------|-----------|------|
| **IDE内でのコーディング** | Windsurf | リアルタイム補完、ファイルツリー統合 |
| **複雑な調査・設計** | Claude Code | サブエージェント分離、Agent Teams |
| **日記・ドキュメント作成** | どちらでもOK | ore-skills で同一スキル |
| **CI/CDパイプライン** | Claude Code | ターミナルネイティブ、Hooks |
| **プロトタイプ作成** | Windsurf | ブラウザプレビュー、デプロイ |
| **大規模リファクタリング** | Claude Code | worktree isolation、Agent Teams |
| **コードレビュー** | Claude Code | サブエージェント（Explore + Plan） |
| **クイック修正・デバッグ** | Windsurf | IDE統合、即座のフィードバック |

---

## 3. 融合アーキテクチャ — 4層モデル

### Layer 1: 共通スキル基盤 (SKILL.md — 現状維持・拡張)

agentskills.io 仕様準拠の SKILL.md は**両方で動く唯一の共通フォーマット**。これが融合の核。

```
skills/<name>/
├── SKILL.md              # 共通エントリーポイント (agentskills.io準拠)
├── references/           # 詳細ドキュメント (Progressive Disclosure)
├── scripts/              # 確定的ロジック (両環境で実行可能)
├── src/<name>/           # Python実装
└── tests/
```

**拡張ポイント: SKILL.md frontmatter のツール固有フィールド活用**

```yaml
---
name: diary
description: Interactive diary writing assistant...
# === 共通フィールド (agentskills.io) ===
license: MIT
compatibility: Python 3.12+
metadata:
  author: gon9a
  version: "1.0"
# === Claude Code 固有 (Windsurfでは無視される) ===
context: fork              # サブエージェントで実行
effort: high               # 推論の深さ
disable-model-invocation: false
# === Windsurf 固有 (Claude Codeでは無視される) ===
# (現時点では追加フィールドなし — descriptionで制御)
---
```

**重要**: 両ツールとも未知のfrontmatterフィールドは無視する。つまり**1つのSKILL.mdに両方の設定を混在させても安全**。

### Layer 2: ツール固有設定レイヤー

各ツール固有の設定ファイルは分離して管理する。

```
ore-skills/
├── .claude/                  # Claude Code 固有
│   ├── settings.json         # permission rules等
│   ├── agents/               # サブエージェント定義
│   │   ├── researcher.md     # 調査特化エージェント
│   │   ├── reviewer.md       # コードレビューエージェント
│   │   └── planner.md        # 計画立案エージェント
│   └── rules/                # パス別ルール
│       └── skills.md         # skills/ 編集時のルール
├── .windsurf/                # Windsurf 固有
│   └── workflows/            # Windsurf ワークフロー
│       ├── review.md
│       └── update-spec.md
├── CLAUDE.md                 # Claude Code のプロジェクトルール
└── AGENTS.md                 # ベンダー非依存の共通ルール
```

### Layer 3: MCP Server (ツール非依存のAPI層)

MCP はClaude CodeもWindsurfもサポートしている**唯一の共通プロトコル**。

```
ore-skills-server (stdio/SSE)
    │
    ├── Claude Desktop → stdio
    ├── Claude Code    → stdio / MCP設定
    ├── Windsurf       → stdio / mcp_config.json
    └── その他MCPクライアント → SSE (リモート)
```

**融合における役割**: スキルのPython実装をMCP経由で公開することで、SKILL.md（インストラクション層）とは別に、**プログラマブルなツール層**を提供する。

### Layer 4: AGENTS.md (ベンダー非依存ルール)

`AGENTS.md` はベンダー非依存の新標準。CLAUDE.md の内容を AGENTS.md に移行しつつ、Claude Code固有の設定は CLAUDE.md に残す。

```
AGENTS.md (共通ルール)
├── プロジェクト概要
├── 技術スタック
├── コーディング規約
├── テスト方針
└── アーキテクチャ概要

CLAUDE.md (Claude Code固有)
├── サブエージェント利用方針
├── Hooks設定の参照
├── Agent Teams パターン
└── Permission設定
```

---

## 4. Claude Code でしかできないこと — ore-skills への活用

### 4.1 サブエージェント (Subagents)

Claude Code 最大の差別化要素。**隔離されたコンテキストで専門タスクを実行**し、結果のみを返す。

**ore-skills への提案: スキルごとにサブエージェント定義を同梱**

```
skills/diary/
├── SKILL.md
├── .claude/
│   └── agents/
│       └── diary-researcher.md   # 日記の技術トピック調査用
└── references/
```

```markdown
# .claude/agents/diary-researcher.md
---
description: 日記に出てきた技術トピックを調査する
model: haiku
tools:
  - WebSearch
  - Read
  - Grep
maxTurns: 5
effort: medium
---
日記の技術トピックについて簡潔に調査し、以下の形式で報告する:
- 概要（2-3文）
- 公式ドキュメントURL
- ore-skills のどのスキルと関連するか
```

### 4.2 Hooks (確定的スクリプト実行)

**LLMの推論ループの外**で確定的なスクリプトを実行する仕組み。

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write|Edit",
      "command": "scripts/check-skill-health.sh $SKILL_NAME"
    }],
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "command": "uv run ruff check --fix src/ tests/"
    }]
  }
}
```

**ore-skills への提案**: `scripts/` 内のスクリプトをHooksから呼べるように整備。

### 4.3 Agent Teams (マルチエージェント協調)

複数のClaude Codeセッションが**ピアツーピアでメッセージング**しながら並列作業。

**ore-skills への提案**: 大規模タスク（例: 全スキルのagentskills.io準拠チェック）をAgent Teamsで分散実行。

---

## 5. Windsurf でしかできないこと — ore-skills への活用

### 5.1 Memories (永続的学習)

Windsurfはセッションを跨いで学習した情報を永続化する。ore-skillsの使い方パターンを自動学習。

### 5.2 ブラウザプレビュー & デプロイ

Webアプリのプレビューとデプロイが統合されている。pptxスキルやデモUIの確認に最適。

### 5.3 Workflows (.windsurf/workflows/)

Windsurf固有のワークフロー定義。`/review` や `/update-spec` のような定型作業を自動化。

**重要**: これらは `.windsurf/workflows/` に配置され、Claude Codeからは見えない。逆にClaude Codeのサブエージェント定義は `.claude/agents/` に配置され、Windsurfからは見えない。**互いの領域を侵さない設計**。

---

## 6. 具体的アクションプラン

### Phase 1: 共通基盤の強化 (即座に実施)

- [ ] **AGENTS.md の作成**: ベンダー非依存のプロジェクトルールを記述
- [ ] **CLAUDE.md の作成**: Claude Code 固有の設定（サブエージェント方針、Hooks等）
- [ ] **統合セットアップスクリプトの改善**: `scripts/setup-all.sh` — Windsurf と Claude Code の両方を一括セットアップ

### Phase 2: Claude Code 固有機能の活用 (1-2週間)

- [ ] **サブエージェント定義の追加**: `.claude/agents/` に調査・レビュー・計画エージェントを配置
- [ ] **Hooks の設定**: ruff自動実行、スキルヘルスチェック
- [ ] **SKILL.md の Claude Code 固有フィールド追加**: `context`, `effort`, `disable-model-invocation`

### Phase 3: ワークフローの分業最適化 (2-4週間)

- [ ] **タスク種別→ツール選択ガイドの作成**: どのタスクでどちらを使うか明文化
- [ ] **スキルカタログ候補の実装分担**: 
  - `context-optimizer` → Claude Code (サブエージェント活用)
  - `rules-generator` → Claude Code (codebase調査にExploreエージェント)
  - `task-splitter` → 共通 (SKILL.md)
  - `prompt-linter` → 共通 (SKILL.md + scripts/)

### Phase 4: 高度な統合 (1ヶ月以上)

- [ ] **ore-skills を Claude Code Plugin として配布**: Plugin marketplace への公開検討
- [ ] **Agent Teams パターンの確立**: 複数スキル連携の自動化
- [ ] **Windsurf Memories と Claude Code CLAUDE.md の知見同期**: 片方で学んだルールをもう片方にも反映する運用フロー

---

## 7. ディレクトリ構造 — 融合後の最終形

```
ore-skills/
├── AGENTS.md                     # ★ NEW: ベンダー非依存ルール
├── CLAUDE.md                     # ★ NEW: Claude Code固有ルール
├── .claude/                      # ★ NEW: Claude Code固有設定
│   ├── agents/                   #   サブエージェント定義
│   │   ├── researcher.md         #   調査特化
│   │   ├── reviewer.md           #   コードレビュー特化
│   │   └── skill-builder.md      #   新スキル作成支援
│   ├── rules/                    #   パス別ルール
│   │   └── skills.md             #   skills/ 編集時の追加ルール
│   └── settings.json             #   Hooks, Permissions
├── .windsurf/                    # Windsurf固有設定 (既存)
│   ├── skills/                   #   → setup-windsurf.sh で生成
│   └── workflows/                #   Windsurf ワークフロー
│       ├── review.md
│       └── update-spec.md
├── skills/                       # 共通スキル基盤 (変更なし)
│   ├── common/
│   ├── diary/
│   ├── media/
│   ├── obsidian_utils/
│   ├── pptx/
│   ├── spec/
│   └── youtube_summary/
├── servers/                      # MCP Server (変更なし)
│   └── ore-skills-server/
├── scripts/                      # 共通スクリプト
│   ├── setup-windsurf.sh
│   ├── setup-claude-code.sh
│   ├── setup-all.sh              # ★ NEW: 両方一括セットアップ
│   ├── check-skill-health.sh
│   ├── create-skill.sh
│   └── update-skills.sh
└── docs/
    ├── claude-windsurf-fusion.md  # ★ このドキュメント
    ├── claude_code_integration.md
    ├── windsurf_integration.md
    └── ...
```

---

## 8. 設計原則 — 3つのルール

### Rule 1: SKILL.md は唯一の真実 (Single Source of Truth)

スキルの定義は `skills/<name>/SKILL.md` の1箇所のみ。Windsurf と Claude Code の両方がここを参照する。ツール固有のfrontmatterフィールドは同じファイルに共存させる。

### Rule 2: ツール固有設定は専用ディレクトリに隔離

- `.claude/` — Claude Code 専用（サブエージェント、Hooks、ルール）
- `.windsurf/` — Windsurf 専用（ワークフロー）
- 相互に干渉しない。片方を使っていなくてもエラーにならない。

### Rule 3: MCP は最大公約数

Claude Desktop, Claude Code, Windsurf のすべてがMCPをサポートしている。Python実装を持つスキルは必ず MCP Server 経由でもアクセスできるようにする。これにより「Skills非対応のクライアント」からも利用可能になる。

---

## 9. まとめ

| 観点 | 現状 | 融合後 |
|------|------|--------|
| **スキル管理** | SKILL.md (共通) ✅ | 変更なし — すでに正しい |
| **ツール固有設定** | `.windsurf/` のみ | `.claude/` + `.windsurf/` 並列 |
| **プロジェクトルール** | なし | AGENTS.md (共通) + CLAUDE.md (固有) |
| **サブエージェント** | 未活用 | `.claude/agents/` で専門エージェント |
| **Hooks** | 未活用 | ruff自動実行、ヘルスチェック |
| **MCP** | stdio実装済 | 変更なし — すでに正しい |
| **セットアップ** | 個別スクリプト | `setup-all.sh` で一括化 |

**ore-skills の現在のアーキテクチャは、融合の土台としてすでに非常に良い状態にある。** agentskills.io 準拠の SKILL.md が共通基盤として機能しており、あとは Claude Code 固有の強力な機能（サブエージェント、Hooks、Agent Teams）を **追加** するだけで、両ツールの能力を最大限に引き出せる。
