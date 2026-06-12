"""videoモジュールのテスト."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from news_youtube.video import _generate_thumbnail, generate_video


class TestGenerateThumbnail:
    """サムネイル生成のテスト."""

    def test_creates_png(self) -> None:
        """PNG画像が生成されることを確認."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            _generate_thumbnail(f.name, "Test Title")
            path = Path(f.name)
            assert path.exists()
            assert path.stat().st_size > 0
            path.unlink()


class TestGenerateVideo:
    """動画生成のテスト."""

    @patch("news_youtube.video._run_ffmpeg")
    def test_auto_thumbnail(self, mock_ffmpeg: MagicMock) -> None:
        """サムネイル未指定時に自動生成されることを確認."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audio = Path(tmpdir) / "test.mp3"
            audio.write_bytes(b"dummy")
            output = Path(tmpdir) / "test.mp4"

            generate_video(audio, output, title="Test")

            mock_ffmpeg.assert_called_once()
            args = mock_ffmpeg.call_args[0]
            assert args[1] == str(audio)
            assert args[2] == str(output)

    @patch("news_youtube.video._run_ffmpeg")
    def test_custom_thumbnail(self, mock_ffmpeg: MagicMock) -> None:
        """カスタムサムネイル指定時にそのパスが使用されることを確認."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audio = Path(tmpdir) / "test.mp3"
            audio.write_bytes(b"dummy")
            thumb = Path(tmpdir) / "thumb.png"
            thumb.write_bytes(b"dummy_png")
            output = Path(tmpdir) / "test.mp4"

            generate_video(audio, output, thumbnail_path=thumb)

            args = mock_ffmpeg.call_args[0]
            assert args[0] == str(thumb)
