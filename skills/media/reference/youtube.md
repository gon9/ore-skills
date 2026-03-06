# YouTube Transcript Functions

## Overview
This reference provides detailed information about the YouTube transcript functionality available in the Media skill.

## `get_youtube_transcript`

Fetches and formats the transcript of a YouTube video.

### Arguments
- `video_id` (str): The ID of the YouTube video (e.g., `dQw4w9WgXcQ`).
- `languages` (list[str], optional): List of language codes to prefer (default: `['ja', 'en']`).

### Usage Example (Python)

```python
from media.youtube import get_youtube_transcript

transcript = get_youtube_transcript("dQw4w9WgXcQ")
print(transcript)
```

### CLI Usage
You can execute the script directly to fetch a transcript without writing Python code.

```bash
# Basic usage (defaults to Japanese, then English)
uv run -m media.youtube dQw4w9WgXcQ

# Specify languages
uv run -m media.youtube dQw4w9WgXcQ --lang en ja
```

### Error Handling
- If the video ID is invalid or the video is private, an exception will be raised.
- If no transcript is available in the requested languages, an exception will be raised.
