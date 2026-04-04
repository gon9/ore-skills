import json
import logging
import os
from pathlib import Path

from openai import OpenAI

logger = logging.getLogger(__name__)

def transcribe_audio(audio_path: str | Path, output_text_path: str | Path) -> Path:
    """
    音声ファイルから文字起こしを行い、テキストまたはJSONファイルとして保存する。

    Args:
        audio_path (str | Path): 入力となる音声ファイルのパス
        output_text_path (str | Path): 出力する文字起こしデータのパス

    Returns:
        Path: 出力された文字起こしデータのパス

    Raises:
        FileNotFoundError: 入力となる音声ファイルが存在しない場合
        RuntimeError: OpenAI APIキーが設定されていない場合、またはAPI呼び出しに失敗した場合
    """
    audio_path_obj = Path(audio_path)
    output_text_path_obj = Path(output_text_path)

    if not audio_path_obj.exists():
        raise FileNotFoundError(f"音声ファイルが見つかりません: {audio_path}")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("環境変数 'OPENAI_API_KEY' が設定されていません。")

    client = OpenAI(api_key=api_key)

    # 出力先ディレクトリが存在しない場合は作成する
    output_text_path_obj.parent.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(f"文字起こしを開始します: {audio_path}")
        with open(audio_path_obj, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                response_format="verbose_json"
            )
        
        # verbose_json形式で受け取り、テキストとタイムスタンプなどを保持する形で保存
        with open(output_text_path_obj, "w", encoding="utf-8") as f:
            if output_text_path_obj.suffix.lower() == ".json":
                json.dump(transcript.model_dump(), f, ensure_ascii=False, indent=2)
            else:
                f.write(transcript.text)

        logger.info(f"文字起こしが完了しました: {output_text_path}")
        return output_text_path_obj
    except Exception as e:
        logger.error(f"文字起こしに失敗しました: {e}")
        raise RuntimeError(f"OpenAI APIによる文字起こしに失敗しました: {e}") from e
