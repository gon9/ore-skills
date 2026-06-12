"""uploaderモジュールのテスト."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from news_youtube.uploader import UploadParams, upload_video


class TestUploadVideo:
    """YouTubeアップロードのテスト."""

    def test_missing_file_raises(self) -> None:
        """存在しないファイルでFileNotFoundErrorが発生することを確認."""
        params = UploadParams(
            video_path="/nonexistent/video.mp4",
            title="Test",
            description="Test",
            client_secret_path="/dummy/secret.json",
        )
        with pytest.raises(FileNotFoundError, match="動画ファイルが見つかりません"):
            upload_video(params)

    @patch("news_youtube.uploader.build")
    @patch("news_youtube.uploader.get_credentials")
    def test_upload_returns_video_id(
        self,
        mock_get_creds: MagicMock,
        mock_build: MagicMock,
    ) -> None:
        """アップロード成功時に動画IDが返されることを確認."""
        mock_get_creds.return_value = MagicMock()

        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube
        mock_request = MagicMock()
        mock_request.next_chunk.return_value = (None, {"id": "test_video_id"})
        mock_youtube.videos.return_value.insert.return_value = mock_request

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(b"dummy video content")
            f.flush()

            params = UploadParams(
                video_path=f.name,
                title="Test Title",
                description="Test Description",
                client_secret_path="/dummy/secret.json",
            )
            video_id = upload_video(params)

            assert video_id == "test_video_id"
            Path(f.name).unlink()
