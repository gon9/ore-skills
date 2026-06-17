# Video Summary Skill

## 概要
動画ファイルから音声を抽出し、文字起こしを行った上で、その内容をLLMで要約するスキル。
長時間の動画の内容を素早く把握するため、文字起こしデータを中間ファイルとして出力・保存し、そのテキストデータをもとに要約を生成します。

## 依存環境
- **ffmpeg**: 動画からの音声抽出に使用します。システムにインストールされ、パスが通っている必要があります。
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
- **OpenAI API**: 文字起こし（Whisper API）および要約（GPT-4o-mini）に使用します。環境変数 `OPENAI_API_KEY` を設定してください。

## 使い方

同梱スクリプトを順に実行することで、動画ファイルから文字起こしデータを生成できます。
要約は生成された文字起こしをエージェントが読み、内容に応じて作成します。

```bash
# 音声抽出
uv run skills/video-summary/scripts/extract_audio.py <path_to_video> <output_audio.mp3>
```

```bash
# 文字起こし
uv run skills/video-summary/scripts/transcribe.py <output_audio.mp3> <output_transcript.json>
```

### 出力ファイル
実行が完了すると、以下のファイルが生成されます。

1. `*_audio.mp3`: 抽出された音声ファイル
2. `*_transcript.json`: Whisper APIによる文字起こしデータ（詳細なJSON形式）
3. `*_summary.txt`: エージェントが必要に応じて作成する要約テキスト

## モジュール構成

- `scripts/extract_audio.py`: ffmpegを用いて動画から音声を抽出
- `scripts/transcribe.py`: OpenAI Whisper APIを用いて音声から文字起こしデータを生成
