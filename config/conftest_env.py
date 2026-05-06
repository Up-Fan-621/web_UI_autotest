# ============================
# Pytest 命令行参数注册
# ============================

import pytest
import yaml
from config.settings import BASE_DIR


def pytest_addoption(parser):
    """注册自定义命令行参数"""
    parser.addoption(
        "--env", action="store", default="test",
        choices=["test", "staging", "prod"],
        help="指定运行环境: test / staging / prod (默认: test)"
    )
    parser.addoption(
        "--browser", action="store", default=None,
        choices=["chrome", "firefox", "edge"],
        help="指定浏览器: chrome / firefox / edge (默认读取配置文件)"
    )
    parser.addoption(
        "--headless", action="store_true", default=False,
        help="是否使用无头模式运行"
    )
    parser.addoption(
        "--reruns", action="store", default="0",
        help="失败重试次数 (默认: 0)"
    )
    parser.addoption(
        "--workers", action="store", default="1",
        help="并行 worker 数量 (默认: 1, 需配合 pytest-xdist)"
    )


@pytest.fixture(scope="session")
def env_name(request):
    """获取当前环境名"""
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def env_config(request):
    """
    加载当前环境的 YAML 配置

    Returns:
        dict: 包含 base_url, api_url, db_name 等配置
    """
    env = request.config.getoption("--env")
    config_file = BASE_DIR / "config" / f"{env}_config.yaml"
    if not config_file.exists():
        # 降级到默认配置
        config_file = BASE_DIR / "config" / "test_config.yaml"
    with open(config_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@pytest.fixture(scope="session")
def base_url(env_config):
    """获取当前环境的基础 URL"""
    env = env_config.get("env", {}).get(env_name, {})
    return env.get("base_url", "https://test.example.com")
