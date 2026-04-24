import logging


def get_logger(name: str) -> logging.Logger:
    """返回统一格式的日志对象。"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger(name)

