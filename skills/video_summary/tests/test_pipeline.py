import json
import os
from unittest.mock import MagicMock, patch

import pytest
from video_summary.extractor import extract_audio
from video_summary.pipeline import process_video
from video_summary.summarizer import generate_summary
from video_summary.transcriber import transcribe_audio


@pytest.fixture
def temp_video_file(tmp_path):
    video_file = tmp_path / "test_video.mp4"
    video_file.write_text("dummy video content")
    return video_file


@pytest.fixture
def temp_audio_file(tmp_path):
    audio_file = tmp_path / "test_audio.mp3"
    audio_file.write_text("dummy audio content")
    return audio_file


@pytest.fixture
def temp_transcript_json(tmp_path):
    transcript_file = tmp_path / "test_transcript.json"
    json.dump({"text": "テスト用の文字起こしテキストです。"}, transcript_file.open("w", encoding="utf-8"))
    return transcript_file


@pytest.fixture
def temp_transcript_txt(tmp_path):
    transcript_file = tmp_path / "test_transcript.txt"
    transcript_file.write_text("テスト用の文字起こしテキストです。", encoding="utf-8")
    return transcript_file


def test_extract_audio_file_not_found():
    with pytest.raises(FileNotFoundError):
        extract_audio("non_existent_video.mp4", "output.mp3")


@patch("subprocess.run")
def test_extract_audio_success(mock_run, temp_video_file, tmp_path):
    output_audio = tmp_path / "output.mp3"
    result = extract_audio(temp_video_file, output_audio)

    assert result == output_audio
    mock_run.assert_called_once()
    assert mock_run.call_args[0][0][0] == "ffmpeg"


@patch.dict(os.environ, {}, clear=True)
def test_transcribe_audio_no_api_key(temp_audio_file, tmp_path):
    output_text = tmp_path / "output.txt"
    with pytest.raises(RuntimeError, match="API_KEY"):
        transcribe_audio(temp_audio_file, output_text)


@patch.dict(os.environ, {"OPENAI_API_KEY": "dummy_key"})
@patch("video_summary.transcriber.OpenAI")
def test_transcribe_audio_success(mock_openai, temp_audio_file, tmp_path):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_transcript = MagicMock()
    mock_transcript.text = "テストテキスト"
    mock_transcript.model_dump.return_value = {"text": "テストテキスト", "segments": []}
    mock_client.audio.transcriptions.create.return_value = mock_transcript

    output_json = tmp_path / "output.json"
    result = transcribe_audio(temp_audio_file, output_json)

    assert result == output_json
    assert output_json.exists()

    with open(output_json, encoding="utf-8") as f:
        data = json.load(f)
        assert data["text"] == "テストテキスト"


@patch("video_summary.summarizer.chat_completion")
def test_generate_summary_json_success(mock_chat, temp_transcript_json, tmp_path):
    mock_chat.return_value = MagicMock(
        content="要約テキストです。",
        provider="openai",
        model="gpt-4o-mini",
    )

    output_summary = tmp_path / "summary.txt"
    result = generate_summary(temp_transcript_json, output_summary)

    assert result == output_summary
    assert output_summary.exists()
    assert output_summary.read_text(encoding="utf-8") == "要約テキストです。"
    mock_chat.assert_called_once()


@patch("video_summary.summarizer.chat_completion")
def test_generate_summary_txt_success(mock_chat, temp_transcript_txt, tmp_path):
    mock_chat.return_value = MagicMock(
        content="要約テキストです。",
        provider="anthropic",
        model="claude-sonnet-4-20250514",
    )

    output_summary = tmp_path / "summary.txt"
    result = generate_summary(temp_transcript_txt, output_summary)

    assert result == output_summary
    assert output_summary.exists()
    assert output_summary.read_text(encoding="utf-8") == "要約テキストです。"
    mock_chat.assert_called_once()


@patch("video_summary.pipeline.extract_audio")
@patch("video_summary.pipeline.transcribe_audio")
@patch("video_summary.pipeline.generate_summary")
def test_process_video(mock_generate, mock_transcribe, mock_extract, temp_video_file, tmp_path):
    # パイプラインが正しく各関数を呼び出すかテスト
    output_dir = tmp_path / "output"
    result = process_video(temp_video_file, output_dir)

    assert mock_extract.called
    assert mock_transcribe.called
    assert mock_generate.called
    assert result.name == "test_video_summary.txt"
    assert result.parent == output_dir
