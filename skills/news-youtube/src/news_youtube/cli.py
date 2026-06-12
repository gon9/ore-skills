"""news-youtube CLIエントリポイント."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from news_youtube.parser import parse_owlclaw_daily, to_speech_script
from news_youtube.tts import generate_audio
from news_youtube.uploader import UploadParams, upload_video
from news_youtube.video import generate_video


def main() -> None:
    """CLIメインエントリポイント."""
    parser = argparse.ArgumentParser(
        description="owlclawニュースをYouTube動画としてアップロードする",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("markdown_path", help="owlclaw日次ダイジェストMarkdownファイルのパス")
    parser.add_argument("--audio-only", action="store_true", help="音声ファイルのみ生成")
    parser.add_argument("--video-only", action="store_true", help="動画ファイルのみ生成 (アップロードしない)")
    parser.add_argument("--output-dir", type=str, default=None, help="出力ディレクトリ (デフォルト: 一時ディレクトリ)")
    parser.add_argument("--thumbnail", type=str, default=None, help="サムネイル画像パス")
    parser.add_argument(
        "--client-secret",
        type=str,
        default=None,
        help="YouTube OAuth client_secret.json のパス (env: YOUTUBE_CLIENT_SECRET_PATH)",
    )
    parser.add_argument(
        "--privacy",
        type=str,
        default="public",
        choices=["public", "unlisted", "private"],
        help="公開設定 (デフォルト: public)",
    )

    args = parser.parse_args()

    md_path = Path(args.markdown_path)
    if not md_path.exists():
        print(f"エラー: ファイルが見つかりません: {md_path}", file=sys.stderr)
        sys.exit(1)

    print(f"解析中: {md_path}", file=sys.stderr)
    digest = parse_owlclaw_daily(md_path)
    script = to_speech_script(digest)

    print(f"日付: {digest.date} / 記事数: {len(digest.stories)}", file=sys.stderr)

    if args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path(tempfile.mkdtemp(prefix="news-youtube-"))

    audio_path = output_dir / f"owlclaw-{digest.date}.mp3"
    print(f"音声生成中: {audio_path}", file=sys.stderr)
    generate_audio(script, audio_path)
    print(f"音声生成完了: {audio_path}", file=sys.stderr)

    if args.audio_only:
        print(f"出力: {audio_path}")
        return

    title = f"owlclaw AI Digest {digest.date}"
    video_path = output_dir / f"owlclaw-{digest.date}.mp4"
    print(f"動画生成中: {video_path}", file=sys.stderr)
    generate_video(
        audio_path=audio_path,
        output_path=video_path,
        title=title,
        thumbnail_path=args.thumbnail,
    )
    print(f"動画生成完了: {video_path}", file=sys.stderr)

    if args.video_only:
        print(f"出力: {video_path}")
        return

    description = _build_description(digest, script)
    print("YouTubeアップロード中...", file=sys.stderr)
    params = UploadParams(
        video_path=video_path,
        title=title,
        description=description,
        client_secret_path=args.client_secret,
        privacy_status=args.privacy,
    )
    video_id = upload_video(params)
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"アップロード完了: {video_url}", file=sys.stderr)
    print(video_url)


def _build_description(digest, script: str) -> str:
    """YouTube動画の説明文を生成する."""
    lines: list[str] = []
    lines.append(f"owlclaw AI Digest {digest.date}")
    lines.append("")
    lines.append("AI/SaaS 関連の最新ニュースを毎日お届け。")
    lines.append("Google Home で「OK Google, YouTube で owlclaw を再生」と話しかけてください。")
    lines.append("")
    lines.append("--- 目次 ---")
    for story in digest.stories:
        lines.append(f"{story.number}. {story.title}")
    lines.append("")
    lines.append("#owlclaw #AI #ニュース #テック #SaaS")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
