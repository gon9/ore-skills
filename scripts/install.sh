#!/usr/bin/env bash
# install.sh — ore-skills の skills/ をエージェントが読めるグローバルパスへ symlink する
#
# 対象パス（複数まとめて配置できる）:
#   - ~/.agents/skills/               (cross-agent: Windsurf が公式に追加スキャン)
#   - ~/.claude/skills/               (Claude Code personal scope)
#   - ~/.codeium/windsurf/skills/     (Windsurf global scope)
#   - ~/.cursor/skills/               (Cursor — 公式 Client Showcase 対応)
#
# 設計上の制約（docs_obsidian の Git 同期トラブル教訓より）:
#   - 各プロジェクトリポジトリに submodule や clone を増やさない
#   - 各リポジトリの .claude/skills/ や .windsurf/skills/ には触らない
#   - 配置はユーザの $HOME 配下のみ。リポジトリ境界を一切汚さない
#
# 使い方:
#   scripts/install.sh                       # 3ターゲット全てに配置（確認あり）
#   scripts/install.sh --dry-run             # 実際には書き込まず、計画だけ表示
#   scripts/install.sh --target=agents       # 単一ターゲット (agents|claude|windsurf|cursor|all)
#   scripts/install.sh --yes                 # 確認プロンプトを省略
#   scripts/install.sh --prune               # ore-skills/skills/ に存在しない symlink を削除
#
# 安全装置:
#   - すでに正しい symlink がある場合は何もしない（冪等）
#   - 別パスを指す symlink は --yes か対話確認のうえ張り直し
#   - 実体ディレクトリ/ファイルがある場合は <name>.bak.<timestamp> へ退避してから配置
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORE_SKILLS_ROOT="$(dirname "$SCRIPT_DIR")"
SKILLS_SRC="$ORE_SKILLS_ROOT/skills"

# Skills として配布しないディレクトリ（内部ライブラリ等）
EXCLUDE_NAMES=("common")

DRY_RUN=false
ASSUME_YES=false
PRUNE=false
TARGET="all"

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --yes|-y) ASSUME_YES=true ;;
    --prune) PRUNE=true ;;
    --target=*) TARGET="${arg#--target=}" ;;
    -h|--help)
      sed -n '2,28p' "$0"
      exit 0
      ;;
    *)
      echo "不明な引数: $arg" >&2
      exit 2
      ;;
  esac
done

case "$TARGET" in
  all|agents|claude|windsurf|cursor) ;;
  *) echo "--target は all|agents|claude|windsurf|cursor のいずれか" >&2; exit 2 ;;
esac

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
if [[ "$TARGET" == "all" || "$TARGET" == "cursor" ]]; then
  add_target "$HOME/.cursor/skills" "Cursor (~/.cursor/skills)"
fi

is_excluded() {
  local name="$1"
  for ex in "${EXCLUDE_NAMES[@]}"; do
    [[ "$name" == "$ex" ]] && return 0
  done
  return 1
}

prompt_yes() {
  local msg="$1"
  if [[ "$ASSUME_YES" == "true" ]]; then
    return 0
  fi
  read -r -p "$msg [y/N]: " ans
  [[ "$ans" =~ ^[yY]$ ]]
}

run() {
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [dry-run] $*"
  else
    "$@"
  fi
}

echo "=========================================="
echo "  ore-skills install"
echo "=========================================="
echo "ソース      : $SKILLS_SRC"
echo "ターゲット  : ${TARGET_LABELS[*]}"
echo "dry-run     : $DRY_RUN"
echo "prune       : $PRUNE"
echo ""

if [[ ! -d "$SKILLS_SRC" ]]; then
  echo "❌ skills ディレクトリが見つかりません: $SKILLS_SRC" >&2
  exit 1
fi

