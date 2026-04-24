import logging
import sys


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    アプリケーション共通のロガー設定を行います。

    Args:
        name (str): ロガー名
        level (int): ログレベル (デフォルト: logging.INFO)

    Returns:
        logging.Logger: 設定済みのロガーインスタンス
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
