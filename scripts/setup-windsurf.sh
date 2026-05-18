#!/usr/bin/env bash
# DEPRECATED: scripts/install.sh --target=windsurf に置き換えられました。
# Windsurf は ~/.agents/skills/ も cross-agent としてスキャンするため、--target=all 推奨。
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "⚠️  setup-windsurf.sh は deprecated です。代わりに以下を使ってください:"
echo "    bash $SCRIPT_DIR/install.sh --target=windsurf"
echo "  (または cross-agent も含めて) bash $SCRIPT_DIR/install.sh"
echo ""
echo "互換のため install.sh --target=windsurf を実行します..."
exec bash "$SCRIPT_DIR/install.sh" --target=windsurf "$@"
