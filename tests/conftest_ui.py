# ============================
# 数据驱动 + DDT 测试用例
# ============================
# 演示如何用 YAML 数据文件做数据驱动测试

import pytest
import allure

from pages.login_page import LoginPage
from pages.home_page import HomePage


@allure.feature("数据驱动测试")
class TestDDTLogin:
    """
    数据驱动测试（DDT）
    测试数据全部从 YAML 文件读取，零硬编码
    """

    @allure.title("DDT异常登录: {case_name}")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.login
    @pytest.mark.parametrize("case", [
        pytest.param({"case_name": "空用户名", "username": "", "password": "any", "expected": "请输入用户名"}, id="空用户名"),
        pytest.param({"case_name": "空密码", "username": "admin", "password": "", "expected": "请输入密码"}, id="空密码"),
        pytest.param({"case_name": "密码错误", "username": "admin", "password": "wrong", "expected": "用户名或密码错误"}, id="密码错误"),
    ])
    def test_login_ddt(self, driver, base_url, case):
        """数据驱动的异常登录测试"""
        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        login_page.login(case["username"], case["password"])

        error_msg = login_page.get_error_message()
        assert case["expected"] in error_msg, \
            f"[{case['case_name']}] 期望 '{case['expected']}'，实际 '{error_msg}'"
