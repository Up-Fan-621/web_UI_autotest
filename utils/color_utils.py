# ============================
# Color 颜色工具类
# ============================
# 基于 Selenium WebDriver 的 value_of_css_property + Color 能力
# 封装颜色格式转换、颜色空间比较、批量提取、语义判断等能力
#
# Usage:
#     from utils.color_utils import ColorTool
#
#     # 格式互转
#     ColorTool.hex_to_rgb("#ff0000")          # → (255, 0, 0)
#     ColorTool.rgb_to_hex(255, 0, 0)           # → "#ff0000"
#     ColorTool.hsl_to_rgb(0, 100, 50)          # → (255, 0, 0)
#
#     # 颜色比较
#     ColorTool.is_similar("#ff0000", "#fe0001", tolerance=5)   # → True
#     ColorTool.distance("#ff0000", "#000000")                    # → 441.67
#
#     # 语义判断
#     ColorTool.is_red("#ff0000")               # → True
#     ColorTool.is_dark("#333333")               # → True
#
#     # 从 Selenium 元素提取
#     color_value = element.value_of_css_property("color")
#     ColorTool.normalize_css_color(color_value) # → "#ff0000"

import math
import re
from enum import Enum


class ColorSpace(Enum):
    """颜色空间类型"""
    RGB = "rgb"
    HEX = "hex"
    HSL = "hsl"
    HSV = "hsv"


# ---- 预定义颜色语义表 ----
_SEMANTIC_COLORS = {
    "red":     [(0, 10), (345, 360)],    # hue range (low, high)
    "orange":  [(10, 45)],
    "yellow":  [(45, 70)],
    "green":   [(70, 170)],
    "cyan":    [(170, 200)],
    "blue":    [(200, 265)],
    "purple":  [(265, 310)],
    "pink":    [(310, 345)],
}

_SEMANTIC_NAMES_CN = {
    "red": "红色", "orange": "橙色", "yellow": "黄色", "green": "绿色",
    "cyan": "青色", "blue": "蓝色", "purple": "紫色", "pink": "粉色",
    "white": "白色", "black": "黑色", "gray": "灰色",
}


