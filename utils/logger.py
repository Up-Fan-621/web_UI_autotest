# ============================
# 日志系统封装（基于 loguru）
# ============================

import sys
from pathlib import Path
from loguru import logger

from config.settings import REPORT_DIR


def setup_logger(log_level="INFO"):
    """
    初始化日志系统

    Features:
        - 控制台输出（彩色格式）
        - 文件输出（按天轮转，保留30天）
        - 错误日志单独存放
        - 自动记录到 Allure 报告

    Args:
        log_level: 日志级别，默认 INFO
    """
    # 移除默认 handler
    logger.remove()

    # 日志文件目录
    log_dir = REPORT_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # 日志格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )

    # 1. 控制台输出
    logger.add(
        sys.stderr,
        format=console_format,
        level=log_level,
        colorize=True
    )

    # 2. 全部日志文件（按天轮转，保留30天，单文件最大 50MB）
    logger.add(
        str(log_dir / "ui_auto_{time:YYYY-MM-DD}.log"),
        format=file_format,
        level=log_level,
        rotation="00:00",       # 每天轮转
        retention="30 days",    # 保留30天
        compression="zip",      # 压缩旧日志
        encoding="utf-8",
        enqueue=True            # 异步写入，不阻塞主线程
    )

    # 3. 错误日志单独存放
    logger.add(
        str(log_dir / "error_{time:YYYY-MM-DD}.log"),
        format=file_format,
        level="ERROR",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        enqueue=True
    )

    logger.info("日志系统初始化完成")
    return logger


# 创建全局 logger 实例
# 在 conftest.py 中调用 setup_logger() 进行初始化
# 这里先做基础配置
logger.remove()
logger.add(sys.stderr, format="{time:HH:mm:ss} | {level} | {message}", level="INFO")


def get_logger():
    """获取 logger 实例"""
    return logger


class AllureLogHandler:
    """
    Allure 日志适配器
    在测试步骤中自动将日志附加到 Allure 报告
    """

    @staticmethod
    def step(title: str):
        """记录一个测试步骤到 Allure"""
        try:
            import allure
            with allure.step(title):
                pass
        except ImportError:
            pass
        logger.info(f"📋 步骤: {title}")

    @staticmethod
    def attach_log(text: str, name: str = "日志详情"):
        """将日志文本附加到 Allure 报告"""
        try:
            import allure
            allure.attach(text, name=name, allure.attachment_type.TEXT)
        except ImportError:
            pass
