# Skills Operations Review 2026-07

調査日: 2026-07-02 JST

この文書は、ore-skills のこれまでの活動、Agent Skills 周辺の最新動向、会社の複数メンバーで skills を管理する場合に足りない要素をまとめる。

## 1. これまでの活動の振り返り

ore-skills は、最初は `media` / `spec` などの個別スキルを置くモノレポとして始まり、現在は複数エージェントに同じ `SKILL.md` を配る共通基盤に寄っている。

主な流れ:

| 時期 | 方向性 | 具体化されたもの |
|---|---|---|
| 初期 | スキル実装の集約 | `skills/` 配下に `SKILL.md` と実装を置く構造 |
| Progressive Disclosure 化 | 起動時のコンテキストを軽くする | `SKILL.md` / `references/` / `scripts/` の分離 |
| agentskills.io 準拠 | ベンダー非依存化 | `validate-skills.py`, `skill-catalog.md`, `CONTRIBUTING.md` |
| Windsurf / Claude Code 統合 | 実際のエージェントで使える配置 | `docs/windsurf_integration.md`, `docs/claude_code_integration.md` |
| グローバル symlink 配布 | 各作業リポジトリを汚さない | `scripts/install.sh`, `doctor.sh`, `uninstall.sh` |
| cross-agent 化 | Codex / Antigravity / Devin なども見据える | `~/.agents/skills` を共通配布面として明示 |

技術判断としては、各プロジェクトへ submodule を置く方式から、ホームディレクトリ配下のグローバル symlink 方式へ寄せたのが大きい。これは Obsidian / Google Drive / IDE の Source Control と gitlink が衝突しやすいという実運用上の事故を避けるためで、今後も基本方針として維持する。

## 2. 最新動向

### 2.1 Open standard と Progressive Disclosure が中心

