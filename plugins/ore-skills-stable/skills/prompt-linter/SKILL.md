---
name: prompt-linter
description: "Use this skill to review, diagnose, or improve AI prompts. Use when the user wants to analyze a prompt for clarity, check if it uses best practices (defensive prompting, few-shot examples, output format constraints, role assignment), or when a prompt isn't working as expected. Triggers on keywords: プロンプト改善, プロンプト診断, prompt review, プロンプトエンジニアリング, プロンプトが効かない, system prompt, few-shot."
license: MIT
metadata:
  author: gon9a
  version: "1.0"
---

# Prompt Linter Skill

AIプロンプトの品質を診断し、改善案を提案するスキル。

## 診断チェックリスト

プロンプトを受け取ったら以下の観点でスコアリングする（各項目 0〜2 点）:

### 1. 役割・ペルソナ (Role)
- [ ] エージェントの役割が明確に定義されているか
- [ ] 例: `「あなたはシニアソフトウェアエンジニアです」`
- ❌ 悪い例: 役割の定義なし（エージェントが何者として振る舞うか不明）

### 2. タスクの明確さ (Task Clarity)
- [ ] 何をすべきかが一義的に理解できるか
- [ ] 曖昧な動詞（「整理する」「考える」）ではなく具体的な動詞（「箇条書きで列挙する」「JSON で返す」）を使っているか

### 3. 出力フォーマット指定 (Output Format)
- [ ] 期待する出力の形式が明示されているか（JSON / Markdown / 箇条書き / 表）
- [ ] 出力の長さの目安が示されているか

### 4. Few-Shot 例 (Examples)
- [ ] 入力→出力の具体例が1件以上あるか
- 例が 3 件以上あると特に効果的

### 5. 制約・防御 (Constraints / Defensive)
- [ ] してはいけないことが明示されているか（「ハルシネーションをしない」「確信がなければ不明と答える」）
- [ ] スコープ外の要求をどう扱うかが定義されているか

### 6. コンテキスト (Context)
- [ ] エージェントが判断するために必要な背景情報が含まれているか
- [ ] 対象ユーザーや前提条件が明示されているか

### 7. 反復・確認 (Iteration Hooks)
- [ ] 不明な場合は質問するよう促しているか
- [ ] 完了後の確認アクションが定義されているか

## 診断レポートのフォーマット

```markdown
## プロンプト診断レポート

**総合スコア**: X / 14

| 観点 | スコア | コメント |
|------|--------|---------|
| Role | X/2 | [コメント] |
| Task Clarity | X/2 | [コメント] |
| Output Format | X/2 | [コメント] |
| Few-Shot | X/2 | [コメント] |
| Constraints | X/2 | [コメント] |
| Context | X/2 | [コメント] |
| Iteration | X/2 | [コメント] |

## 主な問題点
1. [最も影響が大きい問題]
2. [次に影響が大きい問題]

## 改善案
[改善後のプロンプト全文 or 差分]
```

## よくあるアンチパターン

| アンチパターン | 問題 | 改善策 |
|--------------|------|--------|
| `「できるだけ詳しく説明して」` | 出力サイズ無制限でコスト増 | `「3つの箇条書きで説明して」` |
| `「いい感じにして」` | 「いい感じ」の定義が人によって異なる | 評価基準を明示する |
| プロンプトが 1 文 | コンテキスト不足でハルシネーション | 背景・制約・例を追加 |
| 否定形の指示のみ | 「〜しないこと」だけでは何をすべきかが不明 | 肯定形で「〜すること」も書く |
| Few-Shot 例が 1 件のみ | パターンが 1 つしか学習されない | 最低 3 件以上用意する |

## System Prompt vs User Prompt の役割分担

- **System Prompt**: 役割・制約・出力フォーマット・ペルソナ（永続的なルール）
- **User Prompt**: 具体的なタスク・入力データ・コンテキスト（その都度変わるもの）

## Gotchas

- プロンプトの長さ ≠ 品質。冗長な説明は精度を下げることがある
- 「〜しないこと」は 1〜2 件まで。多すぎると他の指示が希薄になる
- Few-Shot 例は多様性を持たせる（同じパターンの繰り返しは無意味）
- 改善後のプロンプトを元のプロンプトと同じ入力でテストして比較する
