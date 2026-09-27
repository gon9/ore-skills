"""youtube_summary.get_youtube_transcript のテスト。"""

from __future__ import annotations

import pytest
from youtube_summary import get_youtube_transcript as gyt


class _Transcript:
    def __init__(self, text: str) -> None:
        self._text = text

    def fetch(self) -> list[dict]:
        return [{"text": self._text}]


class _TranscriptList:
    """list_transcripts の戻り値の代わり。manual / generated が None なら見つからない扱い。"""

    def __init__(self, manual: str | None = None, generated: str | None = None, others: tuple[str, ...] = ()) -> None:
        self.manual = manual
        self.generated = generated
        self.others = others

    def find_manually_created_transcript(self, _languages: list[str]) -> _Transcript:
        if self.manual is None:
            raise LookupError("no manual")
        return _Transcript(self.manual)

    def find_generated_transcript(self, _languages: list[str]) -> _Transcript:
        if self.generated is None:
            raise LookupError("no generated")
        return _Transcript(self.generated)

    def __iter__(self):
        return iter(_Transcript(t) for t in self.others)


def _fake_api(direct: list[dict] | None, listing: _TranscriptList | None):
    class _Api:
        @staticmethod
        def get_transcript(_video_id: str, languages: list[str]) -> list[dict]:
            if direct is None:
                raise RuntimeError("direct failed")
            return direct

        @staticmethod
        def list_transcripts(_video_id: str) -> _TranscriptList:
            if listing is None:
                raise RuntimeError("list failed")
            return listing

    return _Api


# --- get_video_id ---


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.youtube.com/watch?v=abc123&t=10", "abc123"),
        ("https://youtu.be/abc123", "abc123"),
        ("https://youtube.com/embed/abc123", "abc123"),
        ("https://www.youtube.com/v/abc123", "abc123"),
        ("abc123", "abc123"),  # すでに ID
        ("https://example.com/other", "https://example.com/other"),  # 対象外はそのまま返す
    ],
)
def test_get_video_id(url: str, expected: str) -> None:
    assert gyt.get_video_id(url) == expected


# --- clean_vtt ---


def test_clean_vtt_strips_headers_timestamps_tags_and_duplicates() -> None:
    vtt = (
        "WEBVTT\nKind: captions\nLanguage: ja\n\n"
        "00:00:00.000 --> 00:00:01.000\n<c>こんにちは</c>\n\n"
        "00:00:01.000 --> 00:00:02.000\nこんにちは\n  世界  \n"
    )
    assert gyt.clean_vtt(vtt) == "こんにちは\n世界"


def test_clean_vtt_empty() -> None:
    assert gyt.clean_vtt("") == ""


# --- get_transcript_api ---


def test_api_direct_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gyt, "YouTubeTranscriptApi", _fake_api([{"text": "a"}, {"text": "b"}], None))
    assert gyt.get_transcript_api("vid") == "a\nb\n"


@pytest.mark.parametrize(
    ("listing", "expected"),
    [
        (_TranscriptList(manual="手動", generated="自動", others=("en",)), "手動\n"),
        (_TranscriptList(generated="自動", others=("en",)), "自動\n"),
        (_TranscriptList(others=("en", "fr")), "en\n"),
    ],
)
def test_api_falls_back_through_listing(
    monkeypatch: pytest.MonkeyPatch, listing: _TranscriptList, expected: str
) -> None:
    monkeypatch.setattr(gyt, "YouTubeTranscriptApi", _fake_api(None, listing))
    assert gyt.get_transcript_api("vid") == expected


def test_api_returns_none_when_nothing_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gyt, "YouTubeTranscriptApi", _fake_api(None, _TranscriptList()))
    assert gyt.get_transcript_api("vid") is None


def test_api_returns_none_when_listing_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gyt, "YouTubeTranscriptApi", _fake_api(None, None))
    assert gyt.get_transcript_api("vid") is None


def test_api_returns_none_when_library_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gyt, "YouTubeTranscriptApi", None)
    assert gyt.get_transcript_api("vid") is None
