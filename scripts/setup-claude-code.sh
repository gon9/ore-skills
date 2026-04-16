#!/bin/bash
set -e

# ore-skills を Claude Code Skills として統合するセットアップスクリプト

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORE_SKILLS_ROOT="$(dirname "$SCRIPT_DIR")"

# ore-skills リポジトリ自体の中から実行されているかを判定
RUNNING_INSIDE_ORE_SKILLS=false
CURRENT_DIR="$(pwd)"
if [ "$CURRENT_DIR" = "$ORE_SKILLS_ROOT" ] || [[ "$CURRENT_DIR" == "$ORE_SKILLS_ROOT/"* ]]; then
  RUNNING_INSIDE_ORE_SKILLS=true
fi

echo "=========================================="
echo "  ore-skills → Claude Code Skills 統合"
echo "=========================================="
echo ""

if [ "$RUNNING_INSIDE_ORE_SKILLS" = true ]; then
  echo "ℹ️  ore-skills リポジトリ内から実行されています。"
  echo "   Personal Skills として統合します（Project は ore-skills 自身と循環するため不可）。"
  echo ""
  choice=1
else
  echo "統合タイプを選択してください:"
  echo "1) Personal Skills (~/.claude/skills/ — すべてのプロジェクトで利用可能)"
  echo "2) Project Skills  (.claude/skills/  — 現在のプロジェクトのみ)"
  echo ""
  read -p "選択 (1 or 2): " choice
fi

case $choice in
  1)
    # Personal Skills として統合
    echo ""
    echo "🌐 Personal Skills として統合します"
    echo ""

    SKILLS_DIR="$HOME/.claude/skills"
    mkdir -p "$SKILLS_DIR"

    echo "🔗 シンボリックリンクを作成中..."

    for skill in "$ORE_SKILLS_ROOT/skills"/*; do
      skill_name=$(basename "$skill")
      if [ "$skill_name" = "common" ]; then
        continue
      fi

      if [ -d "$skill" ] && [ -f "$skill/SKILL.md" ]; then
        ln -sf "$skill" "$SKILLS_DIR/$skill_name"
        echo "  ✓ $skill_name"
      fi
    done

    echo ""
    echo "✅ Personal Skills として統合完了"
    echo ""
    echo "次のステップ:"
    echo "1. Claude Code を再起動（新規セッションを開始）"
    echo "2. /skill-name でスキルを呼び出し可能"
    echo ""
    echo "📝 ore-skills を更新する場合:"
    echo "   cd $ORE_SKILLS_ROOT"
    echo "   git pull"
    ;;

  2)
    # Project Skills として統合
    echo ""
    echo "📁 Project Skills として統合します"
    echo ""

    if [ ! -d ".git" ] && [ ! -f ".git" ]; then
      echo "❌ エラー: Gitリポジトリのルートで実行してください"
      exit 1
    fi

    PROJECT_ROOT="$(pwd)"
    SKILLS_DIR="$PROJECT_ROOT/.claude/skills"
    mkdir -p "$SKILLS_DIR"

    ORE_SKILLS_PATH="$ORE_SKILLS_ROOT/skills"
    echo "✓ ore-skills の skills を使用します: $ORE_SKILLS_PATH"

    echo ""
    echo "🔗 シンボリックリンクを作成中..."

    for skill in "$ORE_SKILLS_PATH"/*; do
      skill_name=$(basename "$skill")
      if [ "$skill_name" = "common" ]; then
        continue
      fi

      if [ -d "$skill" ] && [ -f "$skill/SKILL.md" ]; then
        if command -v python3 &> /dev/null; then
          relative_path=$(python3 -c "import os.path; print(os.path.relpath('$skill', '$SKILLS_DIR'))")
        else
          relative_path="$skill"
        fi

        ln -sf "$relative_path" "$SKILLS_DIR/$skill_name"
        echo "  ✓ $skill_name"
      fi
    done

    echo ""
    echo "✅ Project Skills として統合完了"
    echo ""
    echo "次のステップ:"
    echo "1. Claude Code を再起動（新規セッションを開始）"
    echo "2. /skill-name でスキルを呼び出し可能"
    echo ""
    echo "💡 .claude/skills/ をGitにコミットすると、チームメンバーも同じスキルを利用できます。"
    ;;

  *)
    echo "❌ 無効な選択です"
    exit 1
    ;;
esac
