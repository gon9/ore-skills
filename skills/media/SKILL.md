---
name: media
description: Fetches and processes YouTube video transcripts for analysis, summarization, and content extraction. Use when working with YouTube videos, video transcripts, or when the user mentions YouTube, video content analysis, or transcript extraction.
---

# Media Skill

## Overview
This skill provides tools for processing media content, currently focusing on YouTube videos.

## Capabilities

### YouTube Transcript
Fetch text transcripts from YouTube videos. Useful for summarization, analysis, or extraction of information from video content.

- **Implementation**: `src/media/youtube.py`
- **Reference**: See [references/youtube.md](references/youtube.md) for detailed API and CLI usage.

## Usage

### Fetching a Transcript
You can run the python module directly to get the transcript output to stdout.

```bash
uv run -m media.youtube <video_id>
```

Example:
```bash
uv run -m media.youtube dQw4w9WgXcQ
```
