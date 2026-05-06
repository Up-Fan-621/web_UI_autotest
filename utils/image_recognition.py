# ============================
# 图片识别工具封装
# ============================
# 三条路线，按场景选：
#   1. 模板匹配   → OpenCV matchTemplate（精确位置/尺寸一致的 UI 元素）
#   2. 特征点匹配 → OpenCV ORB/SIFT（旋转、缩放、透视变换场景）
#   3. 文字识别   → Tesseract OCR / PaddleOCR（验证码、Canvas 文字等）
# 辅助能力：SSIM 图片对比、颜色直方图、颜色距离计算

import os
import cv2
import numpy as np
from PIL import Image
from selenium.webdriver.common.by import By
from skimage.metrics import structural_similarity as ssim

from config.settings import BASELINE_IMG_DIR, IMAGE_MATCH_THRESHOLD
from utils.logger import logger


class ImageRecognition:
    """
    图片识别工具类
    支持：元素截图、模板匹配（单尺度/多尺度）、特征点匹配、
          图片对比（SSIM）、颜色直方图、颜色距离计算

    Usage:
        ir = ImageRecognition(driver)

        # 截取元素
        ir.screenshot_element((By.ID, "logo"), "logo.png")

        # 模板匹配（标准）
        is_match, score = ir.match_template("screenshot.png", "baseline/logo.png")

        # 模板匹配（多尺度，适应尺寸变化）
        is_match, score, scale = ir.match_template_multiscale("screenshot.png", "baseline/logo.png")

        # 特征点匹配（适应旋转/缩放/透视）
        is_match, count = ir.match_by_feature("screenshot.png", "baseline/logo.png")

        # 图片相似度对比
        similarity = ir.compare_images("img1.png", "img2.png")

        # 颜色直方图对比
        hist = ir.color_histogram("screenshot.png")
    """

    def __init__(self, driver=None):
        self.driver = driver

    # ========== 截图方法 ==========

    def screenshot_element(self, locator, save_path):
        """
        截取指定元素的截图

        Args:
            locator: 元素定位器 (By.ID, "element_id")
            save_path: 截图保存路径

        Returns:
            str: 截图文件的绝对路径
        """
        element = self.driver.find_element(*locator)
        location = element.location
        size = element.size

        # 先截全屏
        self.driver.save_screenshot("temp_full.png")
        full_img = Image.open("temp_full.png")

        # 裁剪目标元素区域（考虑设备像素比 DPR）
        dpr = self._get_device_pixel_ratio()
        left = int(location['x'] * dpr)
        top = int(location['y'] * dpr)
        right = int((location['x'] + size['width']) * dpr)
        bottom = int((location['y'] + size['height']) * dpr)

        cropped = full_img.crop((left, top, right, bottom))
        cropped.save(save_path)

        # 清理临时文件
        if os.path.exists("temp_full.png"):
            os.remove("temp_full.png")

        logger.info(f"元素截图已保存: {save_path}")
        return os.path.abspath(save_path)

    def full_page_screenshot(self, save_path):
        """全页面截图"""
        self.driver.save_screenshot(save_path)
        logger.info(f"全页面截图已保存: {save_path}")
        return os.path.abspath(save_path)

    def _get_device_pixel_ratio(self):
        """获取设备像素比"""
        try:
            dpr = self.driver.execute_script("return window.devicePixelRatio")
            return dpr or 1
        except Exception:
            return 1

    # ========== 模板匹配方法 ==========

    @staticmethod
    def match_template(screenshot_path, template_path, threshold=None):
        """
        OpenCV 模板匹配（标准单尺度）

        适用场景：元素位置和尺寸固定不变的 UI 组件（按钮、图标、Logo 等）

        Args:
            screenshot_path: 页面截图路径
            template_path: 基准图片路径
            threshold: 匹配阈值，默认 0.8

        Returns:
            tuple: (是否匹配 bool, 匹配分数 float)
        """
        threshold = threshold or IMAGE_MATCH_THRESHOLD

        screenshot = cv2.imread(screenshot_path)
        template = cv2.imread(template_path)

        if screenshot is None:
            logger.error(f"无法读取截图: {screenshot_path}")
            return False, 0.0
        if template is None:
            logger.error(f"无法读取模板: {template_path}")
            return False, 0.0

        # 如果截图比模板小，尝试缩放模板
        if screenshot.shape[0] < template.shape[0] or screenshot.shape[1] < template.shape[1]:
            logger.warning("截图尺寸小于模板，尝试缩放")
            scale = min(
                screenshot.shape[0] / template.shape[0],
                screenshot.shape[1] / template.shape[1]
            )
            template = cv2.resize(template, None, fx=scale, fy=scale)

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        is_match = max_val >= threshold
        logger.info(f"模板匹配: score={max_val:.4f}, threshold={threshold}, match={is_match}")

        return is_match, float(max_val)

    @staticmethod
    def match_template_multiscale(screenshot_path, template_path, threshold=None):
        """
        多尺度模板匹配

        适用场景：响应式布局中元素尺寸不确定，需要在 0.5x~1.5x 范围内逐级匹配

        Args:
            screenshot_path: 页面截图路径
            template_path: 基准图片路径
            threshold: 匹配阈值，默认 0.8

        Returns:
            tuple: (是否匹配 bool, 最高匹配分数 float, 最佳缩放比 float)
        """
        threshold = threshold or IMAGE_MATCH_THRESHOLD

        screenshot = cv2.imread(screenshot_path)
        template = cv2.imread(template_path)

        if screenshot is None:
            logger.error(f"无法读取截图: {screenshot_path}")
            return False, 0.0, 1.0
        if template is None:
            logger.error(f"无法读取模板: {template_path}")
            return False, 0.0, 1.0

        # 在 0.5x ~ 1.5x 范围内以 0.1 步长逐级匹配
        best_score = 0.0
        best_scale = 1.0

        for scale in np.arange(0.5, 1.6, 0.1):
            scaled_w = int(template.shape[1] * scale)
            scaled_h = int(template.shape[0] * scale)

            # 跳过超出截图尺寸的缩放
            if scaled_w > screenshot.shape[1] or scaled_h > screenshot.shape[0]:
                continue

            scaled_template = cv2.resize(template, (scaled_w, scaled_h))
            result = cv2.matchTemplate(screenshot, scaled_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)

            if max_val > best_score:
                best_score = max_val
                best_scale = scale

        is_match = best_score >= threshold
        logger.info(
            f"多尺度匹配: best_score={best_score:.4f}, best_scale={best_scale:.1f}x, "
            f"threshold={threshold}, match={is_match}"
        )

        return is_match, float(best_score), float(best_scale)

    # ========== 特征点匹配 ==========

    @staticmethod
    def match_by_feature(screenshot_path, template_path, min_match_count=10):
        """
        特征点匹配（ORB 算法）

        适用场景：
            - 元素可能旋转（如加载动画）
            - 元素可能被缩放（响应式布局）
            - 元素有透视变换（3D 变换效果）
            - 模板匹配效果不理想时的备选方案

        算法选择：
            ORB 是免费开源的特征检测算法，速度快，适合大多数 UI 场景
            如需更高精度可切换 SIFT/SURF（需 OpenCV contrib）

        Args:
            screenshot_path: 页面截图路径
            template_path: 基准图片路径
            min_match_count: 最少匹配特征点数量，默认 10

        Returns:
            tuple: (是否匹配 bool, 匹配点数 int)
        """
        screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

        if screenshot is None:
            logger.error(f"无法读取截图: {screenshot_path}")
            return False, 0
        if template is None:
            logger.error(f"无法读取模板: {template_path}")
            return False, 0

        # 创建 ORB 特征检测器
        orb = cv2.ORB_create(nfeatures=1000)

        # 检测关键点和描述符
        kp1, des1 = orb.detectAndCompute(template, None)
        kp2, des2 = orb.detectAndCompute(screenshot, None)

        if des1 is None or des2 is None:
            logger.warning("特征点检测失败（可能图片过于简单）")
            return False, 0

        # 使用 BFMatcher 进行特征点匹配
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)

        # 按距离排序，取前 min_match_count 个最佳匹配
        matches = sorted(matches, key=lambda x: x.distance)
        good_matches = matches[:min_match_count]

        # 计算平均距离作为置信度参考
        avg_distance = np.mean([m.distance for m in good_matches]) if good_matches else float('inf')

        is_match = len(good_matches) >= min_match_count
        logger.info(
            f"特征点匹配: 匹配点={len(good_matches)}, "
            f"最少要求={min_match_count}, 平均距离={avg_distance:.1f}, match={is_match}"
        )

        return is_match, len(good_matches)

    # ========== 图片相似度对比 ==========

    @staticmethod
    def compare_images(img_path1, img_path2, threshold=0.95):
        """
        使用 SSIM 算法对比两张图片的相似度

        适用场景：
            - 回归测试：对比当前页面截图与基准截图
            - 验证图表/图形渲染是否一致
            - 检测页面布局是否发生意外变化

        Args:
            img_path1: 图片1路径
            img_path2: 图片2路径
            threshold: 相似度阈值

        Returns:
            tuple: (是否相似 bool, 相似度 float, 差异图片路径)
        """
        img1 = cv2.imread(img_path1)
        img2 = cv2.imread(img_path2)

        if img1 is None or img2 is None:
            logger.error("无法读取对比图片")
            return False, 0.0, None

        # 统一尺寸
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        # 转灰度
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # 计算 SSIM
        score, diff = ssim(gray1, gray2, full=True)

        # 生成差异图片
        diff_path = None
        if score < threshold:
            diff = (diff * 255).astype("uint8")
            diff_path = img_path1.replace(".png", "_diff.png")
            cv2.imwrite(diff_path, diff)
            logger.warning(f"图片差异已保存: {diff_path}")

        is_similar = score >= threshold
        logger.info(f"图片对比: SSIM={score:.4f}, threshold={threshold}, similar={is_similar}")

        return is_similar, float(score), diff_path

    # ========== 颜色直方图 ==========

    @staticmethod
    def color_histogram(image_path, save_path=None):
        """
        分析图片的颜色直方图

        适用场景：
            - 验证页面整体色调是否符合预期（如品牌色规范）
            - 检测错误状态页面的颜色变化（如红色警告区域）
            - 回归测试中检测颜色分布的异常变化

        Args:
            image_path: 图片路径
            save_path: 直方图图片保存路径（可选，保存 RGB 三通道直方图）

        Returns:
            dict: {
                "dominant_color": "#xxxxxx",  # 主色调
                "mean_color": "#xxxxxx",      # 平均颜色
                "brightness": 128.5,           # 平均亮度
                "color_distribution": {...}    # 各通道统计
            }
        """
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"无法读取图片: {image_path}")
            return {}

        # 计算平均颜色
        mean_color = img.mean(axis=(0, 1)).astype(int)
        mean_hex = "#{:02x}{:02x}{:02x}".format(*mean_color[::-1])  # BGR → RGB

        # 计算亮度
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = float(gray.mean())

        # 计算 RGB 直方图
        hist_data = {}
        channels = {"B": 0, "G": 1, "R": 2}
        for name, idx in channels.items():
            hist = cv2.calcHist([img], [idx], None, [256], [0, 256])
            peak_val = int(np.argmax(hist))
            hist_data[name] = {
                "peak": peak_val,
                "mean": float(hist.mean()),
            }

        # 找到主色调（K-means 量化到 8 色）
        dominant_hex = ImageRecognition._find_dominant_color(img)

        # 可选：保存直方图图片
        if save_path:
            ImageRecognition._plot_histogram(img, save_path)

        result = {
            "dominant_color": dominant_hex,
            "mean_color": mean_hex,
            "brightness": round(brightness, 1),
            "color_distribution": hist_data,
        }
        logger.info(f"颜色直方图: 主色调={dominant_hex}, 平均色={mean_hex}, 亮度={brightness:.1f}")
        return result

    @staticmethod
    def _find_dominant_color(img, k=8):
        """使用 K-means 聚类找到图片的主色调"""
        try:
            pixels = img.reshape(-1, 3).astype(np.float32)
            # 如果图片太大，随机采样加速
            if len(pixels) > 10000:
                indices = np.random.choice(len(pixels), 10000, replace=False)
                pixels = pixels[indices]

            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 3, cv2.KMEANS_RANDOM_CENTERS)

            # 统计每个簇的像素数，取最多的
            unique, counts = np.unique(labels, return_counts=True)
            dominant_idx = unique[np.argmax(counts)]
            b, g, r = centers[dominant_idx].astype(int)
            return "#{:02x}{:02x}{:02x}".format(r, g, b)
        except Exception as e:
            logger.warning(f"K-means 主色调分析失败: {e}")
            mean = img.mean(axis=(0, 1)).astype(int)
            return "#{:02x}{:02x}{:02x}".format(mean[2], mean[1], mean[0])

    @staticmethod
    def _plot_histogram(img, save_path):
        """生成 RGB 颜色直方图图片"""
        try:
            import matplotlib
            matplotlib.use('Agg')  # 无头模式
            import matplotlib.pyplot as plt

            colors = ('b', 'g', 'r')
            channel_names = ('Blue', 'Green', 'Red')
            plt.figure(figsize=(10, 4))
            for i, (color, name) in enumerate(zip(colors, channel_names)):
                hist = cv2.calcHist([img], [i], None, [256], [0, 256])
                plt.plot(hist, color=color, label=name, alpha=0.7)
            plt.xlim([0, 256])
            plt.xlabel('Pixel Value')
            plt.ylabel('Frequency')
            plt.title('RGB Color Histogram')
            plt.legend()
            plt.tight_layout()
            plt.savefig(save_path, dpi=100)
            plt.close()
            logger.info(f"直方图已保存: {save_path}")
        except ImportError:
            logger.warning("matplotlib 未安装，跳过直方图图片生成（pip install matplotlib）")

    # ========== 颜色距离计算 ==========

    @staticmethod
    def color_distance(hex1, hex2):
        """
        计算两个颜色的欧氏距离

        Args:
            hex1: 颜色1 (#rrggbb)
            hex2: 颜色2 (#rrggbb)

        Returns:
            float: 距离值，0 表示完全相同，最大约 441
        """
        r1, g1, b1 = int(hex1[1:3], 16), int(hex1[3:5], 16), int(hex1[5:7], 16)
        r2, g2, b2 = int(hex2[1:3], 16), int(hex2[3:5], 16), int(hex2[5:7], 16)
        return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5

    def get_element_color(self, locator, css_property="color"):
        """
        获取元素的颜色值

        Args:
            locator: 元素定位器
            css_property: CSS 属性名 (color / background-color / border-color)

        Returns:
            str: hex 格式颜色值，如 "#ff0000"
        """
        from utils.color_utils import ColorTool
        value = self.driver.find_element(*locator).value_of_css_property(css_property)
        return ColorTool.normalize_css_color(value)

    def assert_element_color(self, locator, expected_hex, css_property="color", tolerance=0):
        """
        断言元素颜色

        Args:
            locator: 元素定位器
            expected_hex: 期望的 hex 颜色值
            css_property: CSS 属性名
            tolerance: 容差距离（0=精确匹配，>0=允许色差）
        """
        from utils.color_utils import ColorTool
        actual = self.get_element_color(locator, css_property)
        if tolerance > 0:
            distance = ColorTool.distance(actual, expected_hex)
            assert distance <= tolerance, (
                f"颜色不匹配（容差={tolerance}）: "
                f"期望 {expected_hex}，实际 {actual}，距离={distance:.1f}"
            )
        else:
            assert actual == expected_hex, (
                f"颜色不匹配: 期望 {expected_hex}，实际 {actual}"
            )


