---
description: "docs / タスク管理 / CI の運用規約（Linear が正典、lane:1/2/3、ready label）"
trigger: always_on
---

## 正典を一つに決め、二重に持たない

- 進行状態・担当・blocker は **Linear だけ**が持つ。docs に書き戻さない
- `ready` label が付いた issue だけを着手対象にする。付いていないものは「まだ考えるべきこと」

## 文書量はリスクと不可逆性で決める

作業の大きさではない。Linear の `lane:` label で表す。

- `lane:1` バグ修正・設定変更 → issue だけ。docs を書かない
- `lane:2` 通常の機能追加 → issue + `docs/tasks/<slug>/task.md`。設計書は実装後に書き戻す
- `lane:3` 外部書き込み・課金・個人情報・不可逆 → task + plan + 設計書のフル構成

## 規約を宣言したら検証も足す

- 宣言しただけの規約は守られない。規約を足したら同じ PR で検証も足し、CI で自動実行する
- 既存プロジェクトを見るときは `.github/` の有無を最初に確認する
- CI の環境を本番に寄せない。緑にするために検出力を削っていないか毎回問う

## docs の構成

- フォルダは目的で分ける。進行状態では分けない
- 状態は frontmatter の `status:`（draft / active / implemented / superseded / frozen）だけで持つ

## 失敗の扱い

- 無音で壊れるな。「0件」と「取得できていない」を区別する。exit 0 は成功を意味しない
- 現在の branch / worktree を自分専用と推定しない
