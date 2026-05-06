# ============================
# RegisterPage - 注册页面对象
# ============================

import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import logger


class RegisterPage(BasePage):
    """
    注册页面 PO

    页面元素：用户名、手机号、密码、确认密码、验证码、注册按钮
    页面操作：注册、发送验证码、跳转登录
    """

    # ---------- 元素定位 ----------
    INPUT_USERNAME    = (By.ID, "reg-username")
    INPUT_PHONE       = (By.ID, "reg-phone")
    INPUT_PASSWORD    = (By.ID, "reg-password")
    INPUT_CONFIRM_PWD = (By.ID, "reg-confirm-password")
    INPUT_SMS_CODE    = (By.ID, "sms-code")
    BTN_SEND_CODE     = (By.ID, "send-sms-code")
    BTN_REGISTER      = (By.ID, "btn-register")
    LINK_TO_LOGIN     = (By.LINK_TEXT, "立即登录")
    MSG_ERROR         = (By.CSS_SELECTOR, ".error-msg")
    CHECKBOX_AGREE    = (By.ID, "agree-terms")

    # ---------- 页面操作 ----------

    @allure.step("填写注册信息并注册")
    def register(self, username, phone, password, confirm_pwd=None, sms_code="888888"):
        """
        完整注册流程

        Args:
            username: 用户名
            phone: 手机号
            password: 密码
            confirm_pwd: 确认密码（默认与密码相同）
            sms_code: 短信验证码（测试环境默认值）
        """
        confirm_pwd = confirm_pwd or password

        self.input_text(self.INPUT_USERNAME, username)
        self.input_text(self.INPUT_PHONE, phone)
        self.input_text(self.INPUT_PASSWORD, password)
        self.input_text(self.INPUT_CONFIRM_PWD, confirm_pwd)

        # 勾选同意协议
        if not self.is_selected(self.CHECKBOX_AGREE):
            self.click(self.CHECKBOX_AGREE)

        # 输入验证码
        self.input_text(self.INPUT_SMS_CODE, sms_code)

        self.click(self.BTN_REGISTER)
        return self

    @allure.step("发送短信验证码")
    def send_sms_code(self):
        """发送短信验证码"""
        self.click(self.BTN_SEND_CODE)
        return self

    @allure.step("跳转到登录页面")
    def go_to_login(self):
        """跳转到登录页面"""
        self.click(self.LINK_TO_LOGIN)
        from pages.login_page import LoginPage
        return LoginPage(self.driver)

    def get_error_message(self):
        """获取注册错误信息"""
        if self.is_element_exist(self.MSG_ERROR, timeout=5):
            return self.get_text(self.MSG_ERROR)
        return ""
