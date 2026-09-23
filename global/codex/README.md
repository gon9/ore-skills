# global/codex — Codex CLI / Desktop のコスト制御設定

`~/.codex/config.toml` に**手で差し込む**設定の正典。config.toml 全体は Desktop アプリが
書き換える(projects / plugins / desktop)ため、ファイルごとの管理はせず、ここには
コスト制御に効く差分だけを置く。

方針は `plugins/ore-rules/rules/model-routing.md`(Fusion 型のモデル配分)。

## 1. サブエージェントを安価階層に固定する

```toml
model_auto_compact_token_limit = 100000

[agents]
default_subagent_model = "gpt-6-luna"        # 安価階層。更新時は models_cache.json の説明で選ぶ
default_subagent_reasoning_effort = "medium"
max_concurrent_threads_per_session = 3
```

- spawn 時にモデルを明示した場合はそちらが優先される(`agents.default_subagent_model` の仕様)
- `model_auto_compact_token_limit` は保険。文脈が 10 万を超えたら自動で compact する。
  主対策は resume-guard フックと「1 スレッド 1 目的」

## 2. resume-guard フック(長いスレッドの「続き」再開を止める)

`~/.codex/hooks.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 $HOME/workspace/ai-agent/ore-skills/hooks/resume_guard.py --agent codex",
            "timeout": 10,
            "statusMessage": "resume-guard"
          }
        ]
      }
    ]
  }
}
```

**初回は Codex で `/hooks` を開き、このフックを trust すること。** trust されるまでスキップされる。
挙動・閾値は `hooks/resume_guard.py` の docstring を参照。

### 限界

- `/goal` の**自動継続**はユーザー入力ではないため `UserPromptSubmit` が発火しない。
  止められるのは「/goal 続き…」を打った瞬間だけ。巨大な文脈で goal を回さないこと
- フックは compact や新スレッド作成を実行できない(Codex の hooks 仕様)。
  代わりにハンドオフを書き出してプロンプトをブロックし、`/new` を促す

## 3. プラグインの棚卸し(2026-09-23 時点)

全セッションのツール呼び出しを集計した結果、利用 0〜3 回のものを無効化した。
スキル一覧やツール定義は毎リクエストの固定コストになるため、使わないものは切る。

| 状態 | プラグイン | 根拠(ツール呼び出し回数) |
|---|---|---|
| 有効 | github / linear / google-drive | 17 / 8 / 6 |
| 有効 | browser / chrome / computer-use / unified-computer-use / codex-app-tools | 40 / 18 / 12 / 基盤 |
| 無効 | gmail / google-calendar / documents / template-creator / visualize | 0 |
| 無効 | slack / spreadsheets / presentations / pdf | 3 / 3 / 2 / 1 |

必要になったら `[plugins."<name>@<marketplace>"] enabled = true` に戻すだけでよい。
