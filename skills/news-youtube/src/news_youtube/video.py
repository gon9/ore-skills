"""ffmpegで音声+静止画からMP4動画を生成する."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def generate_video(
    audio_path: str | Path,
    output_path: str | Path,
    title: str = "owlclaw AI Digest",
    thumbnail_path: str | Path | None = None,
) -> Path:
    """音声と静止画からMP4動画を生成する.

    Args:
        audio_path: 入力MP3ファイルのパス
        output_path: 出力MP4ファイルのパス
        title: サムネイルに表示するタイトル
        thumbnail_path: カスタムサムネイル画像パス (None=自動生成)

    Returns:
        生成されたMP4ファイルのパス
    """
    audio_path = Path(audio_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if thumbnail_path is None:
        tmp_thumb = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        _generate_thumbnail(tmp_thumb.name, title)
        thumbnail_path = tmp_thumb.name
        cleanup_thumb = True
    else:
        thumbnail_path = str(thumbnail_path)
        cleanup_thumb = False

    try:
        _run_ffmpeg(str(thumbnail_path), str(audio_path), str(output_path))
    finally:
        if cleanup_thumb:
            Path(thumbnail_path).unlink(missing_ok=True)

    return output_path


def _generate_thumbnail(output_path: str, title: str) -> None:
    """デフォルトサムネイル画像を生成する."""
    width, height = 1280, 720
    img = Image.new("RGB", (width, height), color=(15, 15, 35))
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except OSError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((width // 2, height // 3), "owlclaw", fill=(255, 180, 50), font=font_large, anchor="mm")
    draw.text((width // 2, height // 2), title, fill=(220, 220, 220), font=font_small, anchor="mm")

    img.save(output_path)


def _run_ffmpeg(image_path: str, audio_path: str, output_path: str) -> None:
    """ffmpegで静止画+音声をMP4に合成する."""
    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        image_path,
        "-i",
        audio_path,
        "-c:v",
        "libx264",
        "-tune",
        "stillimage",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-pix_fmt",
        "yuv420p",
        "-shortest",
        "-movflags",
        "+faststart",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpegエラー: {result.stderr}")
