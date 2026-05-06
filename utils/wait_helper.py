# ============================
# 等待条件扩展（自定义 Expected Conditions）
# ============================

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from config.settings import EXPLICIT_WAIT
from utils.logger import logger


class WaitHelper:
    """
    等待条件扩展工具
    封装了常用但 Selenium EC 未提供的等待条件

    Usage:
        wait = WaitHelper(driver)

        # 等待元素包含文本
        wait.for_text_contains((By.CLASS_NAME, "msg"), "成功")

        # 等待元素消失
        wait.for_element_invisible((By.ID, "loading"))

        # 等待 AJAX 请求完成
        wait.for_ajax_complete()

        # 等待数量变化
        wait.for_count_change((By.CLASS_NAME, "item"), 5)
    """

    def __init__(self, driver, timeout=None):
        self.driver = driver
        self.timeout = timeout or EXPLICIT_WAIT
        self._wait = WebDriverWait(driver, self.timeout)

    def for_text_contains(self, locator, text):
        """等待元素文本包含指定内容"""
        def _check(driver):
            try:
                return text in driver.find_element(*locator).text
            except:
                return False
        self._wait.until(_check)
        logger.debug(f"等待文本包含: '{text}'")

    def for_text_equals(self, locator, text):
        """等待元素文本等于指定内容"""
        def _check(driver):
            try:
                return driver.find_element(*locator).text == text
            except:
                return False
        self._wait.until(_check)
        logger.debug(f"等待文本等于: '{text}'")

    def for_element_invisible(self, locator, timeout=None):
        """等待元素不可见（消失）"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        wait.until(EC.invisibility_of_element_located(locator))
        logger.debug(f"等待元素不可见: {locator}")

    def for_element_stale(self, locator):
        """等待元素被从 DOM 移除"""
        def _check(driver):
            try:
                driver.find_element(*locator)
                return False
            except:
                return True
        self._wait.until(_check)

    def for_ajax_complete(self, timeout=None):
        """等待 AJAX 请求完成（jQuery）"""
        def _check(driver):
            try:
                return driver.execute_script(
                    "return jQuery.active == 0"
                ) if self._has_jquery(driver) else True
            except:
                return True
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        wait.until(_check)
        logger.debug("AJAX 请求已完成")

    def for_page_loaded(self):
        """等待页面完全加载"""
        def _check(driver):
            return driver.execute_script("return document.readyState") == "complete"
        self._wait.until(_check)
        logger.debug("页面加载完成")

    def for_animation_end(self, locator):
        """等待 CSS 动画结束"""
        def _check(driver):
            try:
                element = driver.find_element(*locator)
                animations = driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).animationName",
                    element
                )
                return not animations or animations == "none"
            except:
                return True
        self._wait.until(_check)

    def for_count_change(self, locator, expected_count):
        """等待指定元素数量变为预期值"""
        def _check(driver):
            try:
                elements = driver.find_elements(*locator)
                return len(elements) == expected_count
            except:
                return False
        self._wait.until(_check)
        logger.debug(f"等待元素数量变为: {expected_count}")

    def for_url_contains(self, text):
        """等待 URL 包含指定文本"""
        self._wait.until(EC.url_contains(text))
        logger.debug(f"等待 URL 包含: '{text}'")

    def for_new_tab_opened(self, original_handles):
        """等待新标签页打开"""
        def _check(driver):
            return len(driver.window_handles) > len(original_handles)
        self._wait.until(_check)

    @staticmethod
    def _has_jquery(driver):
        """检查页面是否加载了 jQuery"""
        try:
            return driver.execute_script("return typeof jQuery != 'undefined'")
        except:
            return False
