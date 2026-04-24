import logging

from common.logger import setup_logger


def test_setup_logger():
    logger = setup_logger("test_logger")
    assert logger.name == "test_logger"
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_setup_logger_singleton():
    logger1 = setup_logger("test_logger_singleton")
    logger2 = setup_logger("test_logger_singleton")
    assert logger1 is logger2
    # ハンドラが増えていないことを確認
    assert len(logger1.handlers) == 1
