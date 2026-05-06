# ============================
# conftest.py - Pytest 核心配置
# ============================
# 这是最重要的文件之一：
# - 注册所有 fixtures（driver、测试数据、工具实例等）
# - 配置失败截图监听
# - 初始化日志系统
# - 管理测试生命周期

import sys
import os
import time
import pytest
import allure
import yaml
from pathlib import Path

# 将项目根目录添加到 sys.path（确保跨目录 import 正常）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import (
    ENV, BASE_DIR, SCREENSHOT_DIR, ALLURE_RESULTS_DIR, get_env_config, ensure_dirs
)
from config.conftest_env import pytest_addoption  # noqa: F401 - 确保 CLI 参数注册
from utils.driver_manager import DriverManager, inject_stealth_js
from utils.logger import setup_logger, logger
from utils.screenshot_listener import ScreenshotListener
from utils.api_utils import APIUtils
from utils.db_utils import DBUtils
from utils.file_utils import FileUtils


# ===========================
# 1. Session 级别初始化
# ===========================

def pytest_configure(config):
    """
    Pytest 初始化钩子
    在所有测试开始前执行一次
    """
    # 确保必要目录存在
    ensure_dirs()

    # 初始化日志系统
    setup_logger(log_level="INFO")

    # 注册失败自动截图监听器
    config.pluginmanager.register(ScreenshotListener())

    logger.info("=" * 60)
    logger.info("UI 自动化测试启动")
    logger.info(f"环境: {ENV}")
    logger.info(f"浏览器: {config.getoption('--browser', default='chrome')}")
    logger.info(f"无头模式: {config.getoption('--headless', default=False)}")
    logger.info("=" * 60)


def pytest_sessionfinish(session, exitstatus):
    """
    Pytest 会话结束钩子
    """
    total = session.testscollected
    passed = session.testscollected - session.testsfailed - session.tests_skipped
    logger.info("=" * 60)
    logger.info(f"测试完成: 总计 {total}, 通过 {passed}, 失败 {session.testsfailed}, 跳过 {session.tests_skipped}")
    logger.info("=" * 60)


# ===========================
# 2. Fixtures 定义
# ===========================

@pytest.fixture(scope="session")
def base_url(request):
    """
    获取当前环境的基础 URL

    Returns:
        str: 如 "https://test.example.com"
    """
    env = request.config.getoption("--env")
    config = get_env_config(env)
    return config["base_url"]


@pytest.fixture(scope="session")
def api_url(request):
    """获取当前环境的 API URL"""
    env = request.config.getoption("--env")
    config = get_env_config(env)
    return config["api_url"]


@pytest.fixture(scope="session")
def env_name(request):
    """获取当前环境名"""
    return request.config.getoption("--env")


@pytest.fixture(scope="function")
def driver(request):
    """
    WebDriver fixture（每个用例独立实例）

    生命周期:
        1. 用例执行前 → 创建浏览器实例
        2. 用例执行中 → 提供 driver 给用例使用
        3. 用例执行后 → 失败自动截图（由 ScreenshotListener 处理）
        4. 用例执行后 → 关闭浏览器

    Returns:
        WebDriver: Selenium WebDriver 实例
    """
    browser = request.config.getoption("--browser", default="chrome") or "chrome"
    headless = request.config.getoption("--headless", default=False)

    # 创建 driver
    dm = DriverManager(browser=browser, headless=headless)
    driver = dm.get_driver()

    # 注入反检测 JS
    inject_stealth_js(driver)

    # 记录启动到 Allure
    try:
        allure.attach(
            f"Browser: {browser}\nHeadless: {headless}\nURL: {driver.current_url}",
            name="测试环境信息",
            attachment_type=allure.attachment_type.TEXT
        )
    except Exception:
        pass

    logger.info(f"浏览器已启动: {browser} (headless={headless})")

    yield driver

    # 清理：关闭浏览器
    dm.quit_driver()
    logger.info(f"浏览器已关闭: {browser}")


@pytest.fixture(scope="session")
def api_utils(api_url):
    """
    API 工具 fixture（Session 级别共享）

    用途:
        - 通过 API 造数据（绕过 UI）
        - 清理测试数据
        - 接口数据交叉验证

    Returns:
        APIUtils: API 工具实例
    """
    return APIUtils(base_url=api_url)


