import argparse
import datetime
import os
import re

import pytz


def generate_frontmatter(date_str: str, tags: list[str]) -> str:
    """
    Obsidian形式のFrontmatterを生成する
    """
    now = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
    created_at = now.isoformat(timespec="seconds")
    
    tags_yaml = "\n".join([f"  - {tag}" for tag in tags])
    
    return f"""---
date: {date_str}
tags:
{tags_yaml}
created: {created_at}
---"""

def build_filename(date_str: str, title: str) -> str:
    """
    日付とタイトルからファイル名を生成する
    例: 2026-04-04_ai-agent-potential.md
    """
    # 簡易的なslug化(実際にはLLMに英語の短いslugを生成させる想定)
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
    
    # 全て日本語などでslugが空になった場合のフォールバック
    if not slug:
        slug = "entry"
        
    return f"{date_str}_{slug}.md"

def get_vault_path() -> str | None:
    """
    環境変数からObsidian Vaultのパスを取得する
    """
    return os.environ.get("OBSIDIAN_VAULT_DIR")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Diary Utility")
    parser.add_argument("command", choices=["filename"])
    parser.add_argument("--date", required=True)
    parser.add_argument("--title", required=True)
    
    args = parser.parse_args()
    
    if args.command == "filename":
        print(build_filename(args.date, args.title))
