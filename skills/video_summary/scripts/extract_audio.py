# /// script
# dependencies = []
# requires-python = ">=3.12"
# ///
"""動画ファイルから音声を抽出する。

Usage:
    uv run scripts/extract_audio.py <video_path> <output_audio_path>

依存: ffmpeg (システムにインストール済みであること)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def extract_audio(video_path: str, output_audio_path: str) -> Path:
    """動画ファイルから音声を抽出し MP3 として保存する。"""
    video_path_obj = Path(video_path)
    output_audio_path_obj = Path(output_audio_path)

    if not video_path_obj.exists():
        print(f"ERROR: 動画ファイルが見つかりません: {video_path}", file=sys.stderr)
        sys.exit(1)

    output_audio_path_obj.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-i",
        str(video_path_obj),
        "-q:a",
        "0",
        "-map",
        "a",
        "-y",
        str(output_audio_path_obj),
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"OK: {output_audio_path_obj}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: ffmpeg 失敗: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: ffmpeg が見つかりません。インストールしてください。", file=sys.stderr)
        sys.exit(1)

    return output_audio_path_obj


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="動画ファイルから音声を抽出する")
    parser.add_argument("video_path", help="入力動画ファイルのパス")
    parser.add_argument("output_audio_path", help="出力MP3ファイルのパス")
    args = parser.parse_args()
    extract_audio(args.video_path, args.output_audio_path)
