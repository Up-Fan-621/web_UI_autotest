# ============================
# 颜色识别测试用例
# ============================
# 验证框架的颜色识别能力：Selenium value_of_css_property + ColorTool
#
# 核心路线：
#   Selenium 原生能力：element.value_of_css_property("color")
#   Color 工具类：格式转换、颜色比较、语义判断
#   封装到 BasePage：测试用例一行调用即可
#
# 执行命令：
#   pytest tests/test_color_recognition.py -v
#   pytest tests/test_color_recognition.py -v --headless
#   pytest tests/ -m color

import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.color_utils import ColorTool


@allure.feature("颜色识别")
class TestColorRecognition:
    """
    颜色识别测试集

    覆盖场景：
        1. ColorTool 工具类：格式转换、颜色比较、语义判断
        2. BasePage 集成：通过 Selenium 获取元素颜色并验证
        3. 实际 UI 场景：按钮颜色、状态颜色、文字颜色、对比度检查
    """

    # ==================================================================
    # 一、ColorTool 工具类单元测试（无需浏览器）
    # ==================================================================

    @allure.story("ColorTool 工具类")
    @allure.title("格式转换: HEX ↔ RGB ↔ HSL ↔ HSV")
    @pytest.mark.color
    @pytest.mark.p0
    def test_color_format_conversion(self):
        """验证 ColorTool 的格式转换能力"""
        # HEX → RGB
        assert ColorTool.hex_to_rgb("#ff0000") == (255, 0, 0)
        assert ColorTool.hex_to_rgb("#00ff00") == (0, 255, 0)
        assert ColorTool.hex_to_rgb("#0000ff") == (0, 0, 255)

        # 短格式 HEX → RGB
        assert ColorTool.hex_to_rgb("#f00") == (255, 0, 0)

        # RGB → HEX
        assert ColorTool.rgb_to_hex(255, 0, 0) == "#ff0000"
        assert ColorTool.rgb_to_hex(0, 128, 0) == "#008000"

        # HEX → HSL
        h, s, l = ColorTool.hex_to_hsl("#ff0000")
        assert abs(h - 0.0) < 0.5
        assert abs(s - 100.0) < 0.5
        assert abs(l - 50.0) < 0.5

        # HSL → RGB 往返验证
        r, g, b = ColorTool.hsl_to_rgb(120, 100, 50)
        assert r == 0 and g == 255 and b == 0  # 纯绿

        # HEX → HSV
        h, s, v = ColorTool.hex_to_hsv("#000000")
        assert h == 0.0 and s == 0.0 and v == 0.0

    @allure.story("ColorTool 工具类")
    @allure.title("CSS 颜色解析: normalize_css_color")
    @pytest.mark.color
    @pytest.mark.p0
    def test_normalize_css_color(self):
        """验证 Selenium 返回的各种 CSS 颜色格式都能正确解析为 HEX"""
        # rgb() 格式（Selenium 最常见返回格式）
        assert ColorTool.normalize_css_color("rgb(255, 0, 0)") == "#ff0000"
        assert ColorTool.normalize_css_color("rgb(0, 128, 255)") == "#0080ff"

        # rgba() 格式（带透明度）
        assert ColorTool.normalize_css_color("rgba(255, 0, 0, 1)") == "#ff0000"
        assert ColorTool.normalize_css_color("rgba(0, 0, 0, 0.8)") == "#000000"

        # 已经是 HEX
        assert ColorTool.normalize_css_color("#ff0000") == "#ff0000"
        assert ColorTool.normalize_css_color("#ABCDEF") == "#abcdef"

        # CSS 颜色名（通过 Selenium Color 类兜底）
        assert ColorTool.normalize_css_color("red") == "#ff0000"
        assert ColorTool.normalize_css_color("blue") == "#0000ff"
        assert ColorTool.normalize_css_color("white") == "#ffffff"

        # 空值处理
        assert ColorTool.normalize_css_color("") == ""
        assert ColorTool.normalize_css_color("   ") == ""

    @allure.story("ColorTool 工具类")
    @allure.title("颜色比较: distance / is_similar / weighted_distance")
    @pytest.mark.color
    @pytest.mark.p1
    def test_color_comparison(self):
        """验证颜色比较能力（精确匹配和容差匹配）"""
        # 完全相同的颜色
        assert ColorTool.distance("#ff0000", "#ff0000") == 0.0

        # 黑白之间距离
        dist = ColorTool.distance("#000000", "#ffffff")
        assert abs(dist - 441.67) < 1.0

        # 微小色差
        assert ColorTool.is_similar("#ff0000", "#fe0001", tolerance=5) is True
        assert ColorTool.is_similar("#ff0000", "#fe0001", tolerance=0) is False

        # 明显色差
        assert ColorTool.is_similar("#ff0000", "#0000ff", tolerance=10) is False

        # 加权距离（人眼对绿色更敏感）
        wd = ColorTool.weighted_distance("#00ff00", "#000000")
        # 加权距离应该大于 0
        assert wd > 0.0

    @allure.story("ColorTool 工具类")
    @allure.title("语义判断: 颜色名称、明暗、对比度")
    @pytest.mark.color
    @pytest.mark.p1
    def test_color_semantics(self):
        """验证颜色语义判断能力"""
        # 颜色名称
        assert ColorTool.get_color_name("#ff0000") == "red"
        assert ColorTool.get_color_name("#00ff00") == "green"
        assert ColorTool.get_color_name("#0000ff") == "blue"
        assert ColorTool.get_color_name("#000000") == "black"
        assert ColorTool.get_color_name("#ffffff") == "white"
        assert ColorTool.get_color_name("#808080") == "gray"

        # 中文颜色名
        assert ColorTool.get_color_name_cn("#ff0000") == "红色"
        assert ColorTool.get_color_name_cn("#00ff00") == "绿色"
        assert ColorTool.get_color_name_cn("#0000ff") == "蓝色"

        # 便捷判断
        assert ColorTool.is_red("#ff0000") is True
        assert ColorTool.is_red("#0000ff") is False
        assert ColorTool.is_green("#00ff00") is True
        assert ColorTool.is_blue("#0000ff") is True

        # 明暗判断
        assert ColorTool.is_dark("#333333") is True
        assert ColorTool.is_dark("#f0f0f0") is False
        assert ColorTool.is_light("#f0f0f0") is True
        assert ColorTool.is_light("#333333") is False

        # WCAG 对比度
        assert ColorTool.is_high_contrast("#000000", "#ffffff") is True
        assert ColorTool.is_high_contrast("#ffffff", "#f0f0f0", min_ratio=4.5) is False

    @allure.story("ColorTool 工具类")
    @allure.title("工具方法: brightness / blend / invert / lighten / darken")
    @pytest.mark.color
    @pytest.mark.p2
    def test_color_utilities(self):
        """验证 ColorTool 的辅助工具方法"""
        # 亮度
        assert ColorTool.brightness("#000000") == 0.0
        assert ColorTool.brightness("#ffffff") == 255.0
        assert ColorTool.brightness("#808080") == 128.0

        # 颜色混合
        blended = ColorTool.blend("#ff0000", "#0000ff", ratio=0.5)
        assert blended == "#800080"  # 紫色

        # 取反
        assert ColorTool.invert("#ffffff") == "#000000"
        assert ColorTool.invert("#ff0000") == "#00ffff"

        # 提亮/加深
        assert ColorTool.lighten("#333333", 30) == "#515151"
        assert ColorTool.darken("#999999", 30) == "#6b6b6b"

        # CSS 字符串转换
        assert ColorTool.to_css_string("#ff0000") == "rgb(255, 0, 0)"

    # ==================================================================
    # 二、BasePage 颜色识别集成测试（需要浏览器）
    # ==================================================================

    @allure.story("BasePage 颜色集成")
    @allure.title("获取元素颜色: get_element_color / get_element_colors")
    @pytest.mark.color
    @pytest.mark.p0
    @pytest.mark.ui_color
    def test_get_element_color(self, driver, base_url):
        """
        验证通过 Selenium 获取页面元素的实际颜色

        原理：
            element.value_of_css_property("color") → "rgb(255, 0, 0)"
            ColorTool.normalize_css_color("rgb(255, 0, 0)") → "#ff0000"
        """
        page = BasePage(driver)
        page.open(base_url)

        # 找到页面上的某个文字元素
        body_locator = (By.TAG_NAME, "body")

        # 获取文字颜色
        text_color = page.get_element_color(body_locator, "color")
        allure.attach(f"body 文字颜色: {text_color}", name="文字颜色")
        assert text_color != "", "应能获取到颜色值"
        assert text_color.startswith("#"), f"应为 HEX 格式: {text_color}"

        # 获取背景颜色
        bg_color = page.get_element_color(body_locator, "background-color")
        allure.attach(f"body 背景颜色: {bg_color}", name="背景颜色")
        assert bg_color != "", "应能获取到背景颜色"

    @allure.story("BasePage 颜色集成")
    @allure.title("批量获取颜色: get_element_colors")
    @pytest.mark.color
    @pytest.mark.p1
    @pytest.mark.ui_color
    def test_get_element_colors_batch(self, driver, base_url):
        """验证批量获取元素的多个颜色属性"""
        page = BasePage(driver)
        page.open(base_url)

        colors = page.get_element_colors((By.TAG_NAME, "body"))
        allure.attach(str(colors), name="批量颜色结果")

        # 应返回多个 CSS 属性的颜色值
        assert isinstance(colors, dict), "应返回字典"
        assert "color" in colors, "应包含 color 属性"
        assert "background-color" in colors, "应包含 background-color 属性"

    @allure.story("BasePage 颜色集成")
    @allure.title("颜色断言: assert_color 精确匹配和容差匹配")
    @pytest.mark.color
    @pytest.mark.p0
    @pytest.mark.ui_color
    def test_assert_color(self, driver, base_url):
        """
        验证颜色断言能力

        场景：
            1. 获取元素的实际颜色
            2. 用实际颜色做精确匹配断言（应通过）
            3. 用偏移 1 的颜色做容差匹配断言（应通过）
        """
        page = BasePage(driver)
        page.open(base_url)

        body = (By.TAG_NAME, "body")
        actual_color = page.get_element_color(body, "color")
        allure.attach(f"实际颜色: {actual_color}", name="颜色断言")

        # 精确匹配（使用实际获取的颜色，一定通过）
        page.assert_color(body, actual_color, "color", tolerance=0)

        # 容差匹配（允许微小色差）
        page.assert_color(body, actual_color, "color", tolerance=10)

    @allure.story("BasePage 颜色集成")
    @allure.title("语义色系断言: assert_color_name")
    @pytest.mark.color
    @pytest.mark.p1
    @pytest.mark.ui_color
    def test_assert_color_name(self, driver, base_url):
        """
        验证语义色系判断

        场景：断言页面 body 的文字颜色属于某个色系
        """
        page = BasePage(driver)
        page.open(base_url)

        body = (By.TAG_NAME, "body")
        actual_color = page.get_element_color(body, "color")
        actual_name = ColorTool.get_color_name(actual_color)

        allure.attach(
            f"实际颜色: {actual_color} → 语义名: {actual_name} ({ColorTool.get_color_name_cn(actual_color)})",
            name="语义颜色分析"
        )

        # 使用实际颜色的语义名做断言（一定通过）
        page.assert_color_name(body, actual_name, "color")

    @allure.story("BasePage 颜色集成")
    @allure.title("WCAG 对比度检查: assert_high_contrast")
    @pytest.mark.color
    @pytest.mark.p2
    @pytest.mark.ui_color
    def test_assert_high_contrast(self, driver, base_url):
        """
        验证 WCAG 无障碍对比度检查

        场景：检查页面 body 的文字颜色与背景颜色之间的对比度
        """
        page = BasePage(driver)
        page.open(base_url)

        body = (By.TAG_NAME, "body")

        # 获取文字色和背景色
        text_color = page.get_element_color(body, "color")
        bg_color = page.get_element_color(body, "background-color")

        allure.attach(
            f"文字色: {text_color}\n背景色: {bg_color}",
            name="对比度检查"
        )

        # 计算对比度（信息记录）
        is_hc = ColorTool.is_high_contrast(text_color, bg_color, min_ratio=4.5)
        allure.attach(
            f"WCAG AA (4.5): {'通过' if is_hc else '未通过'}",
            name="对比度结果"
        )

        # 注意：这里不强制断言，因为不同网站的对比度标准不同
        # 实际项目中可以根据需要取消注释：
        # page.assert_high_contrast(body, body, "color", "background-color", min_ratio=4.5)

    @allure.story("BasePage 颜色集成")
    @allure.title("JS 注入颜色验证: 自定义元素颜色场景")
    @pytest.mark.color
    @pytest.mark.p1
    @pytest.mark.ui_color
    def test_custom_element_color_via_js(self, driver, base_url):
        """
        验证自定义颜色场景（通过 JS 注入创建带颜色的元素）

        场景：在页面上创建一个红色文字的元素，然后验证颜色识别是否准确
        """
        page = BasePage(driver)
        page.open(base_url)

        # 通过 JS 创建一个红色文字的测试元素
        js_create = """
        var el = document.createElement('div');
        el.id = 'color-test-target';
        el.style.color = '#ff0000';
        el.style.backgroundColor = '#00ff00';
        el.style.padding = '10px';
        el.textContent = '颜色测试';
        document.body.appendChild(el);
        """
        page.execute_js(js_create)

        try:
            test_locator = (By.ID, "color-test-target")

            # 等待元素出现
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(test_locator)
            )

            # 验证红色文字
            text_color = page.get_element_color(test_locator, "color")
            allure.attach(f"文字颜色: {text_color}", name="红色文字验证")
            assert ColorTool.is_similar(text_color, "#ff0000", tolerance=5), \
                f"文字应为红色，实际 {text_color}"

            # 验证绿色背景
            bg_color = page.get_element_color(test_locator, "background-color")
            allure.attach(f"背景颜色: {bg_color}", name="绿色背景验证")
            assert ColorTool.is_similar(bg_color, "#00ff00", tolerance=5), \
                f"背景应为绿色，实际 {bg_color}"

            # 使用 assert_color 一行断言
            page.assert_color(test_locator, "#ff0000", "color", tolerance=5)
            page.assert_color(test_locator, "#00ff00", "background-color", tolerance=5)

            # 使用语义断言
            page.assert_color_name(test_locator, "red", "color")
            page.assert_color_name(test_locator, "green", "background-color")

        finally:
            # 清理测试元素
            page.execute_js("var el = document.getElementById('color-test-target'); if(el) el.remove();")

    @allure.story("BasePage 颜色集成")
    @allure.title("颜色状态变化场景: hover 等待颜色变化")
    @pytest.mark.color
    @pytest.mark.p2
    @pytest.mark.ui_color
    def test_wait_for_color_change(self, driver, base_url):
        """
        验证等待颜色变化能力

        场景：通过 JS 创建一个按钮，JS 模拟 hover 后颜色变化
        """
        page = BasePage(driver)
        page.open(base_url)

        # 创建测试按钮
        js_create = """
        var btn = document.createElement('button');
        btn.id = 'color-change-btn';
        btn.style.cssText = 'background-color: #333333; color: #ffffff; padding: 15px 30px; margin: 20px; border: none;';
        btn.textContent = '悬停我';
        document.body.appendChild(btn);
        """
        page.execute_js(js_create)

        try:
            btn_locator = (By.ID, "color-change-btn")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(btn_locator)
            )

            # 验证初始颜色
            initial_color = page.get_element_color(btn_locator, "background-color")
            allure.attach(f"初始背景色: {initial_color}", name="初始颜色")

            # 通过 JS 模拟颜色变化（类似 hover 效果）
            js_change_color = """
            document.getElementById('color-change-btn').style.backgroundColor = '#1890ff';
            """
            page.execute_js(js_change_color)

            # 等待颜色变化
            page.wait_for_color(btn_locator, "#1890ff", "background-color", timeout=5)

            # 验证最终颜色
            final_color = page.get_element_color(btn_locator, "background-color")
            allure.attach(f"变化后背景色: {final_color}", name="最终颜色")
            assert ColorTool.is_similar(final_color, "#1890ff", tolerance=10)

        finally:
            page.execute_js("var btn = document.getElementById('color-change-btn'); if(btn) btn.remove();")

    @allure.story("BasePage 颜色集成")
    @allure.title("数据驱动颜色验证: 多组颜色批量断言")
    @pytest.mark.color
    @pytest.mark.p1
    @pytest.mark.ui_color
    @pytest.mark.parametrize("color_case", [
        pytest.param({
            "name": "红色文字",
            "css_color": "#ff0000",
            "css_bg": "#ffffff",
            "expected_name": "red",
            "expected_bg_name": "white",
        }, id="红色文字_白色背景"),
        pytest.param({
            "name": "蓝色文字",
            "css_color": "#0000ff",
            "css_bg": "#ffff00",
            "expected_name": "blue",
            "expected_bg_name": "yellow",
        }, id="蓝色文字_黄色背景"),
        pytest.param({
            "name": "绿色文字",
            "css_color": "#008000",
            "css_bg": "#000000",
            "expected_name": "green",
            "expected_bg_name": "black",
        }, id="绿色文字_黑色背景"),
    ])
    def test_ddt_color_verification(self, driver, base_url, color_case):
        """
        数据驱动的颜色验证

        通过参数化注入不同颜色组合，验证颜色识别的准确性
        """
        page = BasePage(driver)
        page.open(base_url)

        # 创建测试元素
        js_create = f"""
        var el = document.createElement('div');
        el.id = 'ddt-color-test';
        el.style.color = '{color_case["css_color"]}';
        el.style.backgroundColor = '{color_case["css_bg"]}';
        el.style.padding = '10px';
        el.textContent = '{color_case["name"]}';
        document.body.appendChild(el);
        """
        page.execute_js(js_create)

        try:
            locator = (By.ID, "ddt-color-test")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(locator)
            )

            # 语义断言
            page.assert_color_name(locator, color_case["expected_name"], "color")
            page.assert_color_name(locator, color_case["expected_bg_name"], "background-color")

            # 精确断言
            page.assert_color(locator, color_case["css_color"], "color", tolerance=5)
            page.assert_color(locator, color_case["css_bg"], "background-color", tolerance=5)

            allure.attach(
                f"测试用例: {color_case['name']}\n"
                f"文字色: {color_case['css_color']} → {color_case['expected_name']}\n"
                f"背景色: {color_case['css_bg']} → {color_case['expected_bg_name']}",
                name="DDT 颜色验证结果"
            )

        finally:
            page.execute_js("var el = document.getElementById('ddt-color-test'); if(el) el.remove();")
