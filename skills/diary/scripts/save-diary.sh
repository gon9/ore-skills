#!/bin/bash

# 日記ファイルを指定されたディレクトリ（デフォルト: 00_Inbox）に保存するスクリプト

set -e

# 引数のパース
FILE_PATH=""
TARGET_DIR="00_Inbox"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --file) FILE_PATH="$2"; shift ;;
        --dir) TARGET_DIR="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [ -z "$FILE_PATH" ]; then
    echo "Error: --file argument is required."
    echo "Usage: $0 --file <path/to/diary.md> [--dir <target_directory_name>]"
    exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File not found: $FILE_PATH"
    exit 1
fi

# Vault パスの確認
if [ -z "$OBSIDIAN_VAULT_DIR" ]; then
    echo "Error: OBSIDIAN_VAULT_DIR environment variable is not set."
    echo "Please set it to your Obsidian Vault path (e.g., export OBSIDIAN_VAULT_DIR=/path/to/vault)"
    exit 1
fi

if [ ! -d "$OBSIDIAN_VAULT_DIR" ]; then
    echo "Error: Obsidian Vault directory not found: $OBSIDIAN_VAULT_DIR"
    exit 1
fi

# 保存先ディレクトリの作成とファイルコピー
TARGET_PATH="$OBSIDIAN_VAULT_DIR/$TARGET_DIR"

if [ ! -d "$TARGET_PATH" ]; then
    echo "Creating target directory: $TARGET_PATH"
    mkdir -p "$TARGET_PATH"
fi

FILENAME=$(basename "$FILE_PATH")
DESTINATION="$TARGET_PATH/$FILENAME"

cp "$FILE_PATH" "$DESTINATION"

echo "Successfully saved diary to: $DESTINATION"
