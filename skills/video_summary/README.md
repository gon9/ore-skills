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

CLIツールとして実行することで、動画ファイルから文字起こしおよび要約を生成できます。
プロジェクトルートにある `.env` ファイルから `OPENAI_API_KEY` を自動的に読み込みます。

```bash
# パイプラインの実行
uv run --project skills/video_summary -m video_summary.pipeline <path_to_video>
```

出力先ディレクトリを指定することも可能です（省略時は動画ファイルと同じディレクトリに出力されます）。

```bash
uv run --project skills/video_summary -m video_summary.pipeline <path_to_video> --output-dir <path_to_output_dir>
```

### 出力ファイル
実行が完了すると、以下の3つのファイルが生成されます。

1. `*_audio.mp3`: 抽出された音声ファイル
2. `*_transcript.json`: Whisper APIによる文字起こしデータ（詳細なJSON形式）
3. `*_summary.txt`: GPT-4o-miniによって生成された要約テキスト

## モジュール構成

- `extractor.py`: ffmpegを用いて動画から音声を抽出
- `transcriber.py`: OpenAI Whisper APIを用いて音声から文字起こしデータを生成
- `summarizer.py`: OpenAI GPT APIを用いて文字起こしテキストから要約を生成
- `pipeline.py`: 上記3つの処理を順次実行する統合パイプライン
