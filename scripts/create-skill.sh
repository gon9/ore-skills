#!/usr/bin/env bash

# create-skill.sh: ore-skills の新しいスキルの雛形を生成するスクリプト

set -e

if [ $# -lt 2 ]; then
    echo "Usage: $0 <skill-name> \"<description>\""
    echo "Example: $0 git-utils \"Automates git operations and changelog generation\""
    exit 1
fi

SKILL_NAME="$1"
DESCRIPTION="$2"
SKILLS_DIR="$(dirname "$0")/../skills"
SKILL_PATH="$SKILLS_DIR/$SKILL_NAME"

# スキル名のバリデーション (agentskills.io 仕様: 小文字英数字とハイフンのみ)
if ! [[ "$SKILL_NAME" =~ ^[a-z0-9-]+$ ]]; then
    echo "Error: Skill name can only contain lowercase letters, numbers, and hyphens."
    exit 1
fi

if [ -d "$SKILL_PATH" ]; then
    echo "Error: Skill '$SKILL_NAME' already exists."
    exit 1
fi

echo "🚀 Creating skill '$SKILL_NAME'..."

# ディレクトリ作成
mkdir -p "$SKILL_PATH/src/${SKILL_NAME//-/_}"
mkdir -p "$SKILL_PATH/tests"
mkdir -p "$SKILL_PATH/references"
mkdir -p "$SKILL_PATH/scripts"

# SKILL.md 作成
cat > "$SKILL_PATH/SKILL.md" << EOF
---
name: $SKILL_NAME
description: $DESCRIPTION
license: MIT
compatibility: Python 3.12+
---

# $SKILL_NAME

## Overview
$DESCRIPTION

## Capabilities
- **Feature A**: Description of what Feature A does. See [references/feature-a.md](references/feature-a.md) for details.

## Usage
### Feature A
1. Prepare input
2. Run command: \`uv run -m ${SKILL_NAME//-/_}.main\`
3. Check output

## References
- [API Reference](references/REFERENCE.md)
EOF

# REFERENCE.md 作成
cat > "$SKILL_PATH/references/REFERENCE.md" << EOF
# Reference for $SKILL_NAME

Detailed documentation, edge cases, and API specifications belong here.
EOF

# pyproject.toml 作成
cat > "$SKILL_PATH/pyproject.toml" << EOF
[project]
name = "$SKILL_NAME"
version = "0.1.0"
description = "$DESCRIPTION"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "common",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/${SKILL_NAME//-/_}"]

[tool.uv.sources]
common = { workspace = true }
EOF

# README.md 作成
cat > "$SKILL_PATH/README.md" << EOF
# $SKILL_NAME

$DESCRIPTION

See [SKILL.md](SKILL.md) for agent instructions.
EOF

# src/__init__.py 作成
touch "$SKILL_PATH/src/${SKILL_NAME//-/_}/__init__.py"

# src/main.py 作成
cat > "$SKILL_PATH/src/${SKILL_NAME//-/_}/main.py" << EOF
def hello_skill() -> str:
    """初期実装のサンプル関数です"""
    return "Hello from $SKILL_NAME skill!"

if __name__ == "__main__":
    print(hello_skill())
EOF

# tests/test_main.py 作成
cat > "$SKILL_PATH/tests/test_main.py" << EOF
from ${SKILL_NAME//-/_}.main import hello_skill

def test_hello_skill():
    assert hello_skill() == "Hello from $SKILL_NAME skill!"
EOF

echo "✅ Skill scaffold created at $SKILL_PATH"
echo "⚠️ Don't forget to add '$SKILL_NAME = { workspace = true }' to the root pyproject.toml mapping!"
EOF
