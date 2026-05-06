# ============================
# 全局配置中心
# ============================

import os
from pathlib import Path

# --- 项目根路径 ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- 环境变量 ---
ENV = os.getenv("ENV", "test")

# --- 路径配置 ---
REPORT_DIR = BASE_DIR / "reports"
SCREENSHOT_DIR = REPORT_DIR / "screenshots"
ALLURE_RESULTS_DIR = REPORT_DIR / "html" / "results"
ALLURE_REPORT_DIR = REPORT_DIR / "html"
DATA_DIR = BASE_DIR / "data"
BASELINE_IMG_DIR = BASE_DIR / "baseline_images"

# --- 浏览器配置 ---
BROWSER = os.getenv("BROWSER", "chrome")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
IMPLICIT_WAIT = 10          # 隐式等待（秒）
EXPLICIT_WAIT = 15          # 显式等待（秒）
PAGE_LOAD_TIMEOUT = 30      # 页面加载超时（秒）
SCRIPT_TIMEOUT = 20         # 脚本执行超时（秒）

# --- 截图配置 ---
SCREENSHOT_ON_FAIL = os.getenv("SCREENSHOT_ON_FAIL", "true").lower() == "true"

# --- 数据库配置 ---
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "test_user"),
    "password": os.getenv("DB_PASSWORD", "Test@123"),
    "database": os.getenv("DB_NAME", "test_db"),
    "charset": "utf8mb4"
}

# --- API 配置 ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://api-test.example.com")
API_TOKEN = os.getenv("API_TOKEN", "")
API_TIMEOUT = 30

# --- 图片识别配置 ---
IMAGE_MATCH_THRESHOLD = 0.8    # 图片匹配相似度阈值
OCR_LANG = "chi_sim+eng"       # OCR 识别语言

# --- 多环境 URL 映射 ---
ENV_URLS = {
    "test": {
        "base_url": "https://test.example.com",
        "api_url": "https://api-test.example.com",
        "db_name": "test_db"
    },
    "staging": {
        "base_url": "https://staging.example.com",
        "api_url": "https://api-staging.example.com",
        "db_name": "staging_db"
    },
    "prod": {
        "base_url": "https://www.example.com",
        "api_url": "https://api.example.com",
        "db_name": "prod_db"
    }
}


def get_env_config(env_key=None):
    """
    获取当前环境配置

    Args:
        env_key: 指定环境名（test/staging/prod），默认读取 ENV 变量

    Returns:
        dict: 当前环境的配置字典
    """
    env_name = env_key or ENV
    return ENV_URLS.get(env_name, ENV_URLS["test"])


def ensure_dirs():
    """确保所有必要目录存在"""
    dirs = [SCREENSHOT_DIR, ALLURE_RESULTS_DIR, ALLURE_REPORT_DIR, DATA_DIR, BASELINE_IMG_DIR]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
