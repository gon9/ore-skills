"""gTTSを使用した日本語テキスト→音声変換."""

from __future__ import annotations

from pathlib import Path

from gtts import gTTS


def generate_audio(text: str, output_path: str | Path, lang: str = "ja") -> Path:
    """テキストからMP3音声ファイルを生成する.

    Args:
        text: 読み上げテキスト
        output_path: 出力MP3ファイルのパス
        lang: 言語コード (デフォルト: ja)

    Returns:
        生成された音声ファイルのパス
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(str(output_path))
    return output_path