[Agent Skills specification](https://agentskills.io/specification) は、skill を `SKILL.md` 必須、`scripts/` / `references/` / `assets/` 任意のディレクトリとして定義している。`name` と `description` は必須で、`description` は「何をするか」と「いつ使うか」を明示する必要がある。

重要なのは、skill 全体を常に読み込ませるのではなく、まず `name` / `description` だけで候補にし、必要になった時だけ `SKILL.md` と関連ファイルを読む設計である。この repo の現行構造はこの方向と合っている。

### 2.2 Codex は skills を「ワークフロー authoring」、plugins を「配布単位」として分けている

[Codex Agent Skills](https://developers.openai.com/codex/skills) では、skills は reusable workflow の authoring format、plugins は他の開発者へ配る installable distribution unit と整理されている。つまり、ローカルや repo 内で workflow を育てる段階は skill、複数人や組織に配る段階は plugin 化を検討する流れになる。

Codex 側では次の点も重要:

- skills は Codex CLI / IDE extension / Codex app で利用される
- 初期 skill 一覧はコンテキスト予算を持ち、多数の skill があると description が短縮・省略され得る
- implicit invocation は `description` に強く依存する
- `$skill-creator` と Record & Replay により、実演や対話から skill を起こす流れが用意されている
- `agents/openai.yaml` で表示情報、暗黙起動ポリシー、MCP 依存などを補足できる

また [openai/skills](https://github.com/openai/skills) は deprecated になり、現在の Codex skill / plugin examples は [openai/plugins](https://github.com/openai/plugins) を見る流れに変わっている。ore-skills も、長期的には「単体 skill 群」だけでなく「配布用 plugin bundle」を設計対象に含める必要がある。

### 2.3 Claude Code は open standard を採用しつつ、独自拡張を持つ

[Claude Code skills](https://code.claude.com/docs/en/skills) は Agent Skills open standard に従いつつ、invocation control、subagent execution、dynamic context injection などの独自拡張を持つ。配置場所も enterprise / personal / project / plugin の階層があり、優先順位や nested skill の挙動が定義されている。

ore-skills への示唆:

- 共通 `SKILL.md` は標準フィールド中心に保つ
- Claude 固有フィールドは使えるが、他エージェントへの影響を明示する
- monorepo では package 単位の nested skills も候補になる
- skill が大きくなったら plugin 化や provider-specific metadata へ逃がす

### 2.4 研究動向は「自動生成・評価・安全性」に寄っている

2026年の研究では、skill を人間が手書きするだけでなく、実行結果から改善する方向が出ている。[CoEvoSkills](https://arxiv.org/abs/2604.01687) は skill generator と verifier を組み合わせて、複数ファイル skill package を反復改善する枠組みを提案している。

一方で、[malicious agent skills の大規模調査](https://arxiv.org/abs/2602.06547) は、第三者 skill がユーザー権限で実行され、認証情報窃取や agent 操作につながるリスクを示している。会社で運用する場合、便利さより先に provenance、review、permission、sandbox、依存管理を設計する必要がある。

## 3. 複数メンバー運用で足りない要素

現在の ore-skills は個人利用や少人数の直接編集には十分だが、会社の複数メンバーで管理するには次が不足している。

| 不足要素 | 現状 | 必要な状態 |
|---|---|---|
| Ownership | skill ごとの責任者がない | `CODEOWNERS` か `docs/skill-owners.md` で owner / reviewer を明示 |
| Release 管理 | `git pull` 前提 | versioned release、CHANGELOG、互換性ポリシーを持つ |
| Review 基準 | `CONTRIBUTING.md` 中心 | skill PR checklist、security review、eval evidence を必須化 |
| 評価 | frontmatter validation と pytest 中心 | activation test、sample prompts、golden outputs、regression eval を追加 |
| Security | `.env` 禁止など基本ルール中心 | third-party skill intake、script permission、dependency pinning、secret scan を追加 |
| 配布単位 | symlink 配布中心 | local authoring と organization distribution を分離し、plugin bundle を検討 |
| 互換性 | Claude / Windsurf / cross-agent の説明あり | Codex / Claude / Windsurf / Cursor / Antigravity / Devin の compatibility matrix を継続更新 |
| 変更通知 | docs と git log 依存 | release note と migration guide を用意 |
| Deprecation | 削除時の扱いが弱い | deprecated status、sunset date、代替 skill を catalog に持つ |
| Observability | doctor は symlink 診断中心 | install 状態、実行失敗、使用頻度、false activation を収集する |

## 4. 会社運用の推奨設計

### 4.1 リポジトリ構造

既存構造は維持しつつ、運用メタデータを追加する。

```text
docs/
├── skill-owners.md
├── skill-release-policy.md
├── skill-security-review.md
├── skill-evaluation.md
└── agent-compatibility.md
```

`docs/agent-compatibility.md` はすでにあるので、今後は各エージェントの対応状況、制約、検証日を表で持つとよい。

### 4.2 Skill ごとの必須メタデータ

`SKILL.md` の標準フィールドを壊さず、`metadata` に社内管理情報を入れる。

```yaml
metadata:
  owner: platform-ai
  status: stable
  reviewed_at: "2026-07-02"
  compatible_agents: "codex, claude-code, windsurf"
  risk: low
```

配布チャネルは `docs/skill-catalog.toml` の `channel` を正本とし、`stable` と `experimental` の2段階に揃える。廃止予定やriskなどの運用情報は別フィールドで管理する。`risk` は、外部通信、ファイル変更、secret参照、任意コマンド実行の有無で決める。

### 4.3 PR チェック

skill 追加・変更 PR は最低限これを要求する。

- `python3 scripts/validate-skills.py --strict`
- `python3 scripts/generate-skill-catalog.py --check`
- `bash scripts/check-skill-health.sh`
- scripts を含む場合は最小単位のテスト
- sample prompt と expected behavior
- third-party dependency の有無とライセンス確認
- secret / credential / network access の有無

### 4.4 配布戦略

現行の `scripts/install.sh` によるsymlink配布と、Codex向けstable Plugin配布を次の2段階で使い分ける。

| 段階 | 配布方法 | 用途 |
|---|---|---|
| Authoring | repo clone + symlink | skill 開発者、レビュー担当 |
| Organization distribution | `ore-skills-stable` Pluginまたは社内registry | 一般メンバー、安定版配布 |

Codexではpluginが配布単位になっているため、`plugins/ore-skills-stable/` は単体配布できるcoreスキルだけを収録する。将来bundleが増えた場合も、`ore-skills` 全体を一括配布せず用途別に分ける。

### 4.5 セキュリティ方針

会社利用では、skill は「プロンプト」ではなく「実行可能な運用部品」として扱う。

- 外部から取り込む skill はそのまま入れない
- scripts 付き skill はコードレビュー必須
- network / filesystem / secret に触る skill は risk を上げる
- dependencies は lock か最小バージョン制約を持つ
- `allowed-tools` や provider-specific permission は便利だが、対応エージェント差分を明記する
- 社内 secret 名、顧客名、private endpoint を `SKILL.md` に直書きしない

## 5. 優先ロードマップ

### Phase 1: 管理情報を足す

- `docs/skill-owners.md` を作る
- `docs/skill-release-policy.md` を作る
- `docs/skill-security-review.md` を作る
- `docs/agent-compatibility.md` に検証日とエージェント別制約を足す

### Phase 2: 評価を自動化する

- skill ごとに `tests/prompts/` または `examples/` を置く
- description が正しく trigger するかを評価する
- scripts 付き skill の deterministic path を pytest 対象にする
- false activation / missed activation を issue template で収集する

### Phase 3: 配布を分ける（実装済み）

- 開発者向けは symlink のまま維持
- `stable` / `experimental` のチャネルをcatalogで管理する
- 一般利用者向けにstable core skillsだけをbundle化する
- Codex向けにteam marketplaceと `ore-skills-stable` Pluginを提供する
- Claude / Windsurf / Cursor / Antigravity / Devin は compatibility matrix で追随する

## 6. 結論

ore-skills の方向性は、最新の Agent Skills 動向と合っている。特に `SKILL.md` を核にした Progressive Disclosure、`scripts/` への確定処理分離、`~/.agents/skills` への cross-agent 配布は妥当である。

次に必要なのは、新しい skill を増やすことよりも、会社で壊れずに増やせる governance である。owner、release、security review、eval、compatibility matrix、distribution boundary を docs に追加すれば、個人の便利ツールからチームの運用基盤へ移行できる。
