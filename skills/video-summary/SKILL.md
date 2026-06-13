---
name: video-summary
description: Extracts audio from video files, transcribes speech using Whisper API, and summarizes the content. Use when the user wants to summarize a video, transcribe audio, or extract key points from video content.
compatibility: Requires ffmpeg and OPENAI_API_KEY (for Whisper transcription)
---

# Video Summary

動画ファイルから音声を抽出し、文字起こしを行い、要約を生成するスキル。

## Workflow

```
動画ファイル (.mp4, .mkv, etc.)
  ↓ Step 1: 音声抽出 (scripts/extract_audio.py)
音声ファイル (.mp3)
  ↓ Step 2: 文字起こし (scripts/transcribe.py)
文字起こしテキスト (.json or .txt)
  ↓ Step 3: 要約 (エージェントが直接実行)
要約テキスト
```

## Step 1: 音声抽出

```bash
uv run scripts/extract_audio.py <video_path> <output_audio.mp3>
```

- ffmpeg を使用して動画から音声を抽出する
- 出力形式は MP3 (最高品質)

## Step 2: 文字起こし

```bash
uv run scripts/transcribe.py <audio.mp3> <output_transcript.json>
```

- OpenAI Whisper API を使用 (OPENAI_API_KEY が必要)
- `.json` 出力: タイムスタンプ付き verbose_json 形式
- `.txt` 出力: テキストのみ

## Step 3: 要約

文字起こしテキストを読み取り、以下の形式で要約を生成すること:

1. 文字起こしファイルの内容を読む
2. 以下のガイドラインに従って要約を作成する:
   - 主要なポイント、結論、重要な事実を簡潔にまとめる
   - 箇条書きと短い段落を組み合わせて構造化する
   - 日本語で出力する
3. 要約結果をファイルに保存する

## Gotchas

- ffmpeg がインストールされていない場合、Step 1 が失敗する
- Whisper API は長い音声ファイル (25MB超) を分割する必要がある場合がある
- 文字起こしの精度は音声品質に依存する
