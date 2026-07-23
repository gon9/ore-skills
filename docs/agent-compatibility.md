# Agent Compatibility

ore-skills は `SKILL.md` を共通フォーマットにして、複数のエージェント面に同じスキルを配布する方針を取る。

## 現在の配布先

| エージェント面 | 配布先 |
|---|---|
| Codex / Antigravity / Devin などの cross-agent 面 | `~/.agents/skills/<skill-name>/` |
| Claude Code | `~/.claude/skills/<skill-name>/` |
| Windsurf | `~/.codeium/windsurf/skills/<skill-name>/` |
| Cursor | `~/.cursor/skills/<skill-name>/` |

## インストール

```bash
bash scripts/install.sh --target=agents --channel=stable
```

全ターゲットに配布するなら `--target=all` を使う。`experimental` は明示指定した場合だけ配布する。Codexのチーム配布には `.agents/plugins/marketplace.json` と `plugins/ore-skills-stable/` を使う。

## 運用方針

- repo ルールは `AGENTS.md` に寄せる
- エージェント固有の案内は必要最小限にする
- 共有可能な処理は `scripts/` に切り出す
- 長い説明や手順は `docs/` に逃がす

## 補足

Antigravity の CLI は `agy` を `~/.local/bin` に入れるタイプの軽量 CLI なので、`ore-skills` 側は実行バイナリへ依存せず、`~/.agents/skills` の共有面に寄せておくのが扱いやすい。