class ColorTool:
    """
    颜色工具类 —— 一站式颜色操作

    核心能力：
        1. 格式转换：HEX ↔ RGB ↔ HSL ↔ HSV ↔ CSS 字符串
        2. 颜色比较：欧氏距离、加权距离（感知更均匀）、语义匹配
        3. 语义判断：判断颜色名称、明暗、是否属于指定色系
        4. 与 Selenium 集成：直接解析 value_of_css_property 返回值

    所有公开方法均为 @staticmethod，无需实例化即可调用。
    """

    # =====================================================================
    # 1. 格式转换
    # =====================================================================

    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple:
        """
        HEX → RGB

        Args:
            hex_color: "#rrggbb" 或 "rrggbb" 或 "#rgb"

        Returns:
            tuple: (r, g, b) 各分量 0-255

        Raises:
            ValueError: 格式不合法
        """
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join(c * 2 for c in hex_color)
        if len(hex_color) != 6 or not all(c in "0123456789abcdefABCDEF" for c in hex_color):
            raise ValueError(f"无效的 HEX 颜色: {hex_color}")
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )

    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """
        RGB → HEX

        Args:
            r, g, b: 各分量 0-255

        Returns:
            str: "#rrggbb"
        """
        for val, name in [(r, "r"), (g, "g"), (b, "b")]:
            if not 0 <= val <= 255:
                raise ValueError(f"{name} 值 {val} 超出范围 0-255")
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def rgb_to_hsl(r: int, g: int, b: int) -> tuple:
        """
        RGB → HSL

        Returns:
            tuple: (h, s, l) 其中 h 0-360, s 0-100, l 0-100
        """
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        l = (max_c + min_c) / 2.0

        if max_c == min_c:
            h = s = 0.0
        else:
            d = max_c - min_c
            s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)

            if max_c == r:
                h = (g - b) / d + (6.0 if g < b else 0.0)
            elif max_c == g:
                h = (b - r) / d + 2.0
            else:
                h = (r - g) / d + 4.0

            h *= 60.0

        return round(h, 1), round(s * 100, 1), round(l * 100, 1)

    @staticmethod
    def hsl_to_rgb(h: float, s: float, l: float) -> tuple:
        """
        HSL → RGB

        Args:
            h: 0-360
            s: 0-100
            l: 0-100

        Returns:
            tuple: (r, g, b) 各分量 0-255
        """
        s, l = s / 100.0, l / 100.0
        c = (1.0 - abs(2.0 * l - 1.0)) * s
        x = c * (1.0 - abs((h / 60.0) % 2 - 1.0))
        m = l - c / 2.0

        if h < 60:
            r1, g1, b1 = c, x, 0
        elif h < 120:
            r1, g1, b1 = x, c, 0
        elif h < 180:
            r1, g1, b1 = 0, c, x
        elif h < 240:
            r1, g1, b1 = 0, x, c
        elif h < 300:
            r1, g1, b1 = x, 0, c
        else:
            r1, g1, b1 = c, 0, x

        return (
            round((r1 + m) * 255),
            round((g1 + m) * 255),
            round((b1 + m) * 255),
        )

    @staticmethod
    def rgb_to_hsv(r: int, g: int, b: int) -> tuple:
        """
        RGB → HSV

        Returns:
            tuple: (h, s, v) 其中 h 0-360, s 0-100, v 0-100
        """
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        d = max_c - min_c
        v = max_c

        if max_c == 0:
            s = 0.0
        else:
            s = d / max_c

        if max_c == min_c:
            h = 0.0
        else:
            if max_c == r:
                h = (g - b) / d + (6.0 if g < b else 0.0)
            elif max_c == g:
                h = (b - r) / d + 2.0
            else:
                h = (r - g) / d + 4.0
            h *= 60.0

        return round(h, 1), round(s * 100, 1), round(v * 100, 1)

    @staticmethod
    def hex_to_hsl(hex_color: str) -> tuple:
        """HEX → HSL"""
        r, g, b = ColorTool.hex_to_rgb(hex_color)
        return ColorTool.rgb_to_hsl(r, g, b)

    @staticmethod
    def hex_to_hsv(hex_color: str) -> tuple:
        """HEX → HSV"""
        r, g, b = ColorTool.hex_to_rgb(hex_color)
        return ColorTool.rgb_to_hsv(r, g, b)

    # =====================================================================
    # 2. Selenium CSS 颜色解析
    # =====================================================================

    @staticmethod
    def normalize_css_color(css_value: str) -> str:
        """
        解析 Selenium value_of_css_property 返回的颜色值，统一转为 HEX

        Selenium 返回的 CSS 颜色值可能格式：
            - "rgb(255, 0, 0)"        ← 最常见
            - "rgba(255, 0, 0, 1)"    ← 带透明度
            - "#ff0000"                ← 已经是 HEX
            - "red"                    ← CSS 颜色名
            - ""                       ← 无颜色

        Args:
            css_value: value_of_css_property 的原始返回值

        Returns:
            str: "#rrggbb" 格式，或空字符串表示无颜色
        """
        if not css_value or css_value.strip() == "":
            return ""

        css_value = css_value.strip()

        # 已经是 HEX
        if css_value.startswith("#"):
            return css_value.lower()

        # rgb() / rgba()
        rgb_match = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", css_value)
        if rgb_match:
            r, g, b = int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3))
            return ColorTool.rgb_to_hex(r, g, b)

        # 使用 Selenium 内置 Color 类兜底
        try:
            from selenium.webdriver.support.color import Color
            return Color.from_string(css_value).hex
        except Exception:
            return ""

    @staticmethod
    def extract_colors_from_element(element, properties=None):
        """
        从一个 Selenium WebElement 批量提取多个 CSS 颜色属性

        Args:
            element: Selenium WebElement
            properties: 要提取的属性列表，默认提取常用属性

        Returns:
            dict: {属性名: HEX 颜色值}，如 {"color": "#ff0000", "background-color": "#ffffff"}
        """
        if properties is None:
            properties = [
                "color",
                "background-color",
                "border-top-color",
                "border-bottom-color",
                "border-left-color",
                "border-right-color",
                "outline-color",
            ]

        result = {}
        for prop in properties:
            try:
                raw = element.value_of_css_property(prop)
                hex_val = ColorTool.normalize_css_color(raw)
                result[prop] = hex_val
            except Exception:
                result[prop] = ""
        return result

    # =====================================================================
    # 3. 颜色比较
    # =====================================================================

    @staticmethod
    def distance(hex1: str, hex2: str) -> float:
        """
        计算两个 HEX 颜色的 RGB 欧氏距离

        距离范围：0（完全相同） ~ 441.67（黑白之间）
        经验值：距离 < 10 视觉上几乎无法区分

        Args:
            hex1: "#rrggbb"
            hex2: "#rrggbb"

        Returns:
            float: 欧氏距离
        """
        r1, g1, b1 = ColorTool.hex_to_rgb(hex1)
        r2, g2, b2 = ColorTool.hex_to_rgb(hex2)
        return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

    @staticmethod
    def weighted_distance(hex1: str, hex2: str) -> float:
        """
        加权欧氏距离（考虑人眼对绿色更敏感的感知差异）

        权重基于 Rec. 601 标准：R=0.299, G=0.587, B=0.114
        比纯欧氏距离更贴近人眼的实际感受

        Args:
            hex1: "#rrggbb"
            hex2: "#rrggbb"

        Returns:
            float: 加权距离
        """
        r1, g1, b1 = ColorTool.hex_to_rgb(hex1)
        r2, g2, b2 = ColorTool.hex_to_rgb(hex2)
        dr = r1 - r2
        dg = g1 - g2
        db = b1 - b2
        return math.sqrt(
            0.299 * dr * dr + 0.587 * dg * dg + 0.114 * db * db
        )

    @staticmethod
    def is_similar(hex1: str, hex2: str, tolerance: float = 10.0) -> bool:
        """
        判断两个颜色是否视觉上相似

        Args:
            hex1: "#rrggbb"
            hex2: "#rrggbb"
            tolerance: 容差阈值，默认 10（推荐范围 5-30）
                       - 3: 严格匹配，几乎完全相同
                       - 10: 正常使用，肉眼难以区分
                       - 30: 宽松匹配，允许明显色差

        Returns:
            bool: True 表示在容差范围内相似
        """
        return ColorTool.distance(hex1, hex2) <= tolerance

    @staticmethod
    def is_similar_weighted(hex1: str, hex2: str, tolerance: float = 8.0) -> bool:
        """
        使用加权距离判断颜色相似（更贴近人眼感知）

        Args:
            hex1, hex2: "#rrggbb"
            tolerance: 默认 8（经验值，肉眼难以区分的阈值）
        """
        return ColorTool.weighted_distance(hex1, hex2) <= tolerance

    # =====================================================================
    # 4. 颜色语义判断
    # =====================================================================

    @staticmethod
    def get_color_name(hex_color: str) -> str:
        """
        获取颜色的语义名称（英文）

        Args:
            hex_color: "#rrggbb"

        Returns:
            str: 颜色名，如 "red", "green", "white", "black", "gray"
        """
        r, g, b = ColorTool.hex_to_rgb(hex_color)
        h, s, l = ColorTool.rgb_to_hsl(r, g, b)

        # 无彩色判断（饱和度很低）
        if s < 10:
            if l < 15:
                return "black"
            elif l > 90:
                return "white"
            else:
                return "gray"

        # 有彩色：通过色相判断
        for name, hue_ranges in _SEMANTIC_COLORS.items():
            for low, high in hue_ranges:
                if low <= h <= high:
                    return name

        # 色相环绕（red 在 0 和 360 附近）
        if h >= 345 or h <= 10:
            return "red"

        return "unknown"

    @staticmethod
    def get_color_name_cn(hex_color: str) -> str:
        """获取颜色的中文语义名称"""
        name_en = ColorTool.get_color_name(hex_color)
        return _SEMANTIC_NAMES_CN.get(name_en, "未知")

    @staticmethod
    def is_red(hex_color: str) -> bool:
        """判断是否为红色"""
        return ColorTool.get_color_name(hex_color) == "red"

    @staticmethod
    def is_green(hex_color: str) -> bool:
        """判断是否为绿色"""
        return ColorTool.get_color_name(hex_color) == "green"

    @staticmethod
    def is_blue(hex_color: str) -> bool:
        """判断是否为蓝色"""
        return ColorTool.get_color_name(hex_color) == "blue"

    @staticmethod
    def is_dark(hex_color: str, threshold: int = 128) -> bool:
        """
        判断颜色是否偏暗

        Args:
            hex_color: "#rrggbb"
            threshold: 亮度阈值，默认 128

        Returns:
            bool: True 表示偏暗
        """
        r, g, b = ColorTool.hex_to_rgb(hex_color)
        # 使用 ITU-R BT.601 亮度公式
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance < threshold

    @staticmethod
    def is_light(hex_color: str, threshold: int = 200) -> bool:
        """判断颜色是否偏亮"""
        r, g, b = ColorTool.hex_to_rgb(hex_color)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance >= threshold

    @staticmethod
    def is_high_contrast(hex1: str, hex2: str, min_ratio: float = 4.5) -> bool:
        """
        判断两个颜色之间是否满足 WCAG 对比度标准

        Args:
            hex1: "#rrggbb"
            hex2: "#rrggbb"
            min_ratio: 最小对比度比率，默认 4.5（AA 标准普通文本）
                       - 1.0: 无约束
                       - 3.0: AA 大文本 / UI 组件
                       - 4.5: AA 普通文本
                       - 7.0: AAA 增强对比

        Returns:
            bool: True 表示对比度满足要求
        """
        def relative_luminance(hex_color):
            r, g, b = ColorTool.hex_to_rgb(hex_color)
            def linearize(c):
                c = c / 255.0
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)

        l1 = relative_luminance(hex1)
        l2 = relative_luminance(hex2)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        ratio = (lighter + 0.05) / (darker + 0.05)
        return ratio >= min_ratio

    # =====================================================================
    # 5. 工具方法
    # =====================================================================

    @staticmethod
    def brightness(hex_color: str) -> float:
        """计算颜色的相对亮度（0-255）"""
        r, g, b = ColorTool.hex_to_rgb(hex_color)
        return 0.299 * r + 0.587 * g + 0.114 * b

    @staticmethod
    def blend(hex1: str, hex2: str, ratio: float = 0.5) -> str:
        """
        混合两个颜色

        Args:
            hex1: 颜色1
            hex2: 颜色2
            ratio: 混合比例 0.0-1.0，0.0 全部为 hex1，1.0 全部为 hex2

        Returns:
            str: 混合后的 HEX 颜色
        """
        r1, g1, b1 = ColorTool.hex_to_rgb(hex1)
        r2, g2, b2 = ColorTool.hex_to_rgb(hex2)
        r = round(r1 + (r2 - r1) * ratio)
        g = round(g1 + (g2 - g1) * ratio)
        b = round(b1 + (b2 - b1) * ratio)
        return ColorTool.rgb_to_hex(r, g, b)

    @staticmethod
    def invert(hex_color: str) -> str:
        """颜色取反"""
        r, g, b = ColorTool.hex_to_rgb(hex_color)
        return ColorTool.rgb_to_hex(255 - r, 255 - g, 255 - b)

    @staticmethod
    def lighten(hex_color: str, amount: int = 30) -> str:
        """
        提亮颜色

        Args:
            hex_color: 原始颜色
            amount: 提亮程度 0-255

        Returns:
            str: 提亮后的 HEX 颜色
        """
        r, g, b = ColorTool.hex_to_rgb(hex_color)
        r = min(255, r + amount)
        g = min(255, g + amount)
        b = min(255, b + amount)
        return ColorTool.rgb_to_hex(r, g, b)

    @staticmethod
    def darken(hex_color: str, amount: int = 30) -> str:
        """加深颜色"""
        r, g, b = ColorTool.hex_to_rgb(hex_color)
        r = max(0, r - amount)
        g = max(0, g - amount)
        b = max(0, b - amount)
        return ColorTool.rgb_to_hex(r, g, b)

    @staticmethod
    def to_css_string(hex_color: str) -> str:
        """将 HEX 转为 CSS rgb() 字符串"""
        r, g, b = ColorTool.hex_to_rgb(hex_color)
        return f"rgb({r}, {g}, {b})"
