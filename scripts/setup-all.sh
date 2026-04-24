#!/bin/bash
set -e

# ore-skills を Windsurf と Claude Code の両方に統合するセットアップスクリプト

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "  ore-skills 統合セットアップ"
echo "  (Windsurf + Claude Code)"
echo "=========================================="
echo ""

# Windsurf セットアップ
echo "--- Windsurf Skills ---"
if [ -f "$SCRIPT_DIR/setup-windsurf.sh" ]; then
  bash "$SCRIPT_DIR/setup-windsurf.sh"
else
  echo "  setup-windsurf.sh が見つかりません。スキップします。"
fi

echo ""
echo "--- Claude Code Skills ---"
if [ -f "$SCRIPT_DIR/setup-claude-code.sh" ]; then
  bash "$SCRIPT_DIR/setup-claude-code.sh"
else
  echo "  setup-claude-code.sh が見つかりません。スキップします。"
fi

echo ""
echo "=========================================="
echo "  セットアップ完了"
echo "=========================================="
echo ""
echo "ore-skills は以下の場所から利用可能です:"
echo "  Windsurf:    @skill-name で起動"
echo "  Claude Code: /skill-name で起動"
echo ""
echo "ore-skills を更新する場合:"
echo "  cd $(dirname "$SCRIPT_DIR")"
echo "  git pull"
