# 日記フォーマット仕様

## Frontmatter

すべての日記エントリは以下の YAML frontmatter を持つ。

```yaml
---
date: YYYY-MM-DD
tags:
  - type/journal
  - status/idea
  - topic/xxx        # 内容に応じて 1〜3 個
created: YYYY-MM-DDTHH:MM:SS+09:00
---
```

### タグルール

| プレフィックス | 説明 | 例 |
|---|---|---|
| `type/` | 固定: `journal` | `type/journal` |
| `status/` | 固定: `idea`（Inbox に入るため） | `status/idea` |
| `topic/` | 内容から推定。1〜3 個 | `topic/ai`, `topic/career`, `topic/rust` |

## 本文構造

```markdown
# YYYY-MM-DD — タイトル

## 今日あったこと
（ユーザーの言葉ベースの本文。事実の記録。）

## 感じたこと
（感情・気づき・内省。）

## 技術メモ
（技術的な話題があった場合のみ表示。調査結果のサマリーやリンクを含む。）

## 次のアクション
（あれば。なければこのセクション自体を省略。）
```

### セクションルール

- **「今日あったこと」と「感じたこと」は必須**。最低限この 2 つがあれば日記として成立する。
- **「技術メモ」は任意**。Phase 2 で技術リサーチを行った場合のみ含める。
- **「次のアクション」は任意**。Phase 3 でアクションが出た場合のみ含める。
- 空のセクションは作らない。

## ファイル名

```
YYYY-MM-DD_<slug>.md
```

- `<slug>`: タイトルからローマ字 or 英語で短く生成（ハイフン区切り、小文字）
- 例: `2026-04-04_ai-agent-potential.md`
