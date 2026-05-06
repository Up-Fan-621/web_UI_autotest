# ============================
# WebDriver 生命周期管理器
# ============================

import os
import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions

from config.settings import (
    IMPLICIT_WAIT, PAGE_LOAD_TIMEOUT, SCRIPT_TIMEOUT,
    SCREENSHOT_DIR, HEADLESS, BASE_DIR
)
from utils.logger import logger

# Windows chromedriver 路径
DRIVER_DIR = BASE_DIR / "drivers"


class DriverManager:
    """
    WebDriver 管理器
    统一管理浏览器的创建、配置和销毁

    Usage:
        dm = DriverManager(browser="chrome", headless=True)
        driver = dm.get_driver()
        # ... 测试代码 ...
        dm.quit_driver()
    """

    def __init__(self, browser="chrome", headless=None):
        """
        Args:
            browser: 浏览器类型 chrome / firefox / edge
            headless: 是否无头模式，None 则读取配置
        """
        self.browser = browser.lower()
        self.headless = headless if headless is not None else HEADLESS
        self._driver = None
        logger.info(f"初始化 DriverManager: browser={self.browser}, headless={self.headless}")

    def get_driver(self):
        """
        获取 WebDriver 实例（单例模式）

        Returns:
            WebDriver: 配置好的浏览器实例
        """
        if self._driver is not None:
            return self._driver

        driver = None

        if self.browser == "chrome":
            driver = self._create_chrome_driver()
        elif self.browser == "firefox":
            driver = self._create_firefox_driver()
        elif self.browser == "edge":
            driver = self._create_edge_driver()
        else:
            raise ValueError(f"不支持的浏览器类型: {self.browser}，可选: chrome/firefox/edge")

        # 全局超时设置
        driver.implicitly_wait(IMPLICIT_WAIT)
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        driver.set_script_timeout(SCRIPT_TIMEOUT)

        # 最大化窗口
        driver.maximize_window()

        self._driver = driver
        logger.info(f"{self.browser} 浏览器启动成功")
        return driver

    def _create_chrome_driver(self):
        """创建 Chrome WebDriver"""
        options = ChromeOptions()

        # 无头模式
        if self.headless:
            options.add_argument("--headless=new")

        # 通用配置
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--lang=zh-CN")

        # 禁用不必要的功能
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # 设置下载路径
        prefs = {
            "download.default_directory": str(SCREENSHOT_DIR),
            "download.prompt_for_download": False,
            "profile.default_content_settings.popups": 0
        }
        options.add_experimental_option("prefs", prefs)

        # 自动管理 driver 版本
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except Exception as e:
            logger.warning(f"webdriver-manager 失败: {e}，尝试本地 driver")
            local_driver = DRIVER_DIR / "chromedriver.exe"
            if local_driver.exists():
                service = Service(str(local_driver))
                return webdriver.Chrome(service=service, options=options)
            return webdriver.Chrome(options=options)

    def _create_firefox_driver(self):
        """创建 Firefox WebDriver"""
        options = FirefoxOptions()

        if self.headless:
            options.add_argument("--headless")

        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        options.set_preference("intl.accept_languages", "zh-CN")

        try:
            from webdriver_manager.firefox import GeckoDriverManager
            service = FirefoxService(GeckoDriverManager().install())
            return webdriver.Firefox(service=service, options=options)
        except Exception as e:
            logger.warning(f"webdriver-manager 失败: {e}")
            return webdriver.Firefox(options=options)

    def _create_edge_driver(self):
        """创建 Edge WebDriver"""
        options = EdgeOptions()

        if self.headless:
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        try:
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            service = EdgeService(EdgeChromiumDriverManager().install())
            return webdriver.Edge(service=service, options=options)
        except Exception as e:
            logger.warning(f"webdriver-manager 失败: {e}")
            return webdriver.Edge(options=options)

    def quit_driver(self):
        """安全销毁 WebDriver"""
        if self._driver:
            try:
                self._driver.quit()
                logger.info(f"{self.browser} 浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器异常: {e}")
            finally:
                self._driver = None


def inject_stealth_js(driver):
    """
    注入反检测 JS，避免被网站识别为自动化工具

    Usage:
        driver = DriverManager().get_driver()
        inject_stealth_js(driver)
    """
    stealth_js = """
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
    Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
    window.chrome = {runtime: {}};
    """
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": stealth_js})
        logger.info("反检测 JS 注入成功")
    except Exception as e:
        logger.warning(f"反检测 JS 注入失败（非致命）: {e}")
