"""rules-generator のエントリポイント。"""

from __future__ import annotations

import argparse
from pathlib import Path

from rules_generator.generator import generate_rules_md
from rules_generator.scanner import scan_project


def main() -> None:
    """プロジェクトを解析してルールファイルを生成する。"""
    parser = argparse.ArgumentParser(description="プロジェクトを解析してルールファイルを生成する")
    parser.add_argument("project_root", help="プロジェクトルートのパス")
    parser.add_argument(
        "--format",
        choices=["CLAUDE.md", "AGENTS.md", ".cursorrules"],
        default="CLAUDE.md",
        help="出力フォーマット (デフォルト: CLAUDE.md)",
    )
    parser.add_argument(
        "--output",
        help="出力ファイルパス (省略時は stdout)",
    )
    args = parser.parse_args()

    info = scan_project(args.project_root)
    md = generate_rules_md(info, args.format)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(md, encoding="utf-8")
        print(f"✅ {output_path} を生成しました")
    else:
        print(md)


if __name__ == "__main__":
    main()
