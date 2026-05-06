# ============================
# BasePage - 所有页面的基类
# ============================

import time
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.color import Color
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from config.settings import EXPLICIT_WAIT
from utils.logger import logger
from utils.wait_helper import WaitHelper
from utils.image_recognition import ImageRecognition, OCREngine


class BasePage:
    """
    页面对象基类
    封装所有页面的通用操作，子类直接继承使用

    设计原则：
        - 所有元素操作都使用显式等待
        - 不使用 time.sleep()
        - 提供链式调用支持
        - 集成日志、截图、图片识别能力
    """

    # ========== 初始化 ==========

    def __init__(self, driver):
        self.driver = driver
        self.timeout = EXPLICIT_WAIT
        self.wait = WaitHelper(driver, self.timeout)
        self.action = ActionChains(driver)
        self.image = ImageRecognition(driver)
        self.ocr = OCREngine(driver)

    # ========== 页面导航 ==========

    def open(self, url):
        """打开指定 URL"""
        logger.info(f"打开页面: {url}")
        self.driver.get(url)
        self.wait.for_page_loaded()
        return self

    def refresh(self):
        """刷新当前页面"""
        logger.info("刷新页面")
        self.driver.refresh()
        self.wait.for_page_loaded()
        return self

    def go_back(self):
        """浏览器后退"""
        logger.info("浏览器后退")
        self.driver.back()
        return self

    def go_forward(self):
        """浏览器前进"""
        self.driver.forward()
        return self

    def switch_to_new_tab(self):
        """切换到最新打开的标签页"""
        self.driver.switch_to.window(self.driver.window_handles[-1])
        return self

    def switch_to_default_content(self):
        """切换到默认 frame"""
        self.driver.switch_to.default_content()
        return self

    def switch_to_frame(self, frame_reference):
        """
        切换到 iframe

        Args:
            frame_reference: 可以是 id/name 字符串、定位器元组或 WebElement
        """
        WebDriverWait(self.driver, self.timeout).until(
            EC.frame_to_be_available_and_switch_to_it(frame_reference)
        )
        return self

    # ========== 元素查找 ==========

    def find_element(self, locator):
        """显式等待 + 查找单个元素"""
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(locator)
        )

    def find_elements(self, locator):
        """显式等待 + 查找多个元素"""
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_all_elements_located(locator)
        )

    def find_visible_element(self, locator):
        """等待元素可见后返回"""
        return WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def find_clickable_element(self, locator):
        """等待元素可点击后返回"""
        return WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable(locator)
        )

    # ========== 元素操作 ==========

    def click(self, locator):
        """点击元素（等待可点击状态）"""
        logger.debug(f"点击元素: {locator}")
        element = self.find_clickable_element(locator)
        element.click()
        return self

    def double_click(self, locator):
        """双击元素"""
        logger.debug(f"双击元素: {locator}")
        element = self.find_element(locator)
        self.action.double_click(element).perform()
        return self

    def right_click(self, locator):
        """右键点击元素"""
        element = self.find_element(locator)
        self.action.context_click(element).perform()
        return self

    def input_text(self, locator, text, clear_first=True):
        """
        输入文本

        Args:
            locator: 元素定位器
            text: 输入文本
            clear_first: 是否先清空
        """
        logger.debug(f"输入文本: '{text}' → {locator}")
        element = self.find_element(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)
        return self

    def press_key(self, locator, *keys):
        """
        按下键盘按键

        Usage:
            page.press_key(locator, Keys.ENTER)
            page.press_key(locator, Keys.CONTROL, "a")
        """
        element = self.find_element(locator)
        for key in keys:
            element.send_keys(key)
        return self

    def upload_file(self, locator, file_path):
        """
        上传文件（input[type=file]）

        Args:
            locator: 文件输入框定位器
            file_path: 文件绝对路径
        """
        element = self.find_element(locator)
        element.send_keys(file_path)
        logger.info(f"上传文件: {file_path}")
        return self

    # ========== 下拉选择 ==========

    def select_by_visible_text(self, locator, text):
        """通过可见文本选择下拉选项"""
        element = self.find_element(locator)
        Select(element).select_by_visible_text(text)
        logger.debug(f"下拉选择(文本): '{text}'")
        return self

    def select_by_value(self, locator, value):
        """通过 value 属性选择下拉选项"""
        element = self.find_element(locator)
        Select(element).select_by_value(value)
        logger.debug(f"下拉选择(value): '{value}'")
        return self

    def select_by_index(self, locator, index):
        """通过索引选择下拉选项（从0开始）"""
        element = self.find_element(locator)
        Select(element).select_by_index(index)
        return self

    # ========== 获取信息 ==========

    def get_text(self, locator):
        """获取元素文本"""
        return self.find_visible_element(locator).text

    def get_value(self, locator):
        """获取 input 元素的 value"""
        return self.find_element(locator).get_attribute("value")

    def get_attribute(self, locator, attribute_name):
        """获取元素指定属性值"""
        return self.find_element(locator).get_attribute(attribute_name)

    def is_displayed(self, locator):
        """判断元素是否可见"""
        try:
            return self.find_element(locator).is_displayed()
        except:
            return False

    def is_enabled(self, locator):
        """判断元素是否可用"""
        try:
            return self.find_element(locator).is_enabled()
        except:
            return False

    def is_selected(self, locator):
        """判断元素是否被选中（checkbox/radio）"""
        try:
            return self.find_element(locator).is_selected()
        except:
            return False

    def is_element_exist(self, locator, timeout=3):
        """判断元素是否存在 DOM 中"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except:
            return False

    def get_element_count(self, locator):
        """获取元素数量"""
        try:
            return len(self.driver.find_elements(*locator))
        except:
            return 0

    # ========== 颜色识别 ==========
    # 核心能力：Selenium value_of_css_property + Color 工具类
    # 封装到 BasePage，测试用例一行调用即可

    def get_element_color(self, locator, css_property="color"):
        """
        获取元素颜色（返回 HEX 格式）

        Selenium 原生能力：element.value_of_css_property("color")
        返回值可能是 "rgb(255, 0, 0)" / "#ff0000" / "red" 等格式
        通过 ColorTool.normalize_css_color() 统一转为 "#rrggbb"

        Args:
            locator: 元素定位器
            css_property: CSS 属性名，常用值：
                         - "color"              文字颜色
                         - "background-color"   背景颜色
                         - "border-color"       边框颜色
                         - "outline-color"      轮廓颜色

        Returns:
            str: "#rrggbb" 格式，如 "#ff0000"

        Usage:
            color = page.get_element_color((By.CSS_SELECTOR, ".price"), "color")
            assert color == "#ff0000"
        """
        from utils.color_utils import ColorTool
        element = self.find_element(locator)
        value = element.value_of_css_property(css_property)
        hex_color = ColorTool.normalize_css_color(value)
        logger.debug(f"元素颜色 [{css_property}]: {value} → {hex_color}")
        return hex_color

    def get_element_colors(self, locator, properties=None):
        """
        批量获取元素的多个颜色属性

        Args:
            locator: 元素定位器
            properties: 要提取的属性列表，默认提取全部常用属性

        Returns:
            dict: {属性名: HEX 颜色值}

        Usage:
            colors = page.get_element_colors((By.CSS_SELECTOR, ".btn"))
            # {"color": "#ffffff", "background-color": "#1890ff", ...}
        """
        from utils.color_utils import ColorTool
        element = self.find_element(locator)
        return ColorTool.extract_colors_from_element(element, properties)

    def assert_color(self, locator, expected_hex, css_property="color", tolerance=0):
        """
        断言元素颜色

        Args:
            locator: 元素定位器
            expected_hex: 期望的 HEX 颜色值，如 "#ff0000"
            css_property: CSS 属性名，默认 "color"
            tolerance: 容差距离（默认 0 = 精确匹配）
                       - 0: 颜色必须完全一致
                       - 5-10: 允许肉眼难以区分的微小色差（推荐）
                       - 30: 允许较明显的色差

        Returns:
            self: 支持链式调用

        Usage:
            page.assert_color((By.CSS_SELECTOR, ".error"), "#ff0000")
            page.assert_color((By.CSS_SELECTOR, ".bg"), "#333333", "background-color", tolerance=10)
        """
        from utils.color_utils import ColorTool
        actual = self.get_element_color(locator, css_property)
        if tolerance > 0:
            distance = ColorTool.distance(actual, expected_hex)
            is_similar = distance <= tolerance
            logger.info(
                f"颜色断言 [{css_property}]: "
                f"期望 {expected_hex}, 实际 {actual}, "
                f"距离={distance:.1f}, 容差={tolerance}, 结果={'✓ 通过' if is_similar else '✗ 失败'}"
            )
            assert is_similar, (
                f"颜色不匹配（容差={tolerance}）: "
                f"期望 {expected_hex}，实际 {actual}，距离={distance:.1f}"
            )
        else:
            logger.info(f"颜色断言 [{css_property}]: 期望 {expected_hex}, 实际 {actual}")
            assert actual == expected_hex, (
                f"颜色不匹配: 期望 {expected_hex}，实际 {actual}"
            )
        return self

    def assert_color_name(self, locator, expected_name, css_property="color"):
        """
        断言元素颜色属于指定色系

        Args:
            locator: 元素定位器
            expected_name: 期望的语义色名，如 "red", "green", "blue"
            css_property: CSS 属性名

        Usage:
            page.assert_color_name((By.CSS_SELECTOR, ".status"), "red")    # 断言是红色系
            page.assert_color_name((By.CSS_SELECTOR, ".badge"), "green")   # 断言是绿色系
        """
        from utils.color_utils import ColorTool
        actual = self.get_element_color(locator, css_property)
        actual_name = ColorTool.get_color_name(actual)
        logger.info(f"颜色语义断言: 期望 {expected_name}, 实际 {actual} → {actual_name}")
        assert actual_name == expected_name, (
            f"颜色色系不匹配: 期望 {expected_name}，"
            f"实际 {actual} 属于 '{actual_name}'"
        )
        return self

    def assert_high_contrast(self, locator1, locator2, css_property1="color",
                             css_property2="background-color", min_ratio=4.5):
        """
        断言两个元素之间的颜色对比度满足 WCAG 标准

        常用于验证文字/背景的对比度是否满足无障碍要求

        Args:
            locator1: 元素1定位器（通常是文字元素）
            locator2: 元素2定位器（通常是背景元素）
            css_property1: 元素1的 CSS 属性
            css_property2: 元素2的 CSS 属性
            min_ratio: 最小对比度比率（默认 4.5 = WCAG AA 普通文本）

        Usage:
            page.assert_high_contrast(
                (By.CSS_SELECTOR, ".text"),
                (By.CSS_SELECTOR, ".container"),
                min_ratio=4.5
            )
        """
        from utils.color_utils import ColorTool
        color1 = self.get_element_color(locator1, css_property1)
        color2 = self.get_element_color(locator2, css_property2)
        passed = ColorTool.is_high_contrast(color1, color2, min_ratio)
        logger.info(f"对比度断言: {color1} vs {color2}, 最小比率={min_ratio}, 结果={'✓' if passed else '✗'}")
        assert passed, (
            f"颜色对比度不满足 WCAG 标准: "
            f"{color1} vs {color2}，需要 >= {min_ratio}"
        )
        return self

    def wait_for_color(self, locator, expected_hex, css_property="color",
                       timeout=None, poll=0.5):
        """
        等待元素颜色变为目标值（适用于动画、hover 效果等场景）

        Args:
            locator: 元素定位器
            expected_hex: 期望的 HEX 颜色值
            css_property: CSS 属性名
            timeout: 最大等待秒数，默认使用显式等待时间
            poll: 轮询间隔

        Returns:
            self: 支持链式调用

        Usage:
            page.hover((By.CSS_SELECTOR, ".btn"))
            page.wait_for_color((By.CSS_SELECTOR, ".btn"), "#1890ff", "background-color")
        """
        from utils.color_utils import ColorTool
        timeout = timeout or self.timeout
        deadline = time.time() + timeout

        while time.time() < deadline:
            try:
                actual = self.get_element_color(locator, css_property)
                if ColorTool.is_similar(actual, expected_hex, tolerance=10):
                    logger.info(f"等待颜色变化完成: {actual} → {expected_hex}")
                    return self
            except Exception:
                pass
            time.sleep(poll)

        actual = self.get_element_color(locator, css_property)
        raise AssertionError(
            f"等待颜色超时（{timeout}s）: 期望 {expected_hex}，实际 {actual}"
        )

    # ========== JavaScript 执行 ==========

    def execute_js(self, script, *args):
        """执行 JavaScript 脚本"""
        return self.driver.execute_script(script, *args)

    def scroll_to_element(self, locator):
        """滚动到指定元素位置"""
        element = self.find_element(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'})",
            element
        )
        time.sleep(0.3)  # 等待滚动完成
        return self

    def scroll_to_top(self):
        """滚动到页面顶部"""
        self.driver.execute_script("window.scrollTo(0, 0)")
        return self

    def scroll_to_bottom(self):
        """滚动到页面底部"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        return self

    def remove_element(self, locator):
        """通过 JS 移除元素（常用于移除遮罩层）"""
        element = self.find_element(locator)
        self.driver.execute_script(
            "arguments[0].parentNode.removeChild(arguments[0])", element
        )
        return self

    # ========== 截图 & 图片识别 ==========
    # 核心路线：
    #   模板匹配 → OpenCV（多尺度 + 特征点匹配）
    #   文字识别 → Tesseract OCR / PaddleOCR
    #   图片对比 → SSIM + 颜色直方图
    # 全部封装到 BasePage，测试用例一行调用

    def screenshot(self, save_path):
        """截取全页面截图"""
        self.driver.save_screenshot(save_path)
        return self

    def screenshot_element(self, locator, save_path):
        """
        截取指定元素截图

        Args:
            locator: 元素定位器
            save_path: 截图保存路径

        Returns:
            str: 截图文件的绝对路径
        """
        return self.image.screenshot_element(locator, save_path)

    def match_image(self, locator, template_path, threshold=None):
        """
        元素图片模板匹配（OpenCV）

        流程：截取元素截图 → 与基准图片做模板匹配
        支持：自动缩放适配、多尺度匹配

        Args:
            locator: 元素定位器
            template_path: 基准图片路径（存放在 baseline_images/ 下）
            threshold: 匹配阈值，默认 0.8

        Returns:
            tuple: (是否匹配 bool, 匹配分数 float)

        Usage:
            is_match, score = page.match_image(
                (By.ID, "logo"),
                "baseline_images/logo.png"
            )
            assert is_match, f"Logo 匹配失败，分数={score:.2f}"
        """
        import os
        temp_path = os.path.join("reports", "temp_match.png")
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        self.image.screenshot_element(locator, temp_path)
        is_match, score = ImageRecognition.match_template(temp_path, template_path, threshold)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return is_match, score

    def match_image_multiscale(self, locator, template_path, threshold=None):
        """
        多尺度模板匹配（适用于元素尺寸不确定的场景）

        在 0.5x ~ 1.5x 缩放范围内逐级匹配，取最高分

        Args:
            locator: 元素定位器
            template_path: 基准图片路径
            threshold: 匹配阈值，默认 0.8

        Returns:
            tuple: (是否匹配 bool, 最高匹配分数 float, 最佳缩放比 float)

        Usage:
            is_match, score, scale = page.match_image_multiscale(
                (By.ID, "banner"),
                "baseline_images/banner.png"
            )
        """
        import os
        temp_path = os.path.join("reports", "temp_multiscale.png")
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        self.image.screenshot_element(locator, temp_path)
        result = ImageRecognition.match_template_multiscale(temp_path, template_path, threshold)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return result

    def match_image_feature(self, locator, template_path, min_match_count=10):
        """
        特征点匹配（ORB 算法，适用于旋转/缩放/透视变换场景）

        当元素可能旋转、缩放或有透视变换时，使用特征点匹配比模板匹配更稳定

        Args:
            locator: 元素定位器
            template_path: 基准图片路径
            min_match_count: 最少匹配特征点数量，默认 10

        Returns:
            tuple: (是否匹配 bool, 匹配点数 int)

        Usage:
            is_match, count = page.match_image_feature(
                (By.CSS_SELECTOR, ".captcha-img"),
                "baseline_images/captcha_sample.png",
                min_match_count=5
            )
        """
        import os
        temp_path = os.path.join("reports", "temp_feature.png")
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        self.image.screenshot_element(locator, temp_path)
        result = ImageRecognition.match_by_feature(temp_path, template_path, min_match_count)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return result

    def compare_images(self, locator, baseline_path, threshold=0.95):
        """
        元素图片对比（SSIM 结构相似度）

        适用于回归测试：对比当前页面元素与基准图片的差异

        Args:
            locator: 元素定位器
            baseline_path: 基准图片路径
            threshold: 相似度阈值，默认 0.95

        Returns:
            tuple: (是否相似 bool, 相似度 float, 差异图片路径或 None)

        Usage:
            is_similar, score, diff_path = page.compare_images(
                (By.CSS_SELECTOR, ".chart"),
                "baseline_images/chart_expected.png"
            )
            assert is_similar, f"图表与基准不匹配, SSIM={score:.3f}"
        """
        import os
        temp_path = os.path.join("reports", "temp_compare.png")
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        self.image.screenshot_element(locator, temp_path)
        is_similar, score, diff_path = ImageRecognition.compare_images(temp_path, baseline_path, threshold)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return is_similar, score, diff_path

    def assert_image_match(self, locator, template_path, threshold=None, method="template"):
        """
        一行断言：元素图片是否匹配基准

        Args:
            locator: 元素定位器
            template_path: 基准图片路径
            threshold: 匹配阈值
            method: 匹配方法 "template"(默认) / "multiscale" / "feature"

        Returns:
            self: 支持链式调用

        Usage:
            page.assert_image_match((By.ID, "logo"), "baseline_images/logo.png")
            page.assert_image_match((By.ID, "chart"), "baseline_images/chart.png", threshold=0.9)
        """
        import allure
        if method == "multiscale":
            is_match, score, scale = self.match_image_multiscale(locator, template_path, threshold)
            msg = f"多尺度匹配: 分数={score:.4f}, 缩放={scale:.2f}"
        elif method == "feature":
            is_match, count = self.match_image_feature(locator, template_path)
            msg = f"特征匹配: 匹配点={count}"
        else:
            is_match, score = self.match_image(locator, template_path, threshold)
            msg = f"模板匹配: 分数={score:.4f}"

        # 截图附加到 Allure
        try:
            import os
            temp_path = os.path.join("reports", "temp_assert.png")
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            self.image.screenshot_element(locator, temp_path)
            if os.path.exists(temp_path):
                with open(temp_path, "rb") as f:
                    allure.attach(f.read(), name="图片匹配截图", attachment_type=allure.attachment_type.PNG)
                os.remove(temp_path)
        except Exception:
            pass

        logger.info(f"图片匹配断言: {msg}, 结果={'✓ 通过' if is_match else '✗ 失败'}")
        assert is_match, f"图片不匹配 - {msg}"
        return self

    def ocr_element(self, locator, preprocess=True):
        """
        OCR 识别页面元素文字

        适用场景：
            - Canvas 绘制的文字
            - 验证码图片
            - 图片水印
            - CSS content 生成的文字

        底层引擎：Tesseract（默认）/ 可切换 PaddleOCR

        Args:
            locator: 元素定位器
            preprocess: 是否预处理（默认 True，提升识别率）

        Returns:
            str: 识别出的文本

        Usage:
            text = page.ocr_element((By.ID, "captcha-image"))
            assert "ABCD" in text
        """
        return self.ocr.recognize_element_text(locator)

    def assert_ocr_text(self, locator, expected_text, contains=True, preprocess=True):
        """
        一行断言：OCR 识别的文本是否符合预期

        Args:
            locator: 元素定位器
            expected_text: 期望的文本
            contains: True=包含匹配（默认），False=精确匹配
            preprocess: 是否预处理图片

        Returns:
            self: 支持链式调用

        Usage:
            page.assert_ocr_text((By.ID, "captcha"), "正确")
            page.assert_ocr_text((By.CSS_SELECTOR, ".watermark"), "CONFIDENTIAL", contains=False)
        """
        actual = self.ocr.recognize_element_text(locator)
        if contains:
            passed = expected_text in actual
            msg = f"OCR 包含匹配: 期望包含 '{expected_text}'，实际 '{actual}'"
        else:
            passed = actual.strip() == expected_text.strip()
            msg = f"OCR 精确匹配: 期望 '{expected_text}'，实际 '{actual}'"

        logger.info(f"OCR 断言: {msg}, 结果={'✓ 通过' if passed else '✗ 失败'}")
        assert passed, msg
        return self

    def get_element_color_histogram(self, locator, save_path=None):
        """
        获取元素截图的颜色直方图数据

        可用于回归测试：验证页面整体色彩分布是否与基准一致

        Args:
            locator: 元素定位器
            save_path: 直方图图片保存路径（可选）

        Returns:
            dict: 颜色直方图统计 {"dominant_color": "#xxx", "mean_color": "#xxx", ...}
        """
        import os
        temp_path = os.path.join("reports", "temp_histogram.png")
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        self.image.screenshot_element(locator, temp_path)
        result = ImageRecognition.color_histogram(temp_path, save_path)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return result

    # ========== 弹窗处理 ==========

    def accept_alert(self):
        """接受弹窗"""
        alert = WebDriverWait(self.driver, self.timeout).until(
            EC.alert_is_present()
        )
        text = alert.text
        alert.accept()
        logger.info(f"接受弹窗: '{text}'")
        return text

    def dismiss_alert(self):
        """取消弹窗"""
        alert = WebDriverWait(self.driver, self.timeout).until(
            EC.alert_is_present()
        )
        text = alert.text
        alert.dismiss()
        logger.info(f"取消弹窗: '{text}'")
        return text

    # ========== Allure 集成 ==========

    def attach_screenshot_to_allure(self, name="页面截图"):
        """将当前页面截图附加到 Allure 报告"""
        try:
            import allure
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name=name,
                attachment_type=allure.attachment_type.PNG
            )
        except ImportError:
            pass

    def attach_page_source_to_allure(self, name="页面源码"):
        """将页面源码附加到 Allure 报告"""
        try:
            import allure
            allure.attach(
                self.driver.page_source,
                name=name,
                attachment_type=allure.attachment_type.HTML
            )
        except ImportError:
            pass

    # ========== Cookie ==========

    def get_cookie(self, name):
        """获取指定 cookie"""
        return self.driver.get_cookie(name)

    def set_cookie(self, name, value):
        """设置 cookie"""
        self.driver.add_cookie({"name": name, "value": value})
        return self

    def delete_cookie(self, name):
        """删除指定 cookie"""
        self.driver.delete_cookie(name)
        return self

    def delete_all_cookies(self):
        """删除所有 cookie"""
        self.driver.delete_all_cookies()
        return self
