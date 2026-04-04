import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

def extract_audio(video_path: str | Path, output_audio_path: str | Path) -> Path:
    """
    動画ファイルから音声を抽出し、MP3ファイルとして保存する。

    Args:
        video_path (str | Path): 入力となる動画ファイルのパス
        output_audio_path (str | Path): 出力する音声ファイル(.mp3)のパス

    Returns:
        Path: 出力された音声ファイルのパス

    Raises:
        FileNotFoundError: 入力となる動画ファイルが存在しない場合
        RuntimeError: ffmpegによる音声抽出に失敗した場合
    """
    video_path_obj = Path(video_path)
    output_audio_path_obj = Path(output_audio_path)

    if not video_path_obj.exists():
        raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")

    # 出力先ディレクトリが存在しない場合は作成する
    output_audio_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # ffmpegコマンドを構築して実行
    command = [
        "ffmpeg",
        "-i", str(video_path_obj),
        "-q:a", "0",        # 音質指定（0は最高品質）
        "-map", "a",        # 音声ストリームのみをマッピング
        "-y",               # 既存のファイルを上書き
        str(output_audio_path_obj)
    ]

    try:
        logger.info(f"音声抽出を開始します: {video_path} -> {output_audio_path}")
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("音声抽出が完了しました。")
        return output_audio_path_obj
    except subprocess.CalledProcessError as e:
        logger.error(f"音声抽出に失敗しました: {e.stderr}")
        raise RuntimeError(f"ffmpegによる音声抽出に失敗しました: {e.stderr}") from e
    except FileNotFoundError as e:
        logger.error("ffmpegコマンドが見つかりません。システムにffmpegがインストールされているか確認してください。")
        raise RuntimeError("ffmpegがインストールされていないか、パスが通っていません。") from e
