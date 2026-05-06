# ============================
# 冒烟测试用例
# ============================
# 冒烟测试：验证核心流程是否基本可用
# 执行命令: pytest tests/test_smoke/ -m smoke

import pytest
import allure

from pages.login_page import LoginPage
from pages.home_page import HomePage


@allure.feature("冒烟测试")
class TestSmoke:
    """
    冒烟测试集合

    执行频率：每次部署后必跑
    目标：5分钟内完成，快速验证核心功能
    """

    @allure.title("冒烟-系统可访问")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_system_accessible(self, driver, base_url):
        """验证：系统首页可正常访问"""
        driver.get(base_url)
        assert base_url in driver.current_url, f"未能访问 {base_url}"
        allure.attach(
            f"访问 URL: {driver.current_url}\nTitle: {driver.title}",
            name="访问信息",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.title("冒烟-登录页可访问")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_login_page_accessible(self, driver, base_url):
        """验证：登录页可正常访问"""
        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        assert login_page.is_login_page_displayed(), "登录页应正常显示"

    @allure.title("冒烟-核心登录流程")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_core_login_flow(self, driver, base_url, login_data):
        """验证：核心登录流程（管理员账号）"""
        user = login_data["valid_users"][0]

        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        home_page = login_page.login(user["username"], user["password"])

        assert home_page.is_logged_in(), "核心登录流程应成功"

    @allure.title("冒烟-首页关键元素显示")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_homepage_elements(self, driver, base_url, login_data):
        """验证：首页关键元素正常显示"""
        user = login_data["valid_users"][0]

        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        home_page = login_page.login(user["username"], user["password"])
        home_page.verify_page_loaded()

        # 验证搜索框、导航菜单等关键元素
        assert home_page.is_displayed(home_page.INPUT_SEARCH), "搜索框应显示"
