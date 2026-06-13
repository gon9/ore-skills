# /// script
# dependencies = [
#     "openai>=1.0.0",
# ]
# requires-python = ">=3.12"
# ///
"""音声ファイルから Whisper API で文字起こしを行う。

Usage:
    uv run scripts/transcribe.py <audio_path> <output_path>

出力形式は拡張子で決定:
  - .json: verbose_json (タイムスタンプ付き)
  - .txt:  テキストのみ

依存: OPENAI_API_KEY 環境変数
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from openai import OpenAI


def transcribe_audio(audio_path: str, output_path: str) -> Path:
    """Whisper API で音声を文字起こしする。"""
    audio_path_obj = Path(audio_path)
    output_path_obj = Path(output_path)

    if not audio_path_obj.exists():
        print(f"ERROR: 音声ファイルが見つかりません: {audio_path}", file=sys.stderr)
        sys.exit(1)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY が設定されていません。", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(audio_path_obj, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
            )

        if output_path_obj.suffix.lower() == ".json":
            with open(output_path_obj, "w", encoding="utf-8") as f:
                json.dump(transcript.model_dump(), f, ensure_ascii=False, indent=2)
        else:
            with open(output_path_obj, "w", encoding="utf-8") as f:
                f.write(transcript.text)

        print(f"OK: {output_path_obj}")
    except Exception as e:
        print(f"ERROR: 文字起こし失敗: {e}", file=sys.stderr)
        sys.exit(1)

    return output_path_obj


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Whisper API で音声を文字起こしする")
    parser.add_argument("audio_path", help="入力音声ファイルのパス")
    parser.add_argument("output_path", help="出力ファイルのパス (.json or .txt)")
    args = parser.parse_args()
    transcribe_audio(args.audio_path, args.output_path)