class OCREngine:
    """
    OCR 文字识别引擎
    支持多引擎切换：
        - Tesseract（默认，开源免费）
        - PaddleOCR（可选，中文识别精度更高，需安装 paddleocr）

    适用场景：
        - Canvas 绘制的文字
        - 验证码图片
        - 图片水印
        - CSS content 生成的文字
        - 其他 Selenium 无法直接获取的文本

    Usage:
        ocr = OCREngine()
        text = ocr.recognize_text("captcha.png")

        # 直接识别页面元素
        ocr = OCREngine(driver)
        text = ocr.recognize_element_text((By.ID, "captcha-image"))

        # 使用 PaddleOCR 引擎
        ocr = OCREngine(engine="paddleocr")
        text = ocr.recognize_text("captcha.png")
    """

    # 引擎类型
    ENGINE_TESSERACT = "tesseract"
    ENGINE_PADDLEOCR = "paddleocr"

    def __init__(self, driver=None, lang="chi_sim+eng", engine="tesseract"):
        """
        Args:
            driver: WebDriver 实例（可选，用于直接截取元素）
            lang: OCR 识别语言
            engine: 识别引擎 "tesseract"(默认) / "paddleocr"
        """
        self.driver = driver
        self.lang = lang
        self.engine = engine
        self._paddle_ocr = None

        if engine == self.ENGINE_PADDLEOCR:
            self._init_paddleocr()

    def _init_paddleocr(self):
        """初始化 PaddleOCR 引擎"""
        try:
            from paddleocr import PaddleOCR
            self._paddle_ocr = PaddleOCR(
                use_angle_cls=True,
                lang="ch",
                show_log=False,
            )
            logger.info("PaddleOCR 引擎初始化成功")
        except ImportError:
            logger.warning(
                "PaddleOCR 未安装，将回退到 Tesseract。"
                "安装方法: pip install paddleocr paddlepaddle"
            )
            self.engine = self.ENGINE_TESSERACT
        except Exception as e:
            logger.warning(f"PaddleOCR 初始化失败: {e}，将回退到 Tesseract")
            self.engine = self.ENGINE_TESSERACT

    def recognize_text(self, image_path, preprocess=False):
        """
        识别图片中的文字

        Args:
            image_path: 图片路径
            preprocess: 是否预处理（二值化、去噪）

        Returns:
            str: 识别出的文本
        """
        if self.engine == self.ENGINE_PADDLEOCR and self._paddle_ocr:
            return self._recognize_paddleocr(image_path)
        else:
            return self._recognize_tesseract(image_path, preprocess)

    def _recognize_tesseract(self, image_path, preprocess=False):
        """使用 Tesseract 识别文字"""
        try:
            import pytesseract
        except ImportError:
            logger.error("请安装 pytesseract: pip install pytesseract")
            raise

        if preprocess:
            image_path = self._preprocess_image(image_path)

        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=self.lang)
            result = text.strip()
            logger.info(f"Tesseract OCR 识别结果: '{result}'")
            return result
        except Exception as e:
            logger.error(f"Tesseract OCR 识别失败: {e}")
            return ""

    def _recognize_paddleocr(self, image_path):
        """使用 PaddleOCR 识别文字"""
        try:
            result = self._paddle_ocr.ocr(image_path, cls=True)
            if result and result[0]:
                texts = [line[1][0] for line in result[0]]
                combined = "".join(texts)
                logger.info(f"PaddleOCR 识别结果: '{combined}'")
                return combined
            return ""
        except Exception as e:
            logger.error(f"PaddleOCR 识别失败: {e}")
            return ""

    def recognize_element_text(self, locator):
        """
        直接识别页面元素的文字（先截图再 OCR）

        Args:
            locator: 元素定位器

        Returns:
            str: 识别出的文本
        """
        if not self.driver:
            raise ValueError("需要提供 driver 实例才能识别页面元素")

        element = self.driver.find_element(*locator)
        location = element.location
        size = element.size

        self.driver.save_screenshot("temp_ocr.png")
        img = Image.open("temp_ocr.png")

        dpr = self.driver.execute_script("return window.devicePixelRatio") or 1
        left = int(location['x'] * dpr)
        top = int(location['y'] * dpr)
        right = int((location['x'] + size['width']) * dpr)
        bottom = int((location['y'] + size['height']) * dpr)

        cropped = img.crop((left, top, right, bottom))
        cropped_path = "temp_ocr_cropped.png"
        cropped.save(cropped_path)

        # Tesseract 使用预处理，PaddleOCR 不需要
        preprocess = self.engine == self.ENGINE_TESSERACT
        text = self.recognize_text(cropped_path, preprocess=preprocess)

        # 清理临时文件
        for f in ["temp_ocr.png", "temp_ocr_cropped.png"]:
            if os.path.exists(f):
                os.remove(f)

        return text

    @staticmethod
    def _preprocess_image(image_path):
        """
        图片预处理以提高 OCR 准确率

        Steps:
        1. 灰度化
        2. 高斯模糊去噪
        3. 自适应二值化
        4. 膨胀腐蚀去噪点

        Returns:
            str: 处理后的图片路径
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        # 高斯模糊
        img = cv2.GaussianBlur(img, (3, 3), 0)

        # 自适应二值化
        img = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # 膨胀腐蚀
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)

        processed_path = image_path.replace(".png", "_processed.png")
        cv2.imwrite(processed_path, img)
        return processed_path
