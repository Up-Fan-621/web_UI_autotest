# UI 自动化测试框架 — 完整使用说明

> 基于 **Selenium + Pytest + Page Object + Allure + Jenkins** 的企业级 UI 自动化测试框架。
> 包含颜色识别、图片识别（OpenCV）、OCR（Tesseract/PaddleOCR）、API 绕过 UI 造数据等高级能力。

---

## 目录

- [1. 环境准备](#1-环境准备)
- [2. 项目安装](#2-项目安装)
- [3. 项目结构](#3-项目结构)
- [4. 快速开始](#4-快速开始)
- [5. 配置说明](#5-配置说明)
- [6. 运行测试](#6-运行测试)
- [7. Allure 报告](#7-allure-报告)
- [8. 核心能力详解](#8-核心能力详解)
  - [8.1 BasePage 通用操作](#81-basepage-通用操作)
  - [8.2 颜色识别](#82-颜色识别)
  - [8.3 图片识别](#83-图片识别)
  - [8.4 OCR 文字识别](#84-ocr-文字识别)
  - [8.5 API 绕过 UI 造数据](#85-api-绕过-ui-造数据)
  - [8.6 数据库操作](#86-数据库操作)
  - [8.7 失败自动截图](#87-失败自动截图)
  - [8.8 日志系统](#88-日志系统)
- [9. 测试数据管理](#9-测试数据管理)
- [10. 测试标记与执行策略](#10-测试标记与执行策略)
- [11. 编写新用例](#11-编写新用例)
- [12. 添加新页面 PO](#12-添加新页面-po)
- [13. Jenkins CI/CD 集成](#13-jenkins-cicd-集成)
- [14. 常见问题](#14-常见问题)

---

## 1. 环境准备

### 1.1 必装软件

| 软件 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.9+ | 推荐 3.10/3.11 |
| Chrome / Firefox / Edge | 最新稳定版 | 至少装一个 |
| ChromeDriver / GeckoDriver | 与浏览器版本匹配 | 框架会自动管理（webdriver-manager） |
| Tesseract OCR | 5.x | 图片文字识别需要（可选） |

### 1.2 Windows 安装 Tesseract（可选）

```powershell
# 方式一：使用 Chocolatey
choco install tesseract

# 方式二：手动安装
# 1. 下载安装包：https://github.com/UB-Mannheim/tesseract/wiki
# 2. 安装时勾选中文语言包 chi_sim
# 3. 将安装路径加入系统 PATH（如 C:\Program Files\Tesseract-OCR）
```

### 1.3 可选增强（中文 OCR 精度更高）

```bash
pip install paddleocr paddlepaddle
```

---

## 2. 项目安装

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd ui_auto_framework

# 2. 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # Linux/Mac

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入实际的数据库、API、邮件配置
```

### 依赖清单说明

| 分类 | 包名 | 用途 |
|------|------|------|
| 测试框架 | pytest >= 7.4 | 测试执行引擎 |
| 测试插件 | pytest-xdist >= 3.5 | 并行执行 |
| 测试插件 | pytest-rerunfailures >= 12 | 失败重试 |
| 报告 | allure-pytest >= 2.13 | Allure 测试报告 |
| 浏览器 | selenium >= 4.15 | 浏览器自动化 |
| 浏览器 | webdriver-manager >= 4.0 | 自动管理浏览器驱动 |
| 图片识别 | opencv-python >= 4.8 | 模板匹配、特征点匹配 |
| 图片识别 | Pillow >= 10.0 | 图片处理 |
| 图片识别 | pytesseract >= 0.3.10 | OCR 文字识别 |
| 图片识别 | scikit-image >= 0.22 | SSIM 图片相似度对比 |
| 日志 | loguru >= 0.7 | 日志系统 |
| 数据库 | pymysql >= 1.1 | MySQL 连接 |
| HTTP | requests >= 2.31 | API 调用 |
| 数据 | PyYAML >= 6.0 | YAML 数据文件 |
| 配置 | python-dotenv >= 1.0 | 环境变量管理 |

---

## 3. 项目结构

```
ui_auto_framework/
├── config/                      # 📌 配置层
│   ├── settings.py              #   全局常量（路径、超时、DB、API、图片识别阈值）
│   ├── conftest_env.py          #   Pytest 命令行参数注册（--env/--browser/--headless）
│   └── test_config.yaml         #   YAML 环境配置（浏览器、截图、OCR、邮件）
│
├── utils/                       # 📌 工具层
│   ├── driver_manager.py        #   浏览器生命周期管理（Chrome/Firefox/Edge + 反检测）
│   ├── logger.py                #   日志系统（loguru 控制台 + 文件 + 错误分离）
│   ├── color_utils.py           #   颜色工具类（格式转换、距离比较、语义判断、WCAG）
│   ├── image_recognition.py     #   图片识别（模板匹配 + 特征点 + SSIM + OCR）
│   ├── api_utils.py             #   HTTP API 工具（造数据 / 清理数据 / 登录）
│   ├── db_utils.py              #   数据库工具（MySQL CRUD + 测试数据操作）
│   ├── screenshot_listener.py   #   失败自动截图 + Allure 附件 + StepLogger
│   ├── wait_helper.py           #   自定义等待条件（AJAX/动画/数量变化/文本）
│   └── file_utils.py            #   文件操作工具（YAML/JSON 读写 + 测试数据加载）
│
├── pages/                       # 📌 Page Object 层
│   ├── base_page.py             #   基类（810行，所有页面通用操作的唯一入口）
│   ├── login_page.py            #   登录页 PO
│   ├── home_page.py             #   首页 PO
│   ├── search_page.py           #   搜索页 PO
│   ├── order_page.py            #   订单页 PO
│   ├── register_page.py         #   注册页 PO
│   └── components/              #   可复用组件
│       ├── header.py            #     顶部导航栏
│       └── table.py             #     通用表格
│
├── data/                        # 📌 测试数据层
│   ├── test_data_login.yaml     #   登录测试数据
│   ├── test_data_search.yaml    #   搜索测试数据
│   ├── test_data_order.yaml     #   订单测试数据
│   ├── test_data_register.yaml  #   注册测试数据
│   ├── test_data_color.yaml     #   颜色识别测试数据
│   └── test_data_image.yaml     #   图片识别测试数据
│
├── tests/                       # 📌 测试用例层
│   ├── conftest.py              #   核心 Fixtures（driver/api/db/数据/清理）
│   ├── conftest_ui.py           #   数据驱动测试用例
│   ├── test_login.py            #   登录测试（正向 + 异常 + 参数化 + 安全）
│   ├── test_search.py           #   搜索测试（基础搜索 + 排序 + 翻页）
│   ├── test_order.py            #   订单测试（API造数据 + UI验证 + 交叉验证）
│   ├── test_register.py         #   注册测试（表单校验 + 异常场景）
│   ├── test_api_bypass.py       #   API 绕过 UI 专项测试
│   ├── test_color_recognition.py #  颜色识别测试（ColorTool + BasePage 集成）
│   ├── test_image_recognition.py #  图片识别测试（模板匹配 + ORB + SSIM + OCR）
│   └── test_smoke/              #   冒烟测试
│       └── test_smoke.py
│
├── reports/                     #   测试报告输出（自动生成）
│   ├── html/results/            #     Allure 原始数据
│   ├── screenshots/             #     失败截图
│   └── logs/                    #     日志文件
│
├── baseline_images/             #   基准图片（图片对比用，手动维护）
├── requirements.txt             #   Python 依赖
├── pytest.ini                   #   Pytest 全局配置
├── Jenkinsfile                  #   Jenkins Pipeline
├── .env.example                 #   环境变量模板
└── .gitignore
```

---

## 4. 快速开始

### 4.1 最快速度跑起来

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，将 base_url 改为你的测试系统地址

# 3. 修改 config/settings.py 中的 ENV_URLS
ENV_URLS = {
    "test": {
        "base_url": "https://your-test-system.com",  # ← 改这里
        ...
    }
}

# 4. 运行冒烟测试
pytest tests/test_smoke/ -m smoke --headless

# 5. 查看报告
allure serve reports/html/results
```

### 4.2 三步验证框架可用

```bash
# Step 1: 验证环境
python -c "from config.settings import ensure_dirs; ensure_dirs(); print('OK')"

# Step 2: 验证浏览器
python -c "from utils.driver_manager import DriverManager; dm = DriverManager(headless=True); d = dm.get_driver(); print(d.title); dm.quit_driver()"

# Step 3: 验证颜色识别
python -c "from utils.color_utils import ColorTool; print(ColorTool.hex_to_rgb('#ff0000'))"
```

---

## 5. 配置说明

### 5.1 多环境切换

框架支持 3 套环境：`test`（测试）、`staging`（预发）、`prod`（生产）。

**方式一：命令行参数**
```bash
pytest tests/ --env test          # 测试环境
pytest tests/ --env staging       # 预发环境
pytest tests/ --env prod          # 生产环境（谨慎！）
```

**方式二：环境变量**
```bash
set ENV=staging
pytest tests/
```

**方式三：修改 config/settings.py**
```python
ENV_URLS = {
    "test": {
        "base_url": "https://test.example.com",
        "api_url": "https://api-test.example.com",
        "db_name": "test_db"
    },
    # ... 其他环境
}
```

### 5.2 浏览器配置

```bash
# Chrome（默认）
pytest tests/ --browser chrome

# Firefox
pytest tests/ --browser firefox

# Edge
pytest tests/ --browser edge

# 无头模式（不弹出浏览器窗口）
pytest tests/ --headless

# 组合使用
pytest tests/ --browser chrome --headless
```

### 5.3 超时配置（config/settings.py）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `IMPLICIT_WAIT` | 10 秒 | 隐式等待 |
| `EXPLICIT_WAIT` | 15 秒 | 显式等待（BasePage 默认超时） |
| `PAGE_LOAD_TIMEOUT` | 30 秒 | 页面加载超时 |
| `SCRIPT_TIMEOUT` | 20 秒 | JS 执行超时 |
| `API_TIMEOUT` | 30 秒 | API 请求超时 |

### 5.4 图片识别配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `IMAGE_MATCH_THRESHOLD` | 0.8 | 模板匹配阈值（0-1，越高越严格） |
| `OCR_LANG` | chi_sim+eng | OCR 语言（中文+英文） |

### 5.5 环境变量（.env）

复制 `.env.example` 为 `.env`，填入实际值：

```bash
# 数据库
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=test_user
DB_PASSWORD=Test@123
DB_NAME=test_db

# API
API_BASE_URL=https://api-test.example.com
API_TOKEN=your_api_token_here

# 邮件通知
SMTP_HOST=smtp.company.com
SMTP_PORT=465
SMTP_USER=qa-notice@company.com
SMTP_PASSWORD=your_smtp_password
NOTIFY_EMAILS=qa-team@company.com,dev-team@company.com
```

---

## 6. 运行测试

### 6.1 基本命令

```bash
# 运行所有测试
pytest tests/

# 运行指定模块
pytest tests/test_login.py
pytest tests/test_order.py

# 运行指定用例
pytest tests/test_login.py::TestLogin::test_login_success_with_admin

# 运行指定目录
pytest tests/test_smoke/
```

### 6.2 按标记运行

```bash
# 冒烟测试（每次部署必跑）
pytest tests/ -m smoke

# P0 核心用例
pytest tests/ -m p0

# P1 重要用例
pytest tests/ -m p1

# 全量回归
pytest tests/ -m regression

# 按功能模块
pytest tests/ -m login
pytest tests/ -m search
pytest tests/ -m order

# 组合标记（同时满足多个标记）
pytest tests/ -m "smoke and login"

# 排除标记
pytest tests/ -m "not p2"
```

### 6.3 执行策略

```bash
# 失败重试（不稳定用例自动重跑 2 次）
pytest tests/ --reruns 2

# 并行执行（4 个进程同时跑）
pytest tests/ -n 4

# 并行 + 重试（推荐用于大量用例）
pytest tests/ -n 4 --reruns 1

# 指定并行数
pytest tests/ --workers 4
```

### 6.4 完整组合示例

```bash
# 典型的回归测试命令
pytest tests/ \
    --env staging \
    --browser chrome \
    --headless \
    -m "regression" \
    --reruns 1 \
    -n 4 \
    -v \
    --tb=short

# 典型的冒烟测试命令
pytest tests/test_smoke/ \
    --env test \
    --browser chrome \
    --headless \
    -m smoke \
    -v

# 本地调试（不无头，看得见浏览器操作）
pytest tests/test_login.py::TestLogin::test_login_success_with_admin \
    --env test \
    --browser chrome \
    -v -s
```

### 6.5 pytest.ini 默认参数

框架在 `pytest.ini` 中预置了默认参数，无需每次手写：

```ini
[pytest]
addopts = -v --alluredir=reports/html/results --clean-alluredir
testpaths = tests
minversion = 7.4
```

---

## 7. Allure 报告

### 7.1 生成报告

```bash
# 方式一：实时查看（启动本地服务器）
allure serve reports/html/results

# 方式二：生成静态 HTML
allure generate reports/html/results -o reports/html --clean
# 然后打开 reports/html/index.html
```

### 7.2 报告内容

Allure 报告包含以下信息：

| 内容 | 说明 |
|------|------|
| 测试结果总览 | 通过/失败/跳过数量和比例 |
| 失败截图 | 用例失败时自动截取的页面截图 |
| 浏览器日志 | 失败用例的 console 日志 |
| 页面源码 | 失败用例的 HTML 源码 |
| 测试步骤 | @allure.step 记录的操作步骤 |
| 环境信息 | 浏览器类型、环境、URL 等 |
| 趋势图 | 历史构建的通过率变化（需 Jenkins 集成） |
| 图片匹配截图 | 图片识别测试的元素截图 |

### 7.3 Allure 装饰器使用

```python
import allure

@allure.feature("功能模块")        # 一级分类
@allure.story("功能场景")          # 二级分类
@allure.title("用例标题")          # 报告中显示的名称
@allure.description("详细描述")     # 用例说明
@allure.severity(allure.severity_level.BLOCKER)  # 严重程度

# 严重程度：
# BLOCKER  — 阻塞级（冒烟测试）
# CRITICAL — 严重级
# NORMAL   — 一般级
# MINOR    — 次要级
# TRIVIAL  — 微小级

# 步骤记录
@allure.step("步骤描述")
def do_something():
    pass

# 附加信息
allure.attach(body, name="名称", attachment_type=allure.attachment_type.PNG)
# 类型：TEXT, HTML, PNG, JSON, CSV 等
```

---

## 8. 核心能力详解

### 8.1 BasePage 通用操作

BasePage 是所有页面的基类，封装了 Selenium 的通用操作，子类直接继承使用。

**页面导航**

```python
page.open("https://example.com")       # 打开页面
page.refresh()                          # 刷新
page.go_back()                          # 后退
page.go_forward()                       # 前进
page.switch_to_new_tab()                # 切换到新标签
page.switch_to_frame("iframe_id")       # 切换 iframe
page.switch_to_default_content()        # 退出 iframe
```

**元素操作**

```python
page.click((By.ID, "btn-login"))                   # 点击
page.double_click((By.ID, "item"))                  # 双击
page.right_click((By.ID, "item"))                   # 右键
page.input_text((By.ID, "username"), "admin")       # 输入文本
page.press_key((By.ID, "input"), Keys.ENTER)        # 按键
page.upload_file((By.ID, "file"), "C:/path/file")   # 上传文件
page.select_by_visible_text((By.ID, "sel"), "选项")  # 下拉选择
```

**获取信息**

```python
page.get_text((By.CSS_SELECTOR, ".msg"))            # 获取文本
page.get_value((By.ID, "input"))                     # 获取 input 的 value
page.get_attribute((By.ID, "link"), "href")          # 获取属性
page.is_displayed((By.ID, "btn"))                    # 是否可见
page.is_enabled((By.ID, "btn"))                      # 是否可用
page.is_selected((By.ID, "checkbox"))                # 是否选中
page.is_element_exist((By.ID, "modal"), timeout=3)   # 是否存在
page.get_element_count((By.CSS_SELECTOR, ".item"))   # 元素数量
```

**滚动 & JS**

```python
page.scroll_to_element((By.ID, "target"))            # 滚动到元素
page.scroll_to_top()                                  # 滚到顶部
page.scroll_to_bottom()                               # 滚到底部
page.execute_js("return document.title")              # 执行 JS
page.remove_element((By.CSS_SELECTOR, ".overlay"))   # 移除元素（去遮罩）
```

**弹窗处理**

```python
text = page.accept_alert()          # 接受弹窗，返回弹窗文本
text = page.dismiss_alert()         # 取消弹窗
```

**Cookie 操作**

```python
page.get_cookie("session_id")                       # 获取 cookie
page.set_cookie("token", "abc123")                  # 设置 cookie
page.delete_cookie("session_id")                    # 删除 cookie
page.delete_all_cookies()                           # 删除所有 cookie
```

**Allure 集成**

```python
page.attach_screenshot_to_allure("页面截图")          # 附加截图
page.attach_page_source_to_allure("页面源码")         # 附加源码
```

> **所有方法都支持链式调用**，例如：
> ```python
> page.open(url).input_text((By.ID, "user"), "admin").input_text((By.ID, "pwd"), "123").click((By.ID, "login"))
> ```

---

### 8.2 颜色识别

颜色识别基于 Selenium 的 `value_of_css_property` + `ColorTool` 工具类，测试用例一行调用即可。

> **技术路线**：Selenium 原生能力 `value_of_css_property` 提取 CSS 属性 → `ColorTool` 统一格式转换/比较/语义判断 → 封装到 `BasePage` → 测试用例一行调用

#### 获取元素颜色

```python
from selenium.webdriver.common.by import By

# 获取文字颜色
color = page.get_element_color((By.CSS_SELECTOR, ".price"), "color")
# → "#ff0000"

# 获取背景颜色
bg = page.get_element_color((By.CSS_SELECTOR, ".btn"), "background-color")
# → "#1890ff"

# 批量获取多个颜色属性
colors = page.get_element_colors((By.CSS_SELECTOR, ".card"))
# → {"color": "#333333", "background-color": "#ffffff", "border-top-color": "#eeeeee", ...}
```

#### 断言颜色

```python
# 精确匹配（颜色必须完全一致）
page.assert_color((By.CSS_SELECTOR, ".error"), "#ff0000", "color")

# 容差匹配（允许微小色差，推荐）
# tolerance=0: 精确 | 5-10: 推荐 | 30: 宽松
page.assert_color((By.CSS_SELECTOR, ".bg"), "#333333", "background-color", tolerance=10)

# 断言颜色属于指定色系（语义判断）
page.assert_color_name((By.CSS_SELECTOR, ".status"), "red")     # 是红色系
page.assert_color_name((By.CSS_SELECTOR, ".badge"), "green")   # 是绿色系

# WCAG 对比度验证（无障碍合规）
page.assert_high_contrast(
    (By.CSS_SELECTOR, ".text"),
    (By.CSS_SELECTOR, ".container"),
    min_ratio=4.5   # AA 标准普通文本
)
```

#### 等待颜色变化

```python
# 适用于 hover 效果、动画、状态切换等场景
page.wait_for_color((By.CSS_SELECTOR, ".btn"), "#1890ff", "background-color", timeout=5)
```

#### ColorTool 独立使用

```python
from utils.color_utils import ColorTool

# 格式转换
ColorTool.hex_to_rgb("#ff0000")          # → (255, 0, 0)
ColorTool.rgb_to_hex(255, 0, 0)          # → "#ff0000"
ColorTool.rgb_to_hsl(255, 0, 0)          # → (0.0, 100.0, 50.0)
ColorTool.hsl_to_rgb(0, 100, 50)         # → (255, 0, 0)
ColorTool.hex_to_hsv("#ff0000")          # → (0.0, 100.0, 100.0)

# 颜色比较
ColorTool.is_similar("#ff0000", "#fe0001", tolerance=5)    # → True
ColorTool.distance("#ff0000", "#000000")                    # → 441.67
ColorTool.weighted_distance("#ff0000", "#000000")          # → 255.0 (更贴近人眼)

# 语义判断
ColorTool.get_color_name("#ff0000")       # → "red"
ColorTool.get_color_name_cn("#ff0000")    # → "红色"
ColorTool.is_red("#ff0000")               # → True
ColorTool.is_dark("#333333")              # → True
ColorTool.is_light("#f0f0f0")             # → True
ColorTool.is_high_contrast("#000000", "#ffffff")  # → True

# 工具方法
ColorTool.brightness("#808080")           # → 128.0
ColorTool.blend("#ff0000", "#0000ff", ratio=0.5)  # → "#800080"
ColorTool.invert("#ffffff")               # → "#000000"
ColorTool.lighten("#333333", 30)          # → "#515151"
ColorTool.darken("#999999", 30)           # → "#6b6b6b"
```

#### 完整示例用例

框架提供了开箱即用的颜色识别测试用例，位于 `tests/test_color_recognition.py`：

```bash
# 运行全部颜色识别用例
pytest tests/test_color_recognition.py -v

# 仅运行 ColorTool 单元测试（无需浏览器）
pytest tests/test_color_recognition.py -v -m "color and not ui_color"

# 运行 BasePage 集成测试（需浏览器）
pytest tests/test_color_recognition.py -v -m "color and ui_color" --headless
```

**测试用例覆盖范围**：

| 用例 | 类型 | 说明 |
|------|------|------|
| `test_color_format_conversion` | 单元测试 | HEX ↔ RGB ↔ HSL ↔ HSV 格式互转 |
| `test_normalize_css_color` | 单元测试 | 解析 `rgb()` / `rgba()` / HEX / CSS 颜色名 |
| `test_color_comparison` | 单元测试 | 距离计算、容差匹配、加权距离 |
| `test_color_semantics` | 单元测试 | 颜色名称（中/英）、明暗判断、WCAG 对比度 |
| `test_color_utilities` | 单元测试 | 亮度、混合、取反、提亮、加深 |
| `test_get_element_color` | 集成测试 | Selenium 获取元素颜色 |
| `test_assert_color` | 集成测试 | 精确匹配 + 容差匹配断言 |
| `test_assert_color_name` | 集成测试 | 语义色系断言 |
| `test_assert_high_contrast` | 集成测试 | WCAG 对比度检查 |
| `test_custom_element_color_via_js` | 集成测试 | JS 注入自定义颜色元素验证 |
| `test_wait_for_color_change` | 集成测试 | 等待颜色变化（hover/动画） |
| `test_ddt_color_verification` | 集成测试 | 数据驱动批量颜色验证 |

#### YAML 测试数据

颜色识别的测试数据存储在 `data/test_data_color.yaml`：

```yaml
# data/test_data_color.yaml 结构
css_color_parse:         # Selenium CSS 颜色格式解析测试数据
color_comparison:        # 颜色比较测试数据（距离 / 容差匹配）
color_semantics:         # 语义判断测试数据（颜色名称 / 明暗 / 对比度）
ui_color_cases:          # UI 页面颜色验证数据（JS 注入测试元素）
  single_element: [...]  # 单元素颜色验证
  ddt_color_cases: [...] # 数据驱动批量验证
  color_change: {...}    # 颜色变化等待场景
  contrast_validation: [...]
```

在用例中加载 YAML 数据：

```python
from utils.file_utils import FileUtils

# 加载颜色测试数据
color_data = FileUtils.load_test_data("test_data_color.yaml")

# 使用 CSS 颜色解析数据
for case in color_data["css_color_parse"]["cases"]:
    result = ColorTool.normalize_css_color(case["css_value"])
    assert result == case["expected_hex"]

# 使用 UI 颜色验证数据
for case in color_data["ui_color_cases"]["ddt_color_cases"]:
    page.assert_color_name(locator, case["expected_name"], "color")
```

#### 落地实践：业务场景颜色验证

```python
# 场景1：验证订单状态颜色
# 待付款=橙色、已付款=蓝色、已发货=绿色、已取消=灰色、退款中=红色
order_colors = {
    "待付款": "orange",
    "已付款": "blue",
    "已发货": "green",
    "已取消": "gray",
    "退款中": "red",
}
for status, color_name in order_colors.items():
    page.assert_color_name(
        (By.CSS_SELECTOR, f".status-{status}"), color_name
    )

# 场景2：验证错误提示的视觉无障碍合规
page.assert_high_contrast(
    (By.CSS_SELECTOR, ".error-msg"),    # 错误文字
    (By.CSS_SELECTOR, ".form-card"),    # 卡片背景
    min_ratio=4.5
)

# 场景3：验证按钮 hover 后颜色变化
page.hover((By.CSS_SELECTOR, ".primary-btn"))
page.wait_for_color(
    (By.CSS_SELECTOR, ".primary-btn"),
    "#40a9ff",  # hover 后的蓝色
    "background-color",
    timeout=3
)
```

---

### 8.3 图片识别

图片识别提供三条技术路线，按场景选择：

> **选型指南**：模板匹配用 OpenCV（位置/尺寸固定），特征点用 ORB（旋转/缩放/透视），文字识别用 Tesseract/PaddleOCR。全部封装到 BasePage，一行调用。

| 场景 | 方法 | 说明 |
|------|------|------|
| 位置/尺寸固定的 UI 元素 | `match_image()` | OpenCV 模板匹配，速度快 |
| 响应式布局尺寸不确定 | `match_image_multiscale()` | 0.5x~1.5x 多尺度匹配 |
| 可能旋转/缩放/透视变换 | `match_image_feature()` | ORB 特征点匹配 |
| 回归测试对比差异 | `compare_images()` | SSIM 结构相似度 |
| 一行断言 | `assert_image_match()` | 自动截图 + Allure 附件 |

#### 模板匹配

```python
from selenium.webdriver.common.by import By

# 基础模板匹配
is_match, score = page.match_image(
    (By.ID, "logo"),
    "baseline_images/logo.png"
)
assert is_match, f"Logo 匹配失败，分数={score:.2f}"

# 自定义阈值（默认 0.8）
is_match, score = page.match_image(
    (By.ID, "icon"),
    "baseline_images/icon.png",
    threshold=0.9
)
```

#### 多尺度匹配

```python
# 响应式布局中元素尺寸不确定，自动在 0.5x~1.5x 范围内匹配
is_match, score, scale = page.match_image_multiscale(
    (By.ID, "banner"),
    "baseline_images/banner.png"
)
```

#### 特征点匹配

```python
# 适用于元素可能旋转、缩放或有透视变换
is_match, count = page.match_image_feature(
    (By.CSS_SELECTOR, ".captcha-img"),
    "baseline_images/captcha_sample.png",
    min_match_count=5
)
```

#### 图片对比（SSIM）

```python
# 回归测试：对比当前页面元素与基准图片
is_similar, score, diff_path = page.compare_images(
    (By.CSS_SELECTOR, ".chart"),
    "baseline_images/chart_expected.png",
    threshold=0.95
)
# diff_path: 差异图片路径（仅在相似度低于阈值时生成）
```

#### 一行断言

```python
# 自动截图 + 匹配 + 附加到 Allure 报告
page.assert_image_match((By.ID, "logo"), "baseline_images/logo.png")

# 指定匹配方法
page.assert_image_match((By.ID, "chart"), "baseline_images/chart.png", method="multiscale")
page.assert_image_match((By.ID, "icon"), "baseline_images/icon.png", method="feature")

# 自定义阈值
page.assert_image_match((By.ID, "logo"), "baseline_images/logo.png", threshold=0.9)
```

#### 颜色直方图

```python
# 获取元素截图的颜色分布
hist = page.get_element_color_histogram((By.CSS_SELECTOR, ".banner"), save_path="hist.png")
# → {"dominant_color": "#1890ff", "mean_color": "#4a90d9", "brightness": 150.3, ...}
```

#### 完整示例用例

框架提供了开箱即用的图片识别测试用例，位于 `tests/test_image_recognition.py`：

```bash
# 运行全部图片识别用例
pytest tests/test_image_recognition.py -v

# 仅运行单元测试（无需浏览器）
pytest tests/test_image_recognition.py -v -m "image and not ui_image"

# 运行 BasePage 集成测试（需浏览器）
pytest tests/test_image_recognition.py -v -m "image and ui_image" --headless
```

**测试用例覆盖范围**：

| 用例 | 类型 | 说明 |
|------|------|------|
| `test_color_distance` | 单元测试 | ImageRecognition 颜色距离计算 |
| `test_color_histogram_analysis` | 单元测试 | 主色调检测 + 亮度分析 |
| `test_ssim_same_image` | 单元测试 | 相同图片 SSIM 应为 1.0 |
| `test_ssim_different_images` | 单元测试 | 不同图片 SSIM + 差异图生成 |
| `test_screenshot` | 集成测试 | 全页面截图 + 元素截图 |
| `test_template_match_with_js_element` | 集成测试 | OpenCV 模板匹配 |
| `test_multiscale_match` | 集成测试 | 多尺度模板匹配 |
| `test_feature_match` | 集成测试 | ORB 特征点匹配 |
| `test_compare_images_ssim` | 集成测试 | SSIM 图片对比（回归测试） |
| `test_assert_image_match` | 集成测试 | 一行图片匹配断言 |
| `test_element_color_histogram` | 集成测试 | 页面元素颜色直方图 |
| `test_color_and_image_combined` | 集成测试 | 颜色 + 图片联合验证 |
| `test_ocr_canvas_text` | 集成测试 | OCR 识别 Canvas 文字 |
| `test_assert_ocr_text` | 集成测试 | OCR 断言方法 |
| `test_yaml_image_data` | 单元测试 | YAML 数据文件加载验证 |

#### YAML 测试数据

图片识别的测试数据存储在 `data/test_data_image.yaml`：

```yaml
# data/test_data_image.yaml 结构
template_match:           # 模板匹配测试数据
  basic_cases: [...]      #   单尺度匹配
  multiscale_cases: [...] #   多尺度匹配
feature_match:            # 特征点匹配测试数据
ssim_compare:             # SSIM 图片对比测试数据
ocr_recognition:          # OCR 文字识别测试数据
  tesseract_cases: [...]  #   Tesseract 引擎
  paddleocr_cases: [...]  #   PaddleOCR 引擎
color_histogram:          # 颜色直方图分析测试数据
business_scenarios:       # 业务场景图片验证数据
  login_page_visual: {...}
  order_status_colors: [...]
config_reference:         # 阈值参数推荐配置
  template_threshold: [...]
  ssim_threshold: [...]
  feature_params: [...]
```

在用例中加载 YAML 数据：

```python
from utils.file_utils import FileUtils

# 加载图片测试数据
img_data = FileUtils.load_test_data("test_data_image.yaml")

# 使用模板匹配配置
for case in img_data["template_match"]["basic_cases"]:
    locator = tuple(case["locator"])  # YAML 中 ["ID", "logo"] → (By.ID, "logo")
    is_match, score = page.match_image(locator, case["baseline_image"], case["threshold"])
    assert is_match == case["expected_match"]

# 使用 SSIM 对比配置
for case in img_data["ssim_compare"]["cases"]:
    locator = tuple(case["locator"])
    is_similar, score, diff = page.compare_images(
        locator, case["baseline_image"], case["threshold"]
    )
```

#### 落地实践：业务场景图片验证

```python
# 场景1：登录页 Logo 完整性检查
page.assert_image_match(
    (By.CSS_SELECTOR, ".login-logo img"),
    "baseline_images/login_logo.png"
)

# 场景2：错误提示颜色 + 对比度联合验证
page.assert_color_name((By.CSS_SELECTOR, ".error-msg"), "red")
page.assert_high_contrast(
    (By.CSS_SELECTOR, ".error-msg"),
    (By.CSS_SELECTOR, ".login-form"),
    min_ratio=3.0
)

# 场景3：订单状态颜色 + 图标匹配
for status, color_name in {"待付款": "orange", "已发货": "green"}.items():
    page.assert_color_name((By.CSS_SELECTOR, f".status-{status}"), color_name)

# 场景4：回归测试 - 图表渲染与基准对比
is_similar, score, diff_path = page.compare_images(
    (By.CSS_SELECTOR, ".sales-chart"),
    "baseline_images/sales_chart_v2.png",
    threshold=0.95
)
if diff_path:
    # 相似度不达标，差异图已自动保存，可附加到 Allure 报告
    allure.attach.file(diff_path, name="图表差异")

# 场景5：识别 Canvas 绘制的文字
canvas_text = page.ocr_element((By.ID, "dynamic-text"))
assert "预期内容" in canvas_text
```

#### 阈值参数选型参考

| 场景 | 模板匹配阈值 | SSIM 阈值 | 特征点最少匹配 |
|------|-------------|-----------|--------------|
| 精确匹配（Logo/品牌） | 0.85 | 0.99 | 15 |
| 正常匹配（按钮/图标） | 0.80 | 0.95 | 10 |
| 宽松匹配（截图模糊） | 0.60 | 0.90 | 5 |
| 仅检测布局结构 | - | 0.80 | - |

---

### 8.4 OCR 文字识别

OCR 用于识别 Selenium 无法直接获取的文本（Canvas、验证码、水印等）。

#### 基础 OCR

```python
from selenium.webdriver.common.by import By

# 识别页面元素中的文字
text = page.ocr_element((By.ID, "captcha-image"))
assert "ABCD" in text

# 预处理（默认开启，提升识别率）
text = page.ocr_element((By.ID, "captcha"), preprocess=True)
```

#### OCR 断言

```python
# 包含匹配（默认）
page.assert_ocr_text((By.ID, "captcha"), "正确")

# 精确匹配
page.assert_ocr_text((By.CSS_SELECTOR, ".watermark"), "CONFIDENTIAL", contains=False)
```

#### OCR 直接使用

```python
from utils.image_recognition import OCREngine

# 识别本地图片
ocr = OCREngine(lang="chi_sim+eng")
text = ocr.recognize_text("captcha.png", preprocess=True)

# 识别页面元素
ocr = OCREngine(driver, lang="chi_sim+eng")
text = ocr.recognize_element_text((By.ID, "captcha-image"))

# 使用 PaddleOCR（中文精度更高，需安装）
ocr = OCREngine(driver, engine="paddleocr")
text = ocr.recognize_element_text((By.ID, "captcha-image"))
```

---

### 8.5 API 绕过 UI 造数据

这是框架的核心亮点：**通过 API 快速准备测试数据，再用 UI 验证**，效率提升 10 倍以上。

#### 使用场景

| 场景 | 传统 UI 方式 | API 方式 |
|------|-------------|---------|
| 创建测试订单 | 10+ 步 UI 操作 | 1 次 API 调用 |
| 准备大量数据 | 逐条手动创建 | 批量 API 调用 |
| 设置用户余额 | 充值 → 多步操作 | 1 次 PUT 请求 |
| 测试分页 | 手动创建 50+ 条数据 | API 循环创建 |

#### Fixtures 自动造数据

```python
# conftest.py 已内置 fixture，直接使用即可

def test_order_page(self, driver, base_url, login_data, prepare_test_order):
    """
    prepare_test_order 会自动：
    1. 通过 API 创建测试订单
    2. yield 返回订单信息
    3. 测试结束后自动清理
    """
    # 直接用 UI 验证即可
    order_page = OrderPage(driver)
    assert order_page.has_orders()
```

#### API 登录 + Cookie 注入

```python
# 使用 api_login fixture（绕过 UI 登录）
def test_some_feature(self, driver, base_url, api_login):
    """
    api_login 会自动：
    1. 通过 API 登录获取 token
    2. 将 token 注入到浏览器 Cookie
    3. 测试结束后自动登出
    """
    # 此时浏览器已经是登录状态，直接操作即可
    driver.get(f"{base_url}/orders")
```

#### APIUtils 直接使用

```python
from utils.api_utils import APIUtils

api = APIUtils(base_url="https://api-test.example.com")

# 登录获取 token
result = api.login_by_api("admin", "Admin@123")
token = result.get("data", {}).get("token")

# 创建测试订单
order = api.create_test_order(user_id=1001, product_id=2001, quantity=2)

# 设置用户余额
api.set_user_balance(user_id=1001, balance=10000.00)

# 清理测试数据
api.cleanup_test_data(user_id=1001)

# 上传文件
api.upload_file("C:/path/to/file.pdf")

# 通用 API 调用
data = api.get("/api/users/1001")
result = api.post("/api/orders", json={"user_id": 1001, "product_id": 2001})
api.delete("/api/test/orders", params={"user_id": 1001})
api.put("/api/test/users/balance", json={"user_id": 1001, "balance": 5000})
```

---

### 8.6 数据库操作

```python
from utils.db_utils import DBUtils

db = DBUtils()

# 查询
user = db.fetch_one("SELECT * FROM users WHERE id = %s", (1001,))
orders = db.fetch_all("SELECT * FROM orders WHERE user_id = %s", (1001,))

# 执行
affected = db.execute("DELETE FROM orders WHERE user_id = %s AND is_test = 1", (1001,))

# 批量执行
db.execute_many(
    "INSERT INTO orders (user_id, product_id) VALUES (%s, %s)",
    [(1001, 2001), (1001, 2002), (1001, 2003)]
)

# 上下文管理器（自动关闭连接）
with db.get_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()

# 便捷方法
user = db.get_test_user(1001)
db.clean_test_orders(1001)
balance = db.get_user_balance(1001)
```

---

### 8.7 失败自动截图

框架通过 `ScreenshotListener` 自动实现失败截图，无需手动调用。

**自动触发条件：**
- 用例失败时自动截图全页面（含滚动区域）
- 截图保存到 `reports/screenshots/` 目录
- 截图自动附加到 Allure 报告

**附加信息：**
- 页面 HTML 源码
- 浏览器控制台日志

**手动截图：**
```python
# 在 BasePage 中
page.screenshot("reports/screenshots/manual.png")

# 截取元素
path = page.screenshot_element((By.ID, "chart"), "chart.png")

# 附加到 Allure
page.attach_screenshot_to_allure("关键步骤截图")
```

---

### 8.8 日志系统

日志系统基于 loguru，三路输出：

| 输出 | 路径 | 说明 |
|------|------|------|
| 控制台 | - | 彩色格式，实时查看 |
| 全量日志 | `reports/logs/ui_auto_YYYY-MM-DD.log` | 按天轮转，保留 30 天 |
| 错误日志 | `reports/logs/error_YYYY-MM-DD.log` | 只记录 ERROR 级别 |

**在代码中使用：**
```python
from utils.logger import logger

logger.info("普通信息")
logger.debug("调试信息")
logger.warning("警告信息")
logger.error("错误信息")

# Allure 日志步骤
from utils.screenshot_listener import StepLogger

# 方式一：装饰器
@StepLogger.step("登录系统")
def test_login():
    pass

# 方式二：上下文管理器
with StepLogger("输入用户名"):
    page.input_text((By.ID, "username"), "admin")
```

---

## 9. 测试数据管理

### 9.1 YAML 数据文件

所有测试数据存储在 `data/` 目录下的 YAML 文件中，零硬编码。

**数据文件结构示例（test_data_login.yaml）：**

```yaml
# 有效账号
valid_users:
  - username: "admin"
    password: "Admin@123"
    nickname: "管理员"
    role: "admin"

# 异常场景
invalid_cases:
  - case_name: "空用户名"
    username: ""
    password: "any_password"
    expected_msg: "请输入用户名"

  - case_name: "密码错误"
    username: "admin"
    password: "wrong"
    expected_msg: "用户名或密码错误"
```

### 9.2 在用例中使用测试数据

```python
# 方式一：通过 fixture 自动加载
def test_login(self, driver, base_url, login_data):
    user = login_data["valid_users"][0]
    login_page.login(user["username"], user["password"])

# 方式二：手动加载
from utils.file_utils import FileUtils
data = FileUtils.load_test_data("test_data_login.yaml")
```

### 9.3 数据驱动测试（参数化）

```python
# 方式一：直接参数化
@pytest.mark.parametrize("keyword, expected", [
    ("iPhone 16", True),
    ("不存在的商品xyz", False),
], ids=["有效关键词", "无效关键词"])
def test_search(self, driver, keyword, expected):
    page.search(keyword)
    assert page.has_results() == expected

# 方式二：从 YAML 读取参数
import pytest

test_data = FileUtils.load_test_data("test_data_search.yaml")

@pytest.mark.parametrize("case", test_data["basic_search"], ids=lambda c: c["keyword"])
def test_search(self, driver, case):
    page.search(case["keyword"])
    assert page.has_results() == case["expect_results"]
```

---

## 10. 测试标记与执行策略

### 10.1 标记体系

| 标记 | 含义 | 执行频率 | 命令 |
|------|------|---------|------|
| `@pytest.mark.smoke` | 冒烟测试 | 每次部署 | `pytest -m smoke` |
| `@pytest.mark.p0` | 核心功能 | 每次部署 | `pytest -m p0` |
| `@pytest.mark.p1` | 重要功能 | 每日构建 | `pytest -m p1` |
| `@pytest.mark.p2` | 一般功能 | 每周回归 | `pytest -m p2` |
| `@pytest.mark.regression` | 回归测试 | 发布前 | `pytest -m regression` |
| `@pytest.mark.login` | 登录模块 | 按需 | `pytest -m login` |
| `@pytest.mark.search` | 搜索模块 | 按需 | `pytest -m search` |
| `@pytest.mark.order` | 订单模块 | 按需 | `pytest -m order` |
| `@pytest.mark.color` | 颜色识别 | 按需 | `pytest -m color` |
| `@pytest.mark.image` | 图片识别 | 按需 | `pytest -m image` |
| `@pytest.mark.ui_color` | 颜色识别(需浏览器) | 按需 | `pytest -m "color and ui_color"` |
| `@pytest.mark.ui_image` | 图片识别(需浏览器) | 按需 | `pytest -m "image and ui_image"` |

### 10.2 推荐执行策略

| 阶段 | 命令 | 预计耗时 |
|------|------|---------|
| 每次提交 | `pytest tests/ -m smoke --headless -n 4` | 2-5 分钟 |
| 每日构建 | `pytest tests/ -m "p0 or p1" --headless -n 4 --reruns 1` | 10-30 分钟 |
| 发布前回归 | `pytest tests/ -m regression --headless -n 4 --reruns 2` | 30-60 分钟 |
| 全量执行 | `pytest tests/ --headless -n 4 --reruns 2` | 60+ 分钟 |

---

## 11. 编写新用例

### 11.1 标准用例模板

```python
import pytest
import allure
from selenium.webdriver.common.by import By

from pages.login_page import LoginPage
from pages.home_page import HomePage


@allure.feature("功能模块名称")
@allure.story("功能场景名称")
class TestYourFeature:
    """
    测试类描述

    覆盖范围：
        - 场景一
        - 场景二
    """

    # 可选：前置登录 fixture
    @pytest.fixture(autouse=True)
    def _login(self, driver, base_url, login_data):
        """测试前自动登录"""
        user = login_data["valid_users"][0]
        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        self.home_page = login_page.login(user["username"], user["password"])

    @allure.title("用例标题：验证 xxx 功能正常")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("详细描述这个用例测试什么")
    @pytest.mark.p1
    def test_your_case(self, driver, base_url):
        """用例描述"""
        # Step 1: 操作页面
        self.home_page.search("关键词")

        # Step 2: 断言验证
        result = self.home_page.get_result()
        assert result == "expected", f"期望 'expected'，实际 '{result}'"

    @allure.title("参数化测试: {keyword}")
    @pytest.mark.p1
    @pytest.mark.parametrize("keyword, expected", [
        ("关键词1", "结果1"),
        ("关键词2", "结果2"),
    ], ids=["场景一", "场景二"])
    def test_parametrized(self, driver, keyword, expected):
        """参数化测试"""
        self.home_page.search(keyword)
        assert self.home_page.get_result() == expected
```

### 11.2 API 造数据用例模板

```python
@allure.feature("订单管理")
class TestOrderWithAPIData:
    """API 造数据 + UI 验证"""

    @pytest.fixture(autouse=True)
    def _setup(self, driver, base_url, login_data, prepare_test_order):
        """
        prepare_test_order 是 conftest.py 中的内置 fixture：
        - 前置：通过 API 创建测试订单
        - 后置：自动清理测试数据
        """
        user = login_data["valid_users"][0]
        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        self.order_page = login_page.login(user["username"], user["password"]).go_to_orders()

    @allure.title("API创建的订单在UI中正确显示")
    @pytest.mark.p0
    def test_order_displayed(self):
        assert self.order_page.has_orders()
```

### 11.3 颜色/图片识别用例模板

```python
from selenium.webdriver.common.by import By

def test_color_validation(self, driver, base_url):
    """颜色验证示例"""
    login_page = LoginPage(driver)
    login_page.open_login_page(base_url)

    # 断言错误提示颜色为红色
    login_page.login("", "any")
    login_page.assert_color_name((By.CSS_SELECTOR, ".error-msg"), "red")

    # 断文字与背景的对比度满足 WCAG AA 标准
    login_page.assert_high_contrast(
        (By.CSS_SELECTOR, ".error-msg"),
        (By.CSS_SELECTOR, ".login-form"),
        min_ratio=4.5
    )

def test_image_match(self, driver, base_url):
    """图片匹配示例"""
    home_page = HomePage(driver)
    home_page.open(base_url)

    # 一行断言 Logo 是否正确
    home_page.assert_image_match(
        (By.CSS_SELECTOR, ".logo img"),
        "baseline_images/logo.png"
    )

def test_ocr(self, driver, base_url):
    """OCR 识别示例"""
    page = SomePage(driver)
    page.open(base_url)

    # 识别验证码
    captcha_text = page.ocr_element((By.ID, "captcha-img"))
    page.assert_ocr_text((By.ID, "captcha-img"), "正确")
```

---

## 12. 添加新页面 PO

### 12.1 创建页面类

在 `pages/` 下创建新文件，继承 `BasePage`：

```python
# pages/product_page.py

import allure
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import logger


class ProductPage(BasePage):
    """商品详情页 PO"""

    # ---------- 元素定位 ----------
    TITLE = (By.CSS_SELECTOR, ".product-title")
    PRICE = (By.CSS_SELECTOR, ".product-price")
    BTN_ADD_CART = (By.ID, "btn-add-cart")
    BTN_BUY_NOW = (By.ID, "btn-buy-now")
    TAB_DESCRIPTION = (By.CSS_SELECTOR, "[data-tab='desc']")
    TAB_REVIEWS = (By.CSS_SELECTOR, "[data-tab='reviews']")
    IMG_MAIN = (By.CSS_SELECTOR, ".main-image img")

    # ---------- 页面操作 ----------
    @allure.step("添加到购物车")
    def add_to_cart(self):
        self.click(self.BTN_ADD_CART)
        return self

    @allure.step("立即购买")
    def buy_now(self):
        self.click(self.BTN_BUY_NOW)
        return self

    @allure.step("切换到评价标签")
    def switch_to_reviews(self):
        self.click(self.TAB_REVIEWS)
        self.wait.for_ajax_complete()
        return self

    # ---------- 页面信息获取 ----------
    def get_title(self):
        return self.get_text(self.TITLE)

    def get_price(self):
        text = self.get_text(self.PRICE)
        return float(text.replace("¥", "").replace(",", ""))

    def get_main_image_color(self):
        return self.get_element_color(self.IMG_MAIN, "background-color")
```

### 12.2 页面间跳转

```python
# 在其他 PO 的方法中返回新页面对象
def go_to_product(self, product_id):
    self.driver.get(f"{self.current_url}/products/{product_id}")
    from pages.product_page import ProductPage
    return ProductPage(self.driver)
```

---

## 13. Jenkins CI/CD 集成

### 13.1 Pipeline 配置

框架已提供 `Jenkinsfile`，支持以下功能：

- **构建参数**：环境、浏览器、无头模式、测试级别、重试次数、并行数
- **自动触发**：工作日每天 9 点定时构建
- **5 个阶段**：环境准备 → 安装依赖 → 执行测试 → 生成报告 → 历史报告
- **失败通知**：邮件告警（HTML 格式，含构建详情）
- **自动清理**：构建完成后清理工作空间

### 13.2 Jenkins 配置步骤

1. **安装插件**：Allure Plugin、Pipeline
2. **新建 Pipeline 任务**，选择 "Pipeline script from SCM"
3. **配置 Git 仓库**，指向项目地址
4. **Script Path** 填 `Jenkinsfile`
5. **构建参数** 可在 Jenkins 界面选择（或保持默认）

### 13.3 本地模拟执行

```bash
# 等价于 Jenkins 的执行命令
pytest tests/ \
    --env test \
    --browser chrome \
    --headless \
    -m smoke \
    --reruns 1 \
    -n 1 \
    --alluredir=reports/html/results \
    --clean-alluredir \
    -v \
    --tb=short
```

---

## 14. 常见问题

### Q1: 提示 "chromedriver not found"

框架使用 `webdriver-manager` 自动管理，如果网络不好会失败：

```bash
# 方案一：手动下载 chromedriver 放到项目 drivers/ 目录
# 方案二：设置代理
set HTTP_PROXY=http://your-proxy:port
set HTTPS_PROXY=http://your-proxy:port
```

### Q2: Tesseract OCR 识别不准确

```bash
# 确保安装了中文语言包
tesseract --list-langs
# 应该包含 chi_sim

# 代码中启用预处理（默认已开启）
text = page.ocr_element((By.ID, "captcha"), preprocess=True)

# 或者切换到 PaddleOCR（中文精度更高）
pip install paddleocr paddlepaddle
ocr = OCREngine(driver, engine="paddleocr")
```

### Q3: 图片匹配失败怎么办

```python
# 1. 降低阈值
is_match, score = page.match_image(locator, template, threshold=0.6)

# 2. 使用多尺度匹配
is_match, score, scale = page.match_image_multiscale(locator, template)

# 3. 使用特征点匹配（更适应变化）
is_match, count = page.match_image_feature(locator, template, min_match_count=5)

# 4. 更新基准图片
# 将最新的正确截图替换 baseline_images/ 中的文件
```

### Q4: 元素等待超时

```python
# 方案一：全局调大超时（config/settings.py）
EXPLICIT_WAIT = 30  # 从 15 改为 30

# 方案二：单次调大
page.timeout = 30

# 方案三：使用自定义等待条件
from utils.wait_helper import WaitHelper
wait = WaitHelper(driver, timeout=30)
wait.for_text_contains((By.CSS_SELECTOR, ".msg"), "成功")
wait.for_element_invisible((By.ID, "loading"))
wait.for_ajax_complete()
wait.for_count_change((By.CLASS_NAME, ".item"), 5)
wait.for_animation_end((By.ID, "spinner"))
```

### Q5: 并行执行时用例互相影响

```bash
# 并行执行默认每个进程创建独立浏览器实例
# 如果用例间共享数据，确保：
# 1. 每个 fixture 使用 function 作用域（默认）
# 2. 测试数据用 API 按需创建和清理
# 3. 不依赖共享状态（如全局变量）
```

### Q6: 如何在用例中手动截图

```python
# 截取全页面
page.screenshot("reports/screenshots/my_test.png")

# 截取元素
page.screenshot_element((By.ID, "chart"), "chart.png")

# 附加到 Allure（会显示在报告中）
page.attach_screenshot_to_allure("关键步骤截图")
```

### Q7: 数据库连接失败

```python
# 确认 .env 中的数据库配置正确
# 确认数据库允许远程连接
# 确认数据库用户有足够权限

# 如果不需要数据库功能，框架会优雅降级（不影响测试执行）
# conftest.py 中 db_utils fixture 已处理异常
```

---

## 附录：Fixture 速查表

| Fixture | 作用域 | 说明 |
|---------|--------|------|
| `driver` | function | WebDriver 实例，每个用例独立 |
| `base_url` | session | 当前环境的基础 URL |
| `api_url` | session | 当前环境的 API URL |
| `env_name` | session | 当前环境名 |
| `api_utils` | session | API 工具实例 |
| `db_utils` | session | 数据库工具实例 |
| `file_utils` | session | 文件工具实例 |
| `login_data` | session | 登录测试数据 |
| `search_data` | session | 搜索测试数据 |
| `order_data` | session | 订单测试数据 |
| `register_data` | session | 注册测试数据 |
| `color_data` | session | 颜色识别测试数据 |
| `image_data` | session | 图片识别测试数据 |
| `prepare_test_order` | function | API 预创建订单 + 测试后清理 |
| `api_login` | function | API 登录 + Cookie 注入 + 测试后登出 |

---

## 附录：BasePage 方法速查表

| 方法 | 返回值 | 说明 |
|------|--------|------|
| **页面导航** | | |
| `open(url)` | self | 打开页面 |
| `refresh()` | self | 刷新页面 |
| `go_back()` | self | 后退 |
| `go_forward()` | self | 前进 |
| `switch_to_frame(ref)` | self | 切换 iframe |
| `switch_to_default_content()` | self | 退出 iframe |
| `switch_to_new_tab()` | self | 切换新标签 |
| **元素操作** | | |
| `click(locator)` | self | 点击 |
| `double_click(locator)` | self | 双击 |
| `right_click(locator)` | self | 右键 |
| `input_text(locator, text)` | self | 输入文本 |
| `press_key(locator, *keys)` | self | 按键 |
| `upload_file(locator, path)` | self | 上传文件 |
| `select_by_visible_text(loc, text)` | self | 下拉选择(文本) |
| `select_by_value(loc, value)` | self | 下拉选择(value) |
| `select_by_index(loc, index)` | self | 下拉选择(索引) |
| **获取信息** | | |
| `get_text(locator)` | str | 获取文本 |
| `get_value(locator)` | str | 获取 input value |
| `get_attribute(locator, attr)` | str | 获取属性 |
| `is_displayed(locator)` | bool | 是否可见 |
| `is_enabled(locator)` | bool | 是否可用 |
| `is_selected(locator)` | bool | 是否选中 |
| `is_element_exist(locator, timeout)` | bool | 是否存在 |
| `get_element_count(locator)` | int | 元素数量 |
| **颜色识别** | | |
| `get_element_color(loc, css_prop)` | str | 获取颜色 (#hex) |
| `get_element_colors(loc, props)` | dict | 批量获取颜色 |
| `assert_color(loc, hex, ...)` | self | 断言颜色 |
| `assert_color_name(loc, name, ...)` | self | 断言色系 |
| `assert_high_contrast(loc1, loc2, ...)` | self | 断言对比度 |
| `wait_for_color(loc, hex, ...)` | self | 等待颜色变化 |
| **图片识别** | | |
| `match_image(loc, template, ...)` | (bool, float) | 模板匹配 |
| `match_image_multiscale(loc, ...)` | (bool, float, float) | 多尺度匹配 |
| `match_image_feature(loc, ...)` | (bool, int) | 特征点匹配 |
| `compare_images(loc, baseline, ...)` | (bool, float, str) | SSIM 对比 |
| `assert_image_match(loc, template, ...)` | self | 一行断言 |
| `ocr_element(loc, ...)` | str | OCR 识别 |
| `assert_ocr_text(loc, text, ...)` | self | OCR 断言 |
| `get_element_color_histogram(loc, ...)` | dict | 颜色直方图 |
| **滚动 & JS** | | |
| `scroll_to_element(locator)` | self | 滚动到元素 |
| `scroll_to_top()` | self | 滚到顶部 |
| `scroll_to_bottom()` | self | 滚到底部 |
| `execute_js(script, *args)` | any | 执行 JS |
| `remove_element(locator)` | self | 移除元素 |
| **弹窗 & Cookie** | | |
| `accept_alert()` | str | 接受弹窗 |
| `dismiss_alert()` | str | 取消弹窗 |
| `get_cookie(name)` | dict | 获取 cookie |
| `set_cookie(name, value)` | self | 设置 cookie |
| `delete_cookie(name)` | self | 删除 cookie |
| `delete_all_cookies()` | self | 删除所有 cookie |
| **Allure** | | |
| `attach_screenshot_to_allure(name)` | None | 附加截图 |
| `attach_page_source_to_allure(name)` | None | 附加源码 |
