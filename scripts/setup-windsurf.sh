#!/bin/bash
set -e

# ore-skills を Windsurf Skills として統合するセットアップスクリプト

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORE_SKILLS_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  ore-skills → Windsurf Skills 統合"
echo "=========================================="
echo ""

# 統合タイプを選択
echo "統合タイプを選択してください:"
echo "1) Workspace Skills (現在のプロジェクトのみ)"
echo "2) Global Skills (すべてのプロジェクト)"
echo ""
read -p "選択 (1 or 2): " choice

case $choice in
  1)
    # Workspace Skills として統合
    echo ""
    echo "📁 Workspace Skills として統合します"
    echo ""
    
    if [ ! -d ".git" ]; then
      echo "❌ エラー: Gitリポジトリのルートで実行してください"
      exit 1
    fi
    
    SKILLS_DIR=".windsurf/skills"
    mkdir -p "$SKILLS_DIR"
    
    # ore-skills が submodule かどうかチェック
    if [ -d ".ore-skills" ]; then
      ORE_SKILLS_PATH="$(pwd)/.ore-skills/skills"
      echo "✓ 既存の .ore-skills を使用します"
    else
      echo "ore-skills を Git Submodule として追加しますか? (y/n)"
      read -p "> " add_submodule
      if [ "$add_submodule" = "y" ]; then
        git submodule add https://github.com/gon9/ore-skills.git .ore-skills
        git submodule update --init --recursive
        ORE_SKILLS_PATH="$(pwd)/.ore-skills/skills"
        echo "✓ Git Submodule として追加しました"
      else
        echo "ore-skills のパスを入力してください:"
        read -p "> " input_path
        ORE_SKILLS_PATH="$input_path"
      fi
    fi
    
    echo ""
    echo "🔗 シンボリックリンクを作成中..."
    
    # シンボリックリンクを作成
    for skill in "$ORE_SKILLS_PATH"/*; do
      skill_name=$(basename "$skill")
      if [ "$skill_name" = "common" ]; then
        continue  # common はスキップ
      fi
      
      if [ -d "$skill" ] && [ -f "$skill/SKILL.md" ]; then
        # 相対パスを計算
        if command -v realpath &> /dev/null; then
          relative_path=$(realpath --relative-to="$SKILLS_DIR" "$skill")
        else
          # realpath がない場合は絶対パスを使用
          relative_path="$skill"
        fi
        
        ln -sf "$relative_path" "$SKILLS_DIR/$skill_name"
        echo "  ✓ $skill_name"
      fi
    done
    
    echo ""
    echo "✅ Workspace Skills として統合完了"
    echo ""
    echo "次のステップ:"
    echo "1. Windsurf を再起動"
    echo "2. Cascade パネルの三点メニュー → Skills で確認"
    ;;
    
  2)
    # Global Skills として統合
    echo ""
    echo "🌐 Global Skills として統合します"
    echo ""
    
    SKILLS_DIR="$HOME/.codeium/windsurf/skills"
    mkdir -p "$SKILLS_DIR"
    
    echo "🔗 シンボリックリンクを作成中..."
    
    # シンボリックリンクを作成
    for skill in "$ORE_SKILLS_ROOT/skills"/*; do
      skill_name=$(basename "$skill")
      if [ "$skill_name" = "common" ]; then
        continue  # common はスキップ
      fi
      
      if [ -d "$skill" ] && [ -f "$skill/SKILL.md" ]; then
        ln -sf "$skill" "$SKILLS_DIR/$skill_name"
        echo "  ✓ $skill_name"
      fi
    done
    
    echo ""
    echo "✅ Global Skills として統合完了"
    echo ""
    echo "次のステップ:"
    echo "1. Windsurf を再起動"
    echo "2. Cascade パネルの三点メニュー → Skills で確認"
    echo ""
    echo "📝 ore-skills を更新する場合:"
    echo "   cd $ORE_SKILLS_ROOT"
    echo "   git pull"
    ;;
    
  *)
    echo "❌ 無効な選択です"
    exit 1
    ;;
esac
