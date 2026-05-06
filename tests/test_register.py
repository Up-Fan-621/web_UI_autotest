# ============================
# 注册测试用例
# ============================

import pytest
import allure
import time

from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from utils.logger import logger


@allure.feature("用户注册")
@allure.story("注册功能")
class TestRegister:
    """
    注册模块测试用例

    覆盖范围：
        - 正常注册
        - 异常注册（用户名已存在、手机号已注册等）
        - 表单校验
    """

    @pytest.fixture(autouse=True)
    def _navigate_to_register(self, driver, base_url):
        """进入注册页面"""
        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        register_page = login_page.go_to_register()
        self.register_page = register_page
        return register_page

    @allure.title("注册页面正确显示")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_register_page_displayed(self):
        """测试：注册页面元素正确显示"""
        rp = self.register_page
        assert rp.is_displayed(rp.BTN_REGISTER), "注册按钮应显示"
        assert rp.is_displayed(rp.LINK_TO_LOGIN), "登录链接应显示"

    @allure.title("跳转到登录页面")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_navigate_to_login(self):
        """测试：从注册页跳转到登录页"""
        login_page = self.register_page.go_to_login()
        assert login_page.is_login_page_displayed()

    @allure.title("注册-用户名已存在")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.login
    def test_register_duplicate_username(self, register_data):
        """测试：已存在的用户名提示错误"""
        case = register_data["invalid_register_cases"][0]

        self.register_page.register(
            username=case["username"],
            phone=case["phone"],
            password=case["password"],
            confirm_pwd=case["password"],
            sms_code=register_data["valid_register"]["sms_code"]
        )

        error_msg = self.register_page.get_error_message()
        assert case["expected_msg"] in error_msg, \
            f"期望包含 '{case['expected_msg']}'，实际: '{error_msg}'"

    @allure.title("注册-密码太短")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p2
    def test_register_short_password(self, register_data):
        """测试：密码太短提示错误"""
        case = register_data["invalid_register_cases"][2]

        self.register_page.register(
            username=case["username"],
            phone=case["phone"],
            password=case["password"],
            confirm_pwd=case["password"],
            sms_code=register_data["valid_register"]["sms_code"]
        )

        error_msg = self.register_page.get_error_message()
        assert case["expected_msg"] in error_msg

    @allure.title("注册-两次密码不一致")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_register_password_mismatch(self, register_data):
        """测试：两次密码不一致提示错误"""
        case = register_data["invalid_register_cases"][3]

        self.register_page.register(
            username=case["username"],
            phone=case["phone"],
            password=case["password"],
            confirm_pwd=case["confirm_password"],
            sms_code=register_data["valid_register"]["sms_code"]
        )

        error_msg = self.register_page.get_error_message()
        assert case["expected_msg"] in error_msg

    @allure.title("注册-手机号格式错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p2
    def test_register_invalid_phone(self, register_data):
        """测试：手机号格式错误"""
        case = register_data["invalid_register_cases"][4]

        self.register_page.register(
            username=case["username"],
            phone=case["phone"],
            password=case["password"],
            confirm_pwd=case["password"],
            sms_code=register_data["valid_register"]["sms_code"]
        )

        error_msg = self.register_page.get_error_message()
        assert case["expected_msg"] in error_msg
