import json
import logging
from pathlib import Path

from common import chat_completion

logger = logging.getLogger(__name__)


def generate_summary(transcript_path: str | Path, output_summary_path: str | Path) -> Path:
    """
    文字起こしデータから要約を生成し、テキストファイルとして保存する。

    OpenAI または Anthropic API を使用(環境変数 LLM_PROVIDER で切替可能)。

    Args:
        transcript_path (str | Path): 入力となる文字起こしデータのパス (.txt または .json)
        output_summary_path (str | Path): 出力する要約テキストのパス

    Returns:
        Path: 出力された要約テキストのパス

    Raises:
        FileNotFoundError: 入力となる文字起こしファイルが存在しない場合
        RuntimeError: APIキーが設定されていない場合、またはAPI呼び出しに失敗した場合
    """
    transcript_path_obj = Path(transcript_path)
    output_summary_path_obj = Path(output_summary_path)

    if not transcript_path_obj.exists():
        raise FileNotFoundError(f"文字起こしファイルが見つかりません: {transcript_path}")

    # 出力先ディレクトリが存在しない場合は作成する
    output_summary_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # 文字起こしデータを読み込む
    try:
        if transcript_path_obj.suffix.lower() == ".json":
            with open(transcript_path_obj, encoding="utf-8") as f:
                data = json.load(f)
                text_content = data.get("text", "")
        else:
            with open(transcript_path_obj, encoding="utf-8") as f:
                text_content = f.read()
    except Exception as e:
        logger.error(f"文字起こしデータの読み込みに失敗しました: {e}")
        raise RuntimeError(f"文字起こしデータの読み込みに失敗しました: {e}") from e

    if not text_content:
        raise ValueError("文字起こしデータが空です。要約を生成できません。")

    system_prompt = (
        "あなたはプロの編集者です。"
        "以下の動画の文字起こしテキストを読み、主要なポイント、結論、重要な事実を簡潔に要約してください。"
        "要約は箇条書きと短い段落を組み合わせて、読みやすく構造化して出力してください。"
        "出力は日本語で行ってください。"
    )

    try:
        logger.info(f"要約の生成を開始します: {transcript_path}")
        response = chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text_content},
            ],
            temperature=0.3,
            max_tokens=1500,
        )

        # 要約結果を保存
        with open(output_summary_path_obj, "w", encoding="utf-8") as f:
            f.write(response.content)

        logger.info(f"要約の生成が完了しました ({response.provider}/{response.model}): {output_summary_path}")
        return output_summary_path_obj
    except Exception as e:
        logger.error(f"要約生成に失敗しました: {e}")
        raise RuntimeError(f"LLM APIによる要約生成に失敗しました: {e}") from e
