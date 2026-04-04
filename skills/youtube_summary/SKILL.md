---
name: youtube_summary
description: Extracts YouTube video transcripts and manages fallback to whisper-based transcription. Use when you need to summarize or extract text from a YouTube video.
license: MIT
compatibility: Requires Python 3.12+
---

# YouTube Summary Skill

## Overview
This skill provides a robust pipeline for extracting transcripts from YouTube videos. It attempts to fetch transcripts via the YouTube API (`youtube-transcript-api`), falls back to `yt-dlp` auto-subs, and if all fails, it will download the video's audio and transcribe it locally using `faster-whisper`. 

Once the transcript is generated, AI agents can read the resulting text file to summarize the video, generate notes, or run further analysis.

## Usage

### 1. Generating a Transcript
To extract the transcript for a video, run the CLI tool passing the YouTube URL:

```bash
uv run youtube-summary "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

The tool will:
1. Try to fetch captions via API.
2. If unavailable, download audio and transcribe it using Whisper.
3. Save the output to `transcript_<video_id>.txt` in the current directory.

### 2. Generating the Summary (AI Task)
After the tool successfully outputs `transcript_<video_id>.txt`, use your `read_file` tools to read the transcript file. Then, use LLM capabilities to summarize the content (e.g., extracting structure, introduction, problems, solutions, and conclusion).

### Fallback to Web Search
If a video has no audio or transcription completely fails, you may resort to:
1. Getting the video title.
2. Using `search_web` with `"[Video Title]" summary` to find existing summaries or articles covering the same content.
