# ============================
# LoginPage - 登录页面对象
# ============================

import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import logger


class LoginPage(BasePage):
    """
    登录页面 PO

    页面元素：用户名输入框、密码输入框、登录按钮、记住我、错误提示、注册链接
    页面操作：登录、跳转注册、获取错误信息、判断是否已显示
    """

    # ---------- URL ----------
    URL_PATH = "/login"

    # ---------- 元素定位 ----------
    INPUT_USERNAME    = (By.ID, "username")
    INPUT_PASSWORD    = (By.ID, "password")
    BTN_LOGIN         = (By.ID, "btn-login")
    BTN_SUBMIT        = (By.CSS_SELECTOR, "button[type='submit']")
    CHECKBOX_REMEMBER = (By.ID, "remember-me")
    LINK_FORGET_PWD   = (By.LINK_TEXT, "忘记密码")
    LINK_REGISTER     = (By.LINK_TEXT, "立即注册")
    MSG_ERROR         = (By.CSS_SELECTOR, ".error-msg")
    MSG_SUCCESS       = (By.CSS_SELECTOR, ".success-msg")
    IFRAME_LOGIN      = (By.ID, "login-iframe")
    ICON_LOADING      = (By.CSS_SELECTOR, ".loading-icon")
    LOGO_IMAGE        = (By.CSS_SELECTOR, ".login-logo img")

    # ---------- 页面访问 ----------

    def open_login_page(self, base_url):
        """打开登录页面"""
        url = f"{base_url.rstrip('/')}{self.URL_PATH}"
        logger.info(f"打开登录页: {url}")

        # 有些系统的登录页在 iframe 中
        try:
            if self.is_element_exist(self.IFRAME_LOGIN, timeout=3):
                self.switch_to_frame(self.IFRAME_LOGIN)
        except Exception:
            pass

        self.open(url)
        return self

    # ---------- 页面操作 ----------

    @allure.step("输入用户名: {username}")
    def input_username(self, username):
        """输入用户名"""
        self.input_text(self.INPUT_USERNAME, username)
        return self

    @allure.step("输入密码: ******")
    def input_password(self, password):
        """输入密码"""
        self.input_text(self.INPUT_PASSWORD, password)
        return self

    @allure.step("点击登录按钮")
    def click_login(self):
        """点击登录按钮"""
        self.click(self.BTN_LOGIN)
        # 等待加载图标消失
        try:
            self.wait.for_element_invisible(self.ICON_LOADING, timeout=10)
        except Exception:
            pass
        return self

    @allure.step("执行登录: username={username}")
    def login(self, username, password):
        """
        完整登录流程

        Args:
            username: 用户名
            password: 密码

        Returns:
            HomePage: 登录成功后跳转到首页
        """
        self.input_username(username)
        self.input_password(password)
        self.click_login()
        from pages.home_page import HomePage
        return HomePage(self.driver)

    def login_with_remember(self, username, password):
        """勾选"记住我"后登录"""
        self.input_username(username)
        self.input_password(password)
        if not self.is_selected(self.CHECKBOX_REMEMBER):
            self.click(self.CHECKBOX_REMEMBER)
        self.click_login()
        from pages.home_page import HomePage
        return HomePage(self.driver)

    @allure.step("跳转到注册页面")
    def go_to_register(self):
        """跳转到注册页面"""
        self.click(self.LINK_REGISTER)
        from pages.register_page import RegisterPage
        return RegisterPage(self.driver)

    @allure.step("跳转到忘记密码页面")
    def go_to_forget_password(self):
        """跳转到忘记密码页面"""
        self.click(self.LINK_FORGET_PWD)
        return self

    # ---------- 页面信息获取 ----------

    def get_error_message(self):
        """获取登录错误提示信息"""
        if self.is_element_exist(self.MSG_ERROR, timeout=5):
            return self.get_text(self.MSG_ERROR)
        return ""

    def get_success_message(self):
        """获取成功提示信息"""
        if self.is_element_exist(self.MSG_SUCCESS, timeout=5):
            return self.get_text(self.MSG_SUCCESS)
        return ""

    def is_login_page_displayed(self):
        """判断登录页面是否已显示"""
        return self.is_displayed(self.BTN_LOGIN)

    def is_username_empty(self):
        """判断用户名输入框是否为空"""
        return self.get_value(self.INPUT_USERNAME) == ""

    def clear_login_form(self):
        """清空登录表单"""
        self.input_text(self.INPUT_USERNAME, "")
        self.input_text(self.INPUT_PASSWORD, "")
        return self
