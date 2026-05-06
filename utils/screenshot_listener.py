# ============================
# 失败自动截图 + Allure 附件监听器
# ============================

import os
import allure
import pytest
from datetime import datetime
from selenium import webdriver
from config.settings import SCREENSHOT_DIR
from utils.logger import logger


class ScreenshotListener:
    """
    Pytest Hook 监听器
    在测试失败时自动截图并附加到 Allure 报告

    使用方式：在 conftest.py 中注册
        def pytest_configure(config):
            config.pluginmanager.register(ScreenshotListener())
    """

    def __init__(self):
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """在每个测试用例执行后判断结果，失败时截图"""
        outcome = yield
        report = outcome.get_result()

        # 只在 call 阶段（实际执行阶段）处理
        if report.when != "call":
            return

        # 获取 driver fixture
        driver = None
        if "driver" in item.funcargs:
            driver = item.funcargs["driver"]

        if driver is None:
            return

        # 测试失败 → 截图 + 附加到 Allure
        if report.failed:
            self._capture_and_attach(driver, item.name, "failed")
        # 测试通过但需要记录
        elif hasattr(item, "capture_pass") and item.capture_pass:
            self._capture_and_attach(driver, item.name, "passed")

    def _capture_and_attach(self, driver, test_name, status):
        """
        截图并附加到 Allure

        Args:
            driver: WebDriver 实例
            test_name: 测试用例名称
            status: 状态 (failed/passed)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{status}_{test_name}_{timestamp}.png"
        filepath = SCREENSHOT_DIR / filename

        try:
            # 截取全页面（含滚动区域）
            self._full_page_screenshot(driver, str(filepath))

            logger.info(f"截图已保存: {filepath}")

            # 附加到 Allure 报告
            with open(filepath, "rb") as f:
                allure.attach(
                    f.read(),
                    name=f"{status}_{test_name}_{timestamp}",
                    attachment_type=allure.attachment_type.PNG
                )

            # 同时获取页面源码附加到 Allure
            page_source = driver.page_source
            allure.attach(
                page_source,
                name=f"页面源码_{test_name}",
                attachment_type=allure.attachment_type.HTML
            )

            # 获取浏览器日志
            try:
                logs = driver.get_log("browser")
                if logs:
                    log_text = "\n".join(
                        f"[{log['level']}] {log['message']}" for log in logs
                    )
                    allure.attach(
                        log_text,
                        name=f"浏览器日志_{test_name}",
                        attachment_type=allure.attachment_type.TEXT
                    )
            except Exception:
                pass

        except Exception as e:
            logger.error(f"截图失败: {e}")

    def _full_page_screenshot(self, driver, filepath):
        """
        全页面截图（包含滚动区域）

        对于普通页面直接 save_screenshot
        对于长页面通过 JS 滚动截图拼接
        """
        try:
            # 方式一：直接截图（大多数场景够用）
            driver.save_screenshot(filepath)
            return
        except Exception:
            pass

        try:
            # 方式二：通过执行 JS 获取完整页面高度
            total_height = driver.execute_script(
                "return document.body.scrollHeight"
            )
            viewport_height = driver.execute_script(
                "return window.innerHeight"
            )
            driver.set_window_size(1920, total_height)
            driver.save_screenshot(filepath)
        except Exception as e:
            logger.error(f"全页面截图失败: {e}")
            driver.save_screenshot(filepath)


class StepLogger:
    """
    测试步骤自动记录器
    装饰器 + 上下文管理器 双模式

    Usage:
        # 装饰器模式
        @StepLogger.step("登录系统")
        def test_login():
            ...

        # 上下文管理器模式
        with StepLogger("输入用户名"):
            login_page.input_username("admin")
    """

    @staticmethod
    def step(title):
        """装饰器：记录测试步骤"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                with StepLogger(title):
                    return func(*args, **kwargs)
            return wrapper
        return decorator

    def __init__(self, title):
        self.title = title

    def __enter__(self):
        try:
            import allure
            allure.step(self.title).__enter__()
        except ImportError:
            pass
        logger.info(f"📋 {self.title}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            import allure
            ctx = allure.step(self.title)
            ctx.__exit__(exc_type, exc_val, exc_tb)
        except (ImportError, AttributeError):
            pass
