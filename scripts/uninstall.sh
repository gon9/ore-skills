#!/usr/bin/env bash
# uninstall.sh — ore-skills が作った symlink を解除する
#
# 安全装置:
#   - ore-skills/skills/ 配下を指す symlink のみ削除する
#   - 実体ファイル/ディレクトリは絶対に削除しない
#   - dangling symlink でも、リンク先文字列が ore-skills/skills/ で始まる場合のみ削除
#
# 使い方:
#   scripts/uninstall.sh                 # 3ターゲット全て
#   scripts/uninstall.sh --target=claude # 単一ターゲット (agents|claude|windsurf|all)
#   scripts/uninstall.sh --dry-run       # 削除予定だけ表示
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORE_SKILLS_ROOT="$(dirname "$SCRIPT_DIR")"
SKILLS_SRC="$ORE_SKILLS_ROOT/skills"

DRY_RUN=false
TARGET="all"

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --target=*) TARGET="${arg#--target=}" ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "不明な引数: $arg" >&2; exit 2 ;;
  esac
done

declare -a TARGET_PATHS=()
declare -a TARGET_LABELS=()
add_target() { TARGET_PATHS+=("$1"); TARGET_LABELS+=("$2"); }

if [[ "$TARGET" == "all" || "$TARGET" == "agents" ]]; then
  add_target "$HOME/.agents/skills" "cross-agent (~/.agents/skills)"
fi
if [[ "$TARGET" == "all" || "$TARGET" == "claude" ]]; then
  add_target "$HOME/.claude/skills" "Claude Code (~/.claude/skills)"
fi
if [[ "$TARGET" == "all" || "$TARGET" == "windsurf" ]]; then
  add_target "$HOME/.codeium/windsurf/skills" "Windsurf (~/.codeium/windsurf/skills)"
fi

run() {
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [dry-run] $*"
  else
    "$@"
  fi
}

echo "=========================================="
echo "  ore-skills uninstall"
echo "=========================================="
echo "ソース      : $SKILLS_SRC"
echo "ターゲット  : ${TARGET_LABELS[*]}"
echo "dry-run     : $DRY_RUN"
echo ""

for i in "${!TARGET_PATHS[@]}"; do
  target_dir="${TARGET_PATHS[$i]}"
  label="${TARGET_LABELS[$i]}"
  echo "▶ $label"
  if [[ ! -d "$target_dir" ]]; then
    echo "  (ディレクトリが存在しません — スキップ)"
    continue
  fi

  for entry in "$target_dir"/*; do
    [[ -e "$entry" || -L "$entry" ]] || continue
    name="$(basename "$entry")"
    [[ "$name" == ".DS_Store" ]] && continue

    if [[ -L "$entry" ]]; then
      current="$(readlink "$entry")"
      if [[ "$current" == "$SKILLS_SRC/"* ]]; then
        echo "  ✓ $name (symlink → $current を削除)"
        run rm "$entry"
      else
        echo "  - $name (ore-skills 由来でない symlink — 保持)"
      fi
    else
      echo "  - $name (実体 — 保持)"
    fi
  done
  echo ""
done

echo "=========================================="
if [[ "$DRY_RUN" == "true" ]]; then
  echo "✅ dry-run 完了"
else
  echo "✅ uninstall 完了"
fi