@pytest.fixture(scope="session")
def db_utils():
    """
    数据库工具 fixture（Session 级别共享）

    用途:
        - 查询验证测试结果
        - 准备/清理测试数据

    Returns:
        DBUtils: 数据库工具实例
    """
    try:
        return DBUtils()
    except Exception as e:
        logger.warning(f"数据库连接失败（非致命）: {e}")
        return None


@pytest.fixture(scope="session")
def file_utils():
    """文件工具 fixture"""
    return FileUtils()


# ===========================
# 3. 测试数据 Fixtures
# ===========================

@pytest.fixture(scope="session")
def login_data(file_utils):
    """加载登录测试数据"""
    return file_utils.load_test_data("test_data_login.yaml")


@pytest.fixture(scope="session")
def search_data(file_utils):
    """加载搜索测试数据"""
    return file_utils.load_test_data("test_data_search.yaml")


@pytest.fixture(scope="session")
def order_data(file_utils):
    """加载订单测试数据"""
    return file_utils.load_test_data("test_data_order.yaml")


@pytest.fixture(scope="session")
def register_data(file_utils):
    """加载注册测试数据"""
    return file_utils.load_test_data("test_data_register.yaml")


@pytest.fixture(scope="session")
def color_data(file_utils):
    """加载颜色识别测试数据"""
    return file_utils.load_test_data("test_data_color.yaml")


@pytest.fixture(scope="session")
def image_data(file_utils):
    """加载图片识别测试数据"""
    return file_utils.load_test_data("test_data_image.yaml")


# ===========================
# 4. 数据准备 & 清理 Fixtures
# ===========================

@pytest.fixture(scope="function")
def prepare_test_order(api_utils, order_data):
    """
    通过 API 预创建测试订单（每个用例前执行）

    Returns:
        dict: 创建的订单信息
    """
    # 从测试数据中获取预创建订单配置
    pre_order = order_data["pre_created_orders"][0]
    logger.info(f"通过 API 创建测试订单: user={pre_order['user_id']}, product={pre_order['product_id']}")

    result = api_utils.create_test_order(
        user_id=pre_order["user_id"],
        product_id=pre_order["product_id"],
        quantity=pre_order["quantity"]
    )

    yield result or pre_order

    # 用例执行后清理
    try:
        api_utils.cleanup_test_data(pre_order["user_id"])
        logger.info(f"测试数据已清理: user_id={pre_order['user_id']}")
    except Exception as e:
        logger.warning(f"测试数据清理失败（非致命）: {e}")


@pytest.fixture(scope="function")
def api_login(driver, api_utils, login_data):
    """
    通过 API 登录并注入 Cookie（绕过 UI 登录流程）

    适用于：需要登录但不需要测试登录流程的用例
    """
    valid_user = login_data["valid_users"][0]
    result = api_utils.login_by_api(valid_user["username"], valid_user["password"])

    # 如果登录返回了 token/cookie，注入到 driver
    if result and "token" in str(result).lower():
        token = result.get("data", {}).get("token") or result.get("token")
        if token:
            driver.execute_script(
                f"document.cookie = 'token={token}; path=/'"
            )
            driver.refresh()

    yield valid_user

    # 登出清理
    try:
        api_utils.delete("/api/auth/logout")
    except Exception:
        pass


# ===========================
# 5. Allure 自定义 Fixtures
# ===========================

@pytest.fixture(scope="function", autouse=True)
def allure_environment_fixture(base_url, env_name):
    """自动将环境信息写入 Allure 报告"""
    allure.environment(env=env_name, base_url=base_url)


@pytest.fixture(scope="function", autouse=True)
def attach_browser_log_on_failure(driver, request):
    """
    用例失败时附加浏览器控制台日志到 Allure

    注意：这个 fixture 通过 yield 的 teardown 部分实现
    """
    yield  # 先让用例执行

    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        try:
            logs = driver.get_log("browser")
            if logs:
                log_text = "\n".join(
                    f"[{log['level']}] {log['timestamp']} - {log['message']}"
                    for log in logs
                )
                allure.attach(
                    log_text,
                    name="浏览器控制台日志",
                    attachment_type=allure.attachment_type.TEXT
                )
        except Exception:
            pass
