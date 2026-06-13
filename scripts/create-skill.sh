#!/usr/bin/env bash

# create-skill.sh: ore-skills の新しいスキル雛形を生成する。

set -euo pipefail

usage() {
    cat <<'EOF'
Usage: scripts/create-skill.sh <skill-name> "<description>" [options]

Options:
  --python                         Python package scaffoldも作成する
  --resources=references,scripts   追加する任意ディレクトリ
  --path=<skills-dir>              生成先 skills ディレクトリ (default: repo skills/)
  --license=<license>              frontmatter の license 値 (default: MIT)
  --compatibility=<text>           frontmatter の compatibility 値
  -h, --help                       ヘルプを表示する

Examples:
  scripts/create-skill.sh prompt-review "Reviews prompts. Use when improving AI prompts."
  scripts/create-skill.sh pdf-tools "Works with PDFs. Use when extracting or editing PDFs." --resources=scripts,references
  scripts/create-skill.sh git-helper "Automates git workflows. Use when preparing commits." --python
EOF
}

if [ $# -eq 0 ]; then
    usage
    exit 1
fi

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    usage
    exit 0
fi

if [ $# -lt 2 ]; then
    usage
    exit 1
fi

SKILL_NAME="$1"
DESCRIPTION="$2"
shift 2

WITH_PYTHON=false
RESOURCE_LIST=""
LICENSE_VALUE="MIT"
COMPATIBILITY_VALUE=""
SKILLS_DIR="$(dirname "$0")/../skills"

for arg in "$@"; do
    case "$arg" in
        --python)
            WITH_PYTHON=true
            ;;
        --resources=*)
            RESOURCE_LIST="${arg#--resources=}"
            ;;
        --path=*)
            SKILLS_DIR="${arg#--path=}"
            ;;
        --license=*)
            LICENSE_VALUE="${arg#--license=}"
            ;;
        --compatibility=*)
            COMPATIBILITY_VALUE="${arg#--compatibility=}"
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Error: unknown option: $arg" >&2
            usage >&2
            exit 2
            ;;
    esac
done

SKILL_PATH="$SKILLS_DIR/$SKILL_NAME"
PACKAGE_NAME="${SKILL_NAME//-/_}"

if ! [[ "$SKILL_NAME" =~ ^[a-z0-9]([a-z0-9-]{0,62}[a-z0-9])?$ ]]; then
    echo "Error: skill name must be 1-64 lowercase letters, numbers, or hyphens, and must not start/end with hyphen." >&2
    exit 1
fi

if [[ "$SKILL_NAME" == *--* ]]; then
    echo "Error: skill name must not contain consecutive hyphens." >&2
    exit 1
fi

if [ ${#DESCRIPTION} -gt 1024 ]; then
    echo "Error: description must be 1024 characters or fewer." >&2
    exit 1
fi

if [ -d "$SKILL_PATH" ]; then
    echo "Error: skill '$SKILL_NAME' already exists." >&2
    exit 1
fi

yaml_quote() {
    local value="$1"
    value="${value//\\/\\\\}"
    value="${value//\"/\\\"}"
    printf '"%s"' "$value"
}

has_resource() {
    local needle="$1"
    local item
    IFS=',' read -ra items <<< "$RESOURCE_LIST"
    for item in "${items[@]}"; do
        if [ "$item" = "$needle" ]; then
            return 0
        fi
    done
    return 1
}

echo "Creating skill '$SKILL_NAME'..."
mkdir -p "$SKILL_PATH"

{
    echo "---"
    echo "name: $SKILL_NAME"
    printf "description: "
    yaml_quote "$DESCRIPTION"
    echo
    if [ -n "$LICENSE_VALUE" ]; then
        printf "license: "
        yaml_quote "$LICENSE_VALUE"
        echo
    fi
    if [ -n "$COMPATIBILITY_VALUE" ]; then
        printf "compatibility: "
        yaml_quote "$COMPATIBILITY_VALUE"
        echo
    fi
    echo "---"
    echo
    echo "# $SKILL_NAME"
    echo
    echo "## Workflow"
    echo
    echo "1. Confirm the user request matches this skill."
    echo "2. Follow the task-specific procedure."
    echo "3. Validate the result before responding."
    echo
    echo "## Gotchas"
    echo
    echo "- Keep instructions concise and specific to this skill."
    echo "- Move long details to references/ only when they are needed."
} > "$SKILL_PATH/SKILL.md"

if has_resource "references"; then
    mkdir -p "$SKILL_PATH/references"
fi

if has_resource "scripts"; then
    mkdir -p "$SKILL_PATH/scripts"
fi

if has_resource "assets"; then
    mkdir -p "$SKILL_PATH/assets"
fi

if [ "$WITH_PYTHON" = true ]; then
    mkdir -p "$SKILL_PATH/src/$PACKAGE_NAME"
    mkdir -p "$SKILL_PATH/tests"

    {
        echo "[project]"
        echo "name = \"$SKILL_NAME\""
        echo "version = \"0.1.0\""
        echo "description = \"$DESCRIPTION\""
        echo "readme = \"SKILL.md\""
        echo "requires-python = \">=3.12\""
        echo "dependencies = []"
        echo
        echo "[build-system]"
        echo "requires = [\"hatchling\"]"
        echo "build-backend = \"hatchling.build\""
        echo
        echo "[tool.hatch.build.targets.wheel]"
        echo "packages = [\"src/$PACKAGE_NAME\"]"
    } > "$SKILL_PATH/pyproject.toml"

    touch "$SKILL_PATH/src/$PACKAGE_NAME/__init__.py"
    {
        echo "def hello_skill() -> str:"
        echo "    \"\"\"初期実装のサンプル関数です。\"\"\""
        echo "    return \"Hello from $SKILL_NAME skill!\""
    } > "$SKILL_PATH/src/$PACKAGE_NAME/main.py"

    {
        echo "from $PACKAGE_NAME.main import hello_skill"
        echo
        echo
        echo "def test_hello_skill() -> None:"
        echo "    assert hello_skill() == \"Hello from $SKILL_NAME skill!\""
    } > "$SKILL_PATH/tests/test_main.py"
fi

python3 "$(dirname "$0")/validate-skills.py" "$SKILL_PATH/.." >/dev/null

echo "Skill scaffold created at $SKILL_PATH"
if [ "$WITH_PYTHON" = true ]; then
    echo "Python scaffold created. Add the skill to root pyproject.toml workspace members if it should be installable."
fi
