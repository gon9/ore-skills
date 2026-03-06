---
name: media
description: Media processing capabilities, including fetching YouTube transcripts. Use for video content analysis.
---

# Media Skill

## Overview
This skill provides tools for processing media content, currently focusing on YouTube videos.

## Capabilities

### YouTube Transcript
Fetch text transcripts from YouTube videos. Useful for summarization, analysis, or extraction of information from video content.

- **Implementation**: `src/media/youtube.py`
- **Reference**: See [reference/youtube.md](reference/youtube.md) for detailed API and CLI usage.

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
