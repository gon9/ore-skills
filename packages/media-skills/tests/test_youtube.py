import pytest
from unittest.mock import patch, MagicMock
from media_skills.youtube import get_youtube_transcript

@patch("media_skills.youtube.TextFormatter")
@patch("media_skills.youtube.YouTubeTranscriptApi")
def test_get_youtube_transcript_success(mock_api, mock_formatter_cls):
    # モックの設定
    mock_transcript = [{"text": "Hello", "start": 0.0, "duration": 1.0}]
    mock_api.get_transcript.return_value = mock_transcript
    
    # Formatterのモック設定
    mock_formatter_instance = mock_formatter_cls.return_value
    mock_formatter_instance.format_transcript.return_value = "Hello"
    
    # 実行
    result = get_youtube_transcript("video123")
    
    # 検証
    assert "Hello" in result
    mock_api.get_transcript.assert_called_once_with("video123", languages=['ja', 'en'])
    mock_formatter_instance.format_transcript.assert_called_once_with(mock_transcript)

@patch("media_skills.youtube.YouTubeTranscriptApi")
def test_get_youtube_transcript_failure(mock_api):
    # エラーを発生させる
    mock_api.get_transcript.side_effect = Exception("Video not found")
    
    with pytest.raises(Exception) as excinfo:
        get_youtube_transcript("invalid_id")
    
    assert "Video not found" in str(excinfo.value)
