#!/usr/bin/env bash

# check-skill-health.sh: skills/ 以下の各スキルの健全性をチェックするスクリプト

set -e

SKILLS_DIR="$(dirname "$0")/../skills"

echo "🩺 Starting Skill Health Check..."
echo "====================================="

PASSED=0
FAILED=0
IGNORED_DIRS=("common" "video_summary")

for skill_path in "$SKILLS_DIR"/*; do
    if [ ! -d "$skill_path" ] || [ "$(basename "$skill_path")" == ".DS_Store" ]; then
        continue
    fi
    
    SKILL_NAME=$(basename "$skill_path")
    
    # スキップ判定
    skip=false
    for ignored in "${IGNORED_DIRS[@]}"; do
        if [ "$SKILL_NAME" == "$ignored" ]; then
            skip=true
            break
        fi
    done
    
    if [ "$skip" = true ]; then
        echo "⏭️  Skipping $SKILL_NAME (ignored)"
        continue
    fi

    echo -n "Checking $SKILL_NAME... "
    
    # 1. SKILL.md の存在チェック
    if [ ! -f "$skill_path/SKILL.md" ]; then
        echo "❌ FAILED"
        echo "   -> Missing SKILL.md"
        FAILED=$((FAILED + 1))
        continue
    fi
    
    # 2. name が SKILL.md とディレクトリで一致しているかチェック (簡単なgrep)
    if ! grep -q "name: $SKILL_NAME" "$skill_path/SKILL.md"; then
        echo "❌ FAILED"
        echo "   -> Frontmatter 'name:' does not match directory name ($SKILL_NAME) in SKILL.md"
        FAILED=$((FAILED + 1))
        continue
    fi
    
    # 3. pyproject.toml が存在するか
    if [ ! -f "$skill_path/pyproject.toml" ]; then
        echo "❌ FAILED"
        echo "   -> Missing pyproject.toml"
        FAILED=$((FAILED + 1))
        continue
    fi
    
    # 4. テスト実行 (存在する場合)
    if [ -d "$skill_path/tests" ] && [ -n "$(ls -A "$skill_path/tests/" 2>/dev/null)" ]; then
        # -q オプションで出力を抑制し、失敗した場合のみ表示
        if ! uv run pytest -q "$skill_path/tests/" > /dev/null 2>&1; then
             echo "❌ FAILED"
             echo "   -> Tests failed for $SKILL_NAME. Run 'uv run pytest $skill_path/tests/' manually."
             FAILED=$((FAILED + 1))
             continue
        fi
    fi
    
    echo "✅ PASSED"
    PASSED=$((PASSED + 1))
done

echo "====================================="
echo "Health Check Complete: $PASSED passed, $FAILED failed."

if [ $FAILED -gt 0 ]; then
    exit 1
fi
