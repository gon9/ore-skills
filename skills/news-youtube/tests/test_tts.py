"""TTSモジュールのテスト."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from news_youtube.tts import generate_audio


class TestGenerateAudio:
    """音声生成のテスト."""

    @patch("news_youtube.tts.gTTS")
    def test_generates_mp3(self, mock_gtts_class: MagicMock) -> None:
        """gTTSが呼び出されてファイルが保存されることを確認."""
        mock_instance = MagicMock()
        mock_gtts_class.return_value = mock_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.mp3"
            result = generate_audio("テストテキスト", output)

            mock_gtts_class.assert_called_once_with(text="テストテキスト", lang="ja", slow=False)
            mock_instance.save.assert_called_once_with(str(output))
            assert result == output

    @patch("news_youtube.tts.gTTS")
    def test_creates_parent_dir(self, mock_gtts_class: MagicMock) -> None:
        """親ディレクトリが自動作成されることを確認."""
        mock_gtts_class.return_value = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "subdir" / "test.mp3"
            generate_audio("テスト", output)
            assert output.parent.exists()

    @patch("news_youtube.tts.gTTS")
    def test_custom_lang(self, mock_gtts_class: MagicMock) -> None:
        """言語指定のテスト."""
        mock_gtts_class.return_value = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.mp3"
            generate_audio("test text", output, lang="en")
            mock_gtts_class.assert_called_once_with(text="test text", lang="en", slow=False)
