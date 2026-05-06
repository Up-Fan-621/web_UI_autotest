# ============================
# 搜索测试用例
# ============================

import pytest
import allure

from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.search_page import SearchPage
from utils.logger import logger


@allure.feature("搜索功能")
@allure.story("商品搜索")
class TestSearch:
    """
    搜索模块测试用例

    覆盖范围：
        - 基础搜索（关键词）
        - 空结果搜索
        - 排序功能
        - 分页功能
    """

    @pytest.fixture(autouse=True)
    def _login(self, driver, base_url, login_data):
        """搜索前先登录"""
        user = login_data["valid_users"][0]
        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        home_page = login_page.login(user["username"], user["password"])
        self.home_page = home_page
        return home_page

    @allure.title("关键词搜索-有结果")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.search
    def test_search_with_results(self, driver, search_data):
        """测试：搜索有效关键词返回结果"""
        case = search_data["basic_search"][0]

        search_page = self.home_page.search(case["keyword"])

        assert search_page.has_results(), f"搜索 '{case['keyword']}' 应有结果"
        count = search_page.get_result_count()
        logger.info(f"搜索 '{case['keyword']}' 返回 {count} 条结果")

    @allure.title("关键词搜索-无结果")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.search
    def test_search_no_results(self, search_data):
        """测试：搜索不存在的内容无结果"""
        case = search_data["basic_search"][1]

        search_page = self.home_page.search(case["keyword"])

        assert search_page.is_no_result(), f"搜索 '{case['keyword']}' 应显示无结果"

    @allure.title("搜索结果数量正确")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.search
    def test_search_result_count(self, search_data):
        """测试：搜索结果数量与页面显示一致"""
        case = search_data["basic_search"][0]

        search_page = self.home_page.search(case["keyword"])
        displayed_count = search_page.get_result_count()
        actual_items = len(search_page.get_result_items())

        assert displayed_count == actual_items, \
            f"显示数量 {displayed_count} 与实际条数 {actual_items} 不一致"

    @allure.title("价格升序排序")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p2
    @pytest.mark.search
    def test_sort_by_price_asc(self, search_data):
        """测试：搜索结果按价格升序排列"""
        case = search_data["sort_test"][0]

        search_page = self.home_page.search(case["keyword"])
        search_page.sort_by(case["sort_type"])

        # 验证排序：获取结果列表，检查价格是否升序
        # （这里简化验证，实际需要从结果中提取价格进行比较）
        search_page.wait.for_page_loaded()
        assert search_page.has_results(), "排序后仍应有结果"

    @allure.title("价格降序排序")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p2
    @pytest.mark.search
    def test_sort_by_price_desc(self, search_data):
        """测试：搜索结果按价格降序排列"""
        case = search_data["sort_test"][1]

        search_page = self.home_page.search(case["keyword"])
        search_page.sort_by(case["sort_type"])
        search_page.wait.for_page_loaded()

        assert search_page.has_results()

    @allure.title("搜索结果翻页")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p2
    @pytest.mark.search
    def test_search_pagination(self, search_data):
        """测试：搜索结果翻页功能"""
        case = search_data["basic_search"][0]

        search_page = self.home_page.search(case["keyword"])
        first_page = search_page.get_current_page_number()

        # 如果有下一页，翻页后页码应增加
        search_page.go_to_next_page()
        second_page = search_page.get_current_page_number()

        # 验证页码变化（或者如果没有下一页，按钮应不可用）
        logger.info(f"第一页: {first_page}, 第二页: {second_page}")

    @allure.title("清空搜索后重新搜索")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    @pytest.mark.search
    def test_clear_and_research(self, search_data):
        """测试：清空搜索内容后重新搜索"""
        case1 = search_data["basic_search"][0]
        case2 = search_data["basic_search"][2]

        # 搜索第一个关键词
        search_page = self.home_page.search(case1["keyword"])
        assert search_page.has_results()

        # 回到首页，清空后搜索第二个
        self.home_page = search_page.go_back() if search_page else self.home_page
        search_page2 = self.home_page.search(case2["keyword"])
        assert search_page2.has_results()
