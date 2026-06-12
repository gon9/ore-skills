"""owlclaw日次ダイジェストMarkdownを音声スクリプトに変換するパーサー."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class NewsStory:
    """個別ニュース記事."""

    number: int
    title: str
    source: str
    summary: str
    why_it_matters: str


@dataclass
class DailyDigest:
    """日次ダイジェスト全体."""

    date: str
    stories: list[NewsStory] = field(default_factory=list)


def parse_owlclaw_daily(markdown_path: str | Path) -> DailyDigest:
    """owlclaw日次ダイジェストMarkdownを解析する.

    Args:
        markdown_path: Markdownファイルのパス

    Returns:
        解析済みのDailyDigestオブジェクト
    """
    text = Path(markdown_path).read_text(encoding="utf-8")
    return _parse_markdown(text)


def _parse_markdown(text: str) -> DailyDigest:
    """Markdown本文を解析してDailyDigestを返す."""
    date = _extract_date(text)
    stories = _extract_stories(text)
    return DailyDigest(date=date, stories=stories)


def _extract_date(text: str) -> str:
    """frontmatterまたはタイトルから日付を抽出する."""
    date_match = re.search(r"date:\s*(\d{4}-\d{2}-\d{2})", text)
    if date_match:
        return date_match.group(1)
    title_match = re.search(r"AI Digest\s*(?:--|---)\s*(\d{4}-\d{2}-\d{2})", text)
    if title_match:
        return title_match.group(1)
    return "unknown"


def _extract_stories(text: str) -> list[NewsStory]:
    """ニュース記事を全件抽出する."""
    story_pattern = re.compile(
        r"###\s*(\d+)\.\s*(.+?)(?:\n)"
        r"(?:.*?-\s*\*\*Source\*\*:\s*(.+?)(?:\n))"
        r"(?:.*?-\s*\*\*Link\*\*:.+?(?:\n))"
        r"(?:.*?-\s*\*\*Summary\*\*:\s*\n(.*?))"
        r"(?:-\s*\*\*Why it matters\*\*:\s*(.+?)(?=\n###|\n---|\Z))",
        re.DOTALL,
    )

    stories: list[NewsStory] = []
    for match in story_pattern.finditer(text):
        number = int(match.group(1))
        title = match.group(2).strip()
        source = match.group(3).strip()
        summary = _clean_text(match.group(4))
        why_it_matters = _clean_text(match.group(5))
        stories.append(
            NewsStory(
                number=number,
                title=title,
                source=source,
                summary=summary,
                why_it_matters=why_it_matters,
            )
        )
    return stories


def _clean_text(text: str) -> str:
    """Markdown記法を除去してプレーンテキストにする."""
    text = text.strip()
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    text = re.sub(r"^\s*-\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n\s*\n", "\n", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def to_speech_script(digest: DailyDigest) -> str:
    """DailyDigestを音声読み上げ用スクリプトに変換する.

    Args:
        digest: 解析済みダイジェスト

    Returns:
        読み上げ用テキスト
    """
    lines: list[str] = []
    lines.append(f"owlclaw AIダイジェスト、{_format_date_japanese(digest.date)}。")
    lines.append("")
    lines.append(f"本日のトップニュースは{len(digest.stories)}件です。")
    lines.append("")

    for story in digest.stories:
        lines.append(f"第{story.number}位。{story.title}。")
        lines.append(f"{story.summary}")
        lines.append(f"ポイント: {story.why_it_matters}")
        lines.append("")

    lines.append("以上、owlclaw AIダイジェストでした。")
    return "\n".join(lines)


def _format_date_japanese(date_str: str) -> str:
    """YYYY-MM-DD を日本語日付に変換する."""
    try:
        parts = date_str.split("-")
        return f"{parts[0]}年{int(parts[1])}月{int(parts[2])}日"
    except (IndexError, ValueError):
        return date_str
