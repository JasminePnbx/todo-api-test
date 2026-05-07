# utils/logger.py
import logging
import sys
from pathlib import Path
from config import settings

def setup_logger(name: str = None, log_level: str = None, log_file: str = None):
    """
    配置并返回一个 logger 实例。
    如果 name 为 None，返回 root logger。
    支持控制台 + 文件输出。
    """
    logger = logging.getLogger(name or __name__)
    log_level = log_level or settings.LOG_LEVEL
    log_file = log_file or settings.LOG_FILE

    logger.setLevel(log_level)

    # 避免重复添加 handler（防止多次调用 setup_logger 导致重复日志）
    if logger.handlers:
        return logger

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)-8s] %(name)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件 handler（自动创建 logs/ 目录）
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger