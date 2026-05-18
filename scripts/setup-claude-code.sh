#!/usr/bin/env bash
# DEPRECATED: scripts/install.sh --target=claude に置き換えられました。
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "⚠️  setup-claude-code.sh は deprecated です。代わりに以下を使ってください:"
echo "    bash $SCRIPT_DIR/install.sh --target=claude"
echo ""
echo "互換のため install.sh --target=claude を実行します..."
exec bash "$SCRIPT_DIR/install.sh" --target=claude "$@"
