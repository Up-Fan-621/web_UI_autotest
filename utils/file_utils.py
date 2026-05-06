# ============================
# 文件操作工具
# ============================

import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from config.settings import DATA_DIR
from utils.logger import logger


class FileUtils:
    """通用文件操作工具"""

    @staticmethod
    def read_yaml(file_path):
        """
        读取 YAML 文件

        Args:
            file_path: 文件路径（相对 data/ 目录或绝对路径）

        Returns:
            dict/list: YAML 数据
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = DATA_DIR / path

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        logger.debug(f"读取 YAML: {path}")
        return data

    @staticmethod
    def write_yaml(file_path, data):
        """写入 YAML 文件"""
        path = Path(file_path)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        logger.debug(f"写入 YAML: {path}")

    @staticmethod
    def read_json(file_path):
        """读取 JSON 文件"""
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def write_json(file_path, data):
        """写入 JSON 文件"""
        path = Path(file_path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_test_data(data_file):
        """
        加载测试数据文件（自动识别格式）

        Args:
            data_file: 文件名（在 data/ 目录下）

        Returns:
            dict/list: 测试数据
        """
        path = DATA_DIR / data_file
        if not path.exists():
            logger.warning(f"测试数据文件不存在: {path}")
            return {}

        suffix = path.suffix.lower()
        if suffix in (".yaml", ".yml"):
            return FileUtils.read_yaml(path)
        elif suffix == ".json":
            return FileUtils.read_json(path)
        else:
            raise ValueError(f"不支持的数据文件格式: {suffix}")

    @staticmethod
    def generate_timestamp_filename(prefix="screenshot", extension="png"):
        """生成带时间戳的文件名"""
        return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
