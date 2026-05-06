# ============================
# 登录测试用例
# ============================

import pytest
import allure

from pages.login_page import LoginPage
from pages.home_page import HomePage
from utils.screenshot_listener import StepLogger


@allure.feature("用户登录")
@allure.story("登录功能")
class TestLogin:
    """
    登录模块测试用例

    覆盖范围：
        - 正常登录（有效账号）
        - 异常登录（空用户名、空密码、错误凭证等）
        - 登录后跳转验证
        - 记住密码功能
        - 登出功能
    """

    # ===========================
    # 正向测试
    # ===========================

    @allure.title("有效账号登录成功")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("使用有效的管理员账号登录，验证跳转到首页且显示用户信息")
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.login
    def test_login_success_with_admin(self, driver, base_url, login_data):
        """测试：管理员账号登录成功"""
        # 准备测试数据
        user = login_data["valid_users"][0]

        # 执行登录
        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        home_page = login_page.login(user["username"], user["password"])

        # 验证：跳转到首页 + 已登录状态
        home_page.verify_page_loaded()
        assert home_page.is_logged_in(), "登录后应显示用户头像"

        # 验证：欢迎语包含昵称
        welcome_text = home_page.get_welcome_text()
        assert user["nickname"] in welcome_text, f"欢迎语应包含昵称 '{user['nickname']}'，实际: '{welcome_text}'"

    @allure.title("普通用户登录成功")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.login
    def test_login_success_with_normal_user(self, driver, base_url, login_data):
        """测试：普通用户登录成功"""
        user = login_data["valid_users"][1]

        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        home_page = login_page.login(user["username"], user["password"])

        assert home_page.is_logged_in(), "普通用户登录后应显示用户头像"

    @allure.title("登录后URL跳转正确")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.login
    def test_login_redirect_to_home(self, driver, base_url, login_data):
        """测试：登录后正确跳转到首页"""
        user = login_data["valid_users"][0]

        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        home_page = login_page.login(user["username"], user["password"])

        # 验证 URL 包含 /home 或首页标识
        current_url = driver.current_url
        assert "login" not in current_url.lower(), f"登录后不应停留在登录页: {current_url}"

    @allure.title("记住密码登录成功")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    @pytest.mark.login
    def test_login_with_remember_me(self, driver, base_url, login_data):
        """测试：勾选记住密码后登录成功"""
        user = login_data["remember_me_test"]

        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        home_page = login_page.login_with_remember(user["username"], user["password"])

        assert home_page.is_logged_in(), "记住密码登录后应成功"

    # ===========================
    # 异常测试
    # ===========================

    @allure.title("空用户名登录失败")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.login
    def test_login_empty_username(self, driver, base_url, login_data):
        """测试：空用户名提示错误"""
        case = login_data["invalid_cases"][0]

        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        login_page.login(case["username"], case["password"])

        error_msg = login_page.get_error_message()
        assert error_msg == case["expected_msg"], \
            f"错误提示不匹配，期望: '{case['expected_msg']}'，实际: '{error_msg}'"

    @allure.title("空密码登录失败")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.login
    def test_login_empty_password(self, driver, base_url, login_data):
        """测试：空密码提示错误"""
        case = login_data["invalid_cases"][1]

        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        login_page.login(case["username"], case["password"])

        error_msg = login_page.get_error_message()
        assert error_msg == case["expected_msg"]

    @allure.title("错误密码登录失败")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.login
    def test_login_wrong_password(self, driver, base_url, login_data):
        """测试：密码错误提示正确"""
        case = login_data["invalid_cases"][3]

        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        login_page.login(case["username"], case["password"])

        error_msg = login_page.get_error_message()
        assert case["expected_msg"] in error_msg

    @allure.title("不存在的用户登录失败")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.login
    def test_login_not_exist_user(self, driver, base_url, login_data):
        """测试：不存在的用户名提示错误"""
        case = login_data["invalid_cases"][2]

        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        login_page.login(case["username"], case["password"])

        error_msg = login_page.get_error_message()
        assert error_msg == case["expected_msg"]

    @allure.title("SQL注入防护")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.login
    def test_login_sql_injection(self, driver, base_url, login_data):
        """测试：SQL 注入攻击被拦截"""
        case = login_data["invalid_cases"][5]

        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        login_page.login(case["username"], case["password"])

        error_msg = login_page.get_error_message()
        assert "错误" in error_msg or "非法" in error_msg, \
            f"SQL注入应被拦截，实际提示: '{error_msg}'"

    @allure.title("XSS注入防护")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p2
    @pytest.mark.login
    def test_login_xss_injection(self, driver, base_url, login_data):
        """测试：XSS 攻击被拦截"""
        case = login_data["invalid_cases"][6]

        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        login_page.login(case["username"], case["password"])

        error_msg = login_page.get_error_message()
        assert case["expected_msg"] in error_msg, \
            f"XSS输入应被拦截，实际提示: '{error_msg}'"

    # ===========================
    # 参数化异常测试（合并写法）
    # ===========================

    @allure.title("异常登录: {case_name}")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.login
    @pytest.mark.parametrize("case_name, username, password, expected_msg", [
        ("空用户名", "", "any_password", "请输入用户名"),
        ("空密码", "admin", "", "请输入密码"),
        ("密码错误", "admin", "wrong", "用户名或密码错误"),
        ("用户不存在", "ghost_user", "any", "用户名或密码错误"),
    ], ids=["空用户名", "空密码", "密码错误", "用户不存在"])
    def test_login_invalid_parametrized(self, driver, base_url, case_name, username, password, expected_msg):
        """参数化异常登录测试"""
        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        login_page.login(username, password)

        error_msg = login_page.get_error_message()
        assert expected_msg in error_msg, \
            f"[{case_name}] 期望包含 '{expected_msg}'，实际: '{error_msg}'"

    # ===========================
    # 登出测试
    # ===========================

    @allure.title("登录后退出成功")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.login
    def test_logout(self, driver, base_url, login_data):
        """测试：登录后退出，回到登录页"""
        user = login_data["valid_users"][0]

        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        home_page = login_page.login(user["username"], user["password"])
        assert home_page.is_logged_in()

        # 退出
        new_login_page = home_page.logout()
        assert new_login_page.is_login_page_displayed(), "退出后应回到登录页"
