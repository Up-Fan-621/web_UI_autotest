# ============================
# SearchPage - 搜索结果页面对象
# ============================

import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import logger


class SearchPage(BasePage):
    """
    搜索结果页 PO

    页面元素：搜索结果列表、筛选条件、排序方式、分页、空结果提示
    页面操作：筛选、排序、翻页、查看详情
    """

    # ---------- 元素定位 ----------
    # 搜索框
    INPUT_SEARCH     = (By.ID, "search-input")
    BTN_SEARCH       = (By.ID, "search-btn")

    # 结果区
    DIV_RESULTS      = (By.CSS_SELECTOR, ".search-result-item")
    LBL_RESULT_COUNT = (By.CSS_SELECTOR, ".result-count")
    LBL_NO_RESULT    = (By.CSS_SELECTOR, ".no-result")
    LINK_RESULT_FIRST = (By.CSS_SELECTOR, ".search-result-item:first-child a")

    # 筛选区
    FILTER_PRICE     = (By.CSS_SELECTOR, ".filter-price")
    FILTER_CATEGORY  = (By.CSS_SELECTOR, ".filter-category")
    BTN_FILTER_SUBMIT = (By.CSS_SELECTOR, ".filter-submit-btn")
    BTN_FILTER_RESET  = (By.CSS_SELECTOR, ".filter-reset-btn")

    # 排序区
    SELECT_SORT      = (By.ID, "sort-select")

    # 分页区
    BTN_NEXT_PAGE    = (By.CSS_SELECTOR, ".pagination .next")
    BTN_PREV_PAGE    = (By.CSS_SELECTOR, ".pagination .prev")
    LBL_CURRENT_PAGE = (By.CSS_SELECTOR, ".pagination .active")

    # ---------- 页面操作 ----------

    @allure.step("搜索: {keyword}")
    def search(self, keyword):
        """重新搜索"""
        self.input_text(self.INPUT_SEARCH, keyword)
        self.click(self.BTN_SEARCH)
        return self

    @allure.step("按价格区间筛选: {min_price} - {max_price}")
    def filter_by_price(self, min_price=None, max_price=None):
        """按价格筛选"""
        self.click(self.FILTER_PRICE)
        if min_price:
            self.input_text((By.ID, "price-min"), str(min_price))
        if max_price:
            self.input_text((By.ID, "price-max"), str(max_price))
        self.click(self.BTN_FILTER_SUBMIT)
        return self

    @allure.step("选择排序方式: {sort_type}")
    def sort_by(self, sort_type):
        """
        选择排序方式

        Args:
            sort_type: 排序类型（"price_asc" / "price_desc" / "sales" / "newest"）
        """
        sort_map = {
            "price_asc": "price_asc",
            "price_desc": "price_desc",
            "sales": "sales",
            "newest": "newest"
        }
        self.select_by_value(self.SELECT_SORT, sort_map.get(sort_type, sort_type))
        return self

    def click_first_result(self):
        """点击第一条搜索结果"""
        self.click(self.LINK_RESULT_FIRST)
        return self

    def go_to_next_page(self):
        """翻到下一页"""
        if self.is_enabled(self.BTN_NEXT_PAGE):
            self.click(self.BTN_NEXT_PAGE)
        return self

    def go_to_prev_page(self):
        """翻到上一页"""
        if self.is_enabled(self.BTN_PREV_PAGE):
            self.click(self.BTN_PREV_PAGE)
        return self

    # ---------- 页面信息获取 ----------

    def get_result_count(self):
        """获取搜索结果数量"""
        try:
            text = self.get_text(self.LBL_RESULT_COUNT)
            # 提取数字，如 "共 25 条结果" → 25
            import re
            numbers = re.findall(r'\d+', text)
            return int(numbers[0]) if numbers else 0
        except Exception:
            return 0

    def get_result_items(self):
        """获取所有搜索结果的文本列表"""
        return [item.text for item in self.find_elements(self.DIV_RESULTS)]

    def has_results(self):
        """是否有搜索结果"""
        return self.get_result_count() > 0 and not self.is_displayed(self.LBL_NO_RESULT)

    def is_no_result(self):
        """是否显示"无结果""""
        return self.is_element_exist(self.LBL_NO_RESULT, timeout=3)

    def get_current_page_number(self):
        """获取当前页码"""
        try:
            return int(self.get_text(self.LBL_CURRENT_PAGE))
        except Exception:
            return 1