# 配布対象 skill 名の一覧
declare -a SKILL_NAMES=()
for skill_path in "$SKILLS_SRC"/*; do
  [[ -d "$skill_path" ]] || continue
  name="$(basename "$skill_path")"
  is_excluded "$name" && continue
  if [[ ! -f "$skill_path/SKILL.md" ]]; then
    echo "⚠️  $name に SKILL.md が無いためスキップ" >&2
    continue
  fi
  SKILL_NAMES+=("$name")
done

if [[ ${#SKILL_NAMES[@]} -eq 0 ]]; then
  echo "配布対象の skill がありません。" >&2
  exit 1
fi

echo "配布する skill:"
printf '  - %s\n' "${SKILL_NAMES[@]}"
echo ""

install_one() {
  local target_dir="$1" label="$2" name="$3"
  local src="$SKILLS_SRC/$name"
  local dst="$target_dir/$name"

  # ターゲットディレクトリ作成
  if [[ ! -d "$target_dir" ]]; then
    run mkdir -p "$target_dir"
  fi

  if [[ -L "$dst" ]]; then
    local current
    current="$(readlink "$dst")"
    if [[ "$current" == "$src" ]]; then
      echo "  ✓ $name (既に正しいリンク)"
      return 0
    fi
    if [[ ! -e "$dst" ]]; then
      echo "  ⚠️  $name: dangling symlink ($current)"
    else
      echo "  ⚠️  $name: 別パスへの symlink ($current)"
    fi
    if prompt_yes "    張り直しますか？"; then
      run rm "$dst"
      run ln -s "$src" "$dst"
      echo "  ✓ $name (張り直し)"
    else
      echo "  - $name (スキップ)"
    fi
    return 0
  fi

  if [[ -e "$dst" ]]; then
    # 実体ディレクトリ/ファイル → 退避
    local ts backup
    ts="$(date +%Y%m%d-%H%M%S)"
    backup="${dst}.bak.${ts}"
    echo "  ⚠️  $name: 実体が存在します → $backup へ退避します"
    if prompt_yes "    退避して symlink に置き換えますか？"; then
      run mv "$dst" "$backup"
      run ln -s "$src" "$dst"
      echo "  ✓ $name (退避→symlink)"
    else
      echo "  - $name (スキップ)"
    fi
    return 0
  fi

  run ln -s "$src" "$dst"
  echo "  ✓ $name (新規)"
}

prune_target() {
  local target_dir="$1" label="$2"
  [[ -d "$target_dir" ]] || return 0
  echo ""
  echo "🧹 prune: $label"
  for entry in "$target_dir"/*; do
    [[ -e "$entry" || -L "$entry" ]] || continue
    local name
    name="$(basename "$entry")"
    [[ "$name" == ".DS_Store" ]] && continue
    if [[ -L "$entry" ]]; then
      local current
      current="$(readlink "$entry")"
      # ore-skills/skills/ 配下を指すリンクのみ判定対象
      if [[ "$current" == "$SKILLS_SRC/"* ]]; then
        local link_name="${current##*/}"
        if [[ ! -d "$SKILLS_SRC/$link_name" ]] || is_excluded "$link_name"; then
          echo "  - $name → 旧 skill ($current) を指しているため削除"
          run rm "$entry"
        fi
      fi
    fi
  done
}

EXIT_CODE=0
for i in "${!TARGET_PATHS[@]}"; do
  target_dir="${TARGET_PATHS[$i]}"
  label="${TARGET_LABELS[$i]}"
  echo ""
  echo "▶ $label"
  for name in "${SKILL_NAMES[@]}"; do
    install_one "$target_dir" "$label" "$name" || EXIT_CODE=$?
  done
  if [[ "$PRUNE" == "true" ]]; then
    prune_target "$target_dir" "$label"
  fi
done

echo ""
echo "=========================================="
if [[ "$DRY_RUN" == "true" ]]; then
  echo "✅ dry-run 完了 (実際の変更はしていません)"
else
  echo "✅ インストール完了"
fi
echo ""
echo "次のステップ:"
echo "  - Windsurf / Claude Code を再起動して新しい skill を認識させる"
echo "  - 状態確認: scripts/doctor.sh"
echo "  - 解除    : scripts/uninstall.sh"

exit $EXIT_CODE
