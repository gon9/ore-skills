# ore-skills-server

外部・動的能力をMCPで公開するための実験的なstdioサーバーです。`SKILL.md` 配布の代替ではなく、全スキルをMCP Toolへ変換することも目的にしません。

現在の公開ツール:

- `get_transcript`: YouTube動画IDから文字起こしを取得する
- `check_spec`: 仕様書本文の必須セクションを検査する

```bash
uv run ore-skills-server
uv run pytest servers/ore-skills-server/tests
```

ツール名、入力、返却値を変更するときは `tests/test_mcp_contract.py` の契約テストも更新してください。リモートtransportは未実装です。
