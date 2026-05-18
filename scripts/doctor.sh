#!/usr/bin/env bash
# doctor.sh — ore-skills の symlink 設置状況を診断する
#
# チェック内容:
#   - 各ターゲット配下の skill が ore-skills/skills/<name> へ正しく解決されるか
#   - dangling symlink がないか
#   - 実体ディレクトリがあって symlink を妨げていないか
#   - ore-skills/skills/ にあるが、いずれかのターゲットに未配置の skill
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORE_SKILLS_ROOT="$(dirname "$SCRIPT_DIR")"
SKILLS_SRC="$ORE_SKILLS_ROOT/skills"
EXCLUDE_NAMES=("common")

is_excluded() {
  local name="$1"
  for ex in "${EXCLUDE_NAMES[@]}"; do
    [[ "$name" == "$ex" ]] && return 0
  done
  return 1
}

declare -a TARGETS=(
  "$HOME/.agents/skills|cross-agent"
  "$HOME/.claude/skills|Claude Code"
  "$HOME/.codeium/windsurf/skills|Windsurf"
)

declare -a EXPECTED=()
for skill_path in "$SKILLS_SRC"/*; do
  [[ -d "$skill_path" ]] || continue
  name="$(basename "$skill_path")"
  is_excluded "$name" && continue
  [[ -f "$skill_path/SKILL.md" ]] || continue
  EXPECTED+=("$name")
done

echo "=========================================="
echo "  ore-skills doctor"
echo "=========================================="
echo "ソース: $SKILLS_SRC"
echo ""
echo "配布対象 skill (${#EXPECTED[@]}):"
printf '  - %s\n' "${EXPECTED[@]}"
echo ""

PROBLEMS=0

for entry in "${TARGETS[@]}"; do
  target_dir="${entry%%|*}"
  label="${entry##*|}"
  echo "▶ $label  ($target_dir)"

  if [[ ! -d "$target_dir" ]]; then
    echo "  ⚠️  ディレクトリ未作成 — install.sh で作成されます"
    PROBLEMS=$((PROBLEMS+1))
    echo ""
    continue
  fi

  PRESENT_NAMES=""

  # 配布対象かどうかを判定するためのリスト文字列
  EXPECTED_STR=""
  for n in "${EXPECTED[@]}"; do EXPECTED_STR="$EXPECTED_STR|$n|"; done

  for child in "$target_dir"/*; do
    [[ -e "$child" || -L "$child" ]] || continue
    name="$(basename "$child")"
    [[ "$name" == ".DS_Store" ]] && continue
    # 退避バックアップは情報通知のみ
    if [[ "$name" == *.bak.* ]]; then
      echo "  ℹ️  $name : install.sh による退避バックアップ (手動で削除可)"
      continue
    fi
    PRESENT_NAMES="$PRESENT_NAMES|$name|"
    is_expected=false
    if [[ "$EXPECTED_STR" == *"|$name|"* ]]; then
      is_expected=true
    fi

    if [[ -L "$child" ]]; then
      target="$(readlink "$child")"
      if [[ ! -e "$child" ]]; then
        echo "  ❌ $name : dangling → $target"
        PROBLEMS=$((PROBLEMS+1))
      elif [[ "$target" == "$SKILLS_SRC/$name" ]]; then
        echo "  ✓ $name"
      elif [[ "$target" == "$SKILLS_SRC/"* ]]; then
        echo "  ⚠️  $name : 別 skill を指している → $target"
        PROBLEMS=$((PROBLEMS+1))
      else
        echo "  ℹ️  $name : ore-skills 外を指す symlink → $target (保持)"
      fi
    else
      if [[ "$is_expected" == "true" ]]; then
        echo "  ⚠️  $name : 実体ディレクトリ/ファイル (symlink にできていない)"
        PROBLEMS=$((PROBLEMS+1))
      else
        echo "  ℹ️  $name : ore-skills 管理外の実体 (保持)"
      fi
    fi
  done

  for name in "${EXPECTED[@]}"; do
    if [[ "$PRESENT_NAMES" != *"|$name|"* ]]; then
      echo "  ❌ $name : 未配置"
      PROBLEMS=$((PROBLEMS+1))
    fi
  done

  echo ""
done

echo "=========================================="
if [[ $PROBLEMS -eq 0 ]]; then
  echo "✅ 問題なし"
  exit 0
else
  echo "⚠️  問題が $PROBLEMS 件見つかりました。"
  echo "    修復: scripts/install.sh --yes"
  echo "    掃除: scripts/install.sh --prune --yes"
  exit 1
fi
