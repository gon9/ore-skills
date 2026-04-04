#!/bin/bash
set -e

# ore-skills を最新化し、Windsurf Skills のシンボリックリンクを再構築するスクリプト

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORE_SKILLS_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  ore-skills 更新スクリプト"
echo "=========================================="
echo ""

# 実行場所の確認
PROJECT_ROOT="$(pwd)"

if [ "$PROJECT_ROOT" = "$ORE_SKILLS_ROOT" ]; then
    # ore-skills リポジトリ単体での実行
    echo "🔄 ore-skills 自体を更新します..."
    git pull
else
    # サブモジュールとして組み込まれているプロジェクトでの実行
    echo "🔄 サブモジュール内の ore-skills を最新化します..."
    
    # ore-skillsディレクトリに移動してpull
    cd "$ORE_SKILLS_ROOT"
    git fetch
    git checkout main
    git pull origin main
    
    # 元のディレクトリに戻る
    cd "$PROJECT_ROOT"
fi

echo ""
echo "📦 依存関係を更新します..."
if command -v uv &> /dev/null; then
    # uvが存在する場合は lock と sync を実行 (プロジェクトルートにpyproject.tomlがある場合)
    if [ -f "pyproject.toml" ]; then
        uv lock
        uv sync
    elif [ -f "$ORE_SKILLS_ROOT/pyproject.toml" ]; then
        cd "$ORE_SKILLS_ROOT"
        uv lock
        uv sync
        cd "$PROJECT_ROOT"
    fi
else
    echo "⚠️ uv コマンドが見つかりません。依存関係の更新はスキップします。"
fi

echo ""
echo "🔗 シンボリックリンクを再構築します..."
bash "$ORE_SKILLS_ROOT/scripts/setup-windsurf.sh" <<EOF
1
EOF

echo ""
echo "✨ 更新が完了しました！"
echo "Windsurfのウィンドウを再起動（Reload Window）して変更を反映してください。"
