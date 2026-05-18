#!/usr/bin/env bash
# DEPRECATED: このスクリプトは scripts/install.sh に置き換えられました。
# install.sh は ~/.agents/skills, ~/.claude/skills, ~/.codeium/windsurf/skills の3パスを
# 一括で安全に管理します (dangling 検知、実体退避、--dry-run / --prune 等)。
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "⚠️  setup-all.sh は deprecated です。代わりに install.sh を使ってください:"
echo "    bash $SCRIPT_DIR/install.sh"
echo ""
echo "互換のため install.sh を実行します..."
exec bash "$SCRIPT_DIR/install.sh" "$@"
