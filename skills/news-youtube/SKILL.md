---
name: news-youtube
description: owlclawニュースMarkdownをTTS音声に変換し、YouTube動画としてアップロードする。Google Homeから「OK Google」で再生可能にする。
license: MIT
compatibility: Python 3.12+, ffmpeg
---

# news-youtube

## Overview
owlclaw が生成する日次AIニュースダイジェスト (Markdown) を、音声付き動画としてYouTubeにアップロードするパイプライン。
Google Home / Nest デバイスから「OK Google, YouTubeで owlclaw を再生」で最新ニュースを聴取可能にする。

## Capabilities

### 1. Markdown Parser
owlclaw 日次ダイジェストの Markdown を解析し、音声読み上げに適したスクリプトテキストを生成する。

### 2. TTS (Text-to-Speech)
gTTS を使用して日本語テキストを MP3 音声に変換する。

### 3. Video Generator
ffmpeg で静止画と音声を合成し、YouTube アップロード用の MP4 動画を生成する。

### 4. YouTube Uploader
YouTube Data API v3 (OAuth 2.0) で既存チャネルに動画をアップロードする。

## Usage

### CLI
```bash
# 日次ダイジェストを動画化してアップロード
uv run news-youtube /path/to/20_news/owlclaw/daily/2026-06-11.md

# 音声ファイルのみ生成 (アップロードしない)
uv run news-youtube --audio-only /path/to/daily/2026-06-11.md

# 動画ファイルのみ生成 (アップロードしない)
uv run news-youtube --video-only /path/to/daily/2026-06-11.md
```

### 環境変数
| 変数名 | 説明 | 必須 |
|--------|------|------|
| `YOUTUBE_CLIENT_SECRET_PATH` | OAuth 2.0 client_secret.json のパス | アップロード時 |
| `YOUTUBE_TOKEN_PATH` | OAuth トークンキャッシュのパス (デフォルト: `~/.config/news-youtube/token.json`) | - |
| `NEWS_YOUTUBE_THUMBNAIL` | サムネイル画像のパス (デフォルト: 内蔵デフォルト画像を自動生成) | - |

## References
- [YouTube Data API v3](references/youtube-api.md)
