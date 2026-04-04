import argparse
import logging
from pathlib import Path

from dotenv import load_dotenv

from .extractor import extract_audio
from .summarizer import generate_summary
from .transcriber import transcribe_audio

# 環境変数の読み込み
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def process_video(video_path: str | Path, output_dir: str | Path = None) -> Path:
    """
    動画ファイルから音声を抽出し、文字起こし、要約までを一貫して実行するパイプライン。

    Args:
        video_path (str | Path): 入力となる動画ファイルのパス
        output_dir (str | Path, optional): 出力ファイルを保存するディレクトリ。デフォルトは動画と同じディレクトリ

    Returns:
        Path: 生成された要約ファイルのパス
    """
    video_path_obj = Path(video_path)

    if not video_path_obj.exists():
        raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")

    # 出力先ディレクトリの設定
    if output_dir is None:
        base_dir = video_path_obj.parent
    else:
        base_dir = Path(output_dir)
        base_dir.mkdir(parents=True, exist_ok=True)

    # 各ステップの出力ファイルパスの決定
    base_name = video_path_obj.stem
    audio_path = base_dir / f"{base_name}.mp3"
    transcript_path = base_dir / f"{base_name}_transcript.json"
    summary_path = base_dir / f"{base_name}_summary.txt"

    try:
        # 1. 音声抽出
        logger.info("--- 1/3: 音声抽出プロセスを開始します ---")
        extract_audio(video_path_obj, audio_path)

        # 2. 文字起こし
        logger.info("--- 2/3: 文字起こしプロセスを開始します ---")
        transcribe_audio(audio_path, transcript_path)

        # 3. 要約
        logger.info("--- 3/3: 要約プロセスを開始します ---")
        generate_summary(transcript_path, summary_path)

        logger.info(f"すべての処理が完了しました。要約ファイル: {summary_path}")
        return summary_path
    except Exception as e:
        logger.error(f"パイプライン処理中にエラーが発生しました: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="動画ファイルから文字起こしと要約を生成するツール")
    parser.add_argument("video_path", type=str, help="入力動画ファイルのパス")
    parser.add_argument("--output-dir", type=str, help="出力ディレクトリのパス（省略時は動画と同じディレクトリ）")
    
    args = parser.parse_args()

    try:
        process_video(args.video_path, args.output_dir)
    except Exception as e:
        logger.error(f"実行に失敗しました: {e}")
        exit(1)

if __name__ == "__main__":
    main()
