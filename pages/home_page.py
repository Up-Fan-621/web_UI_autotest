# ============================
# HomePage - 首页页面对象
# ============================

import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import logger


class HomePage(BasePage):
    """
    首页 PO

    页面元素：搜索框、导航栏、用户菜单、公告/通知、欢迎语
    页面操作：搜索、进入个人中心、退出登录
    """

    # ---------- URL ----------
    URL_PATH = "/home"  # 或 "/" 视实际项目而定

    # ---------- 元素定位 ----------
    # 搜索区
    INPUT_SEARCH    = (By.ID, "search-input")
    BTN_SEARCH      = (By.ID, "search-btn")
    LINK_ADV_SEARCH = (By.LINK_TEXT, "高级搜索")
    DIV_SUGGESTIONS = (By.CSS_SELECTOR, ".search-suggestions")

    # 导航区
    NAV_MENU_ITEMS  = (By.CSS_SELECTOR, ".nav-menu li a")
    LINK_PRODUCTS   = (By.LINK_TEXT, "产品中心")
    LINK_ORDERS     = (By.LINK_TEXT, "我的订单")

    # 用户区
    ICON_USER_AVATAR = (By.CSS_SELECTOR, ".user-avatar")
    LBL_WELCOME     = (By.CSS_SELECTOR, ".welcome-text")
    BTN_LOGOUT      = (By.CSS_SELECTOR, ".btn-logout")
    LINK_PROFILE    = (By.LINK_TEXT, "个人中心")
    LINK_SETTINGS   = (By.LINK_TEXT, "系统设置")

    # 通知区
    ICON_NOTIFICATION = (By.CSS_SELECTOR, ".notification-icon")
    BADGE_COUNT      = (By.CSS_SELECTOR, ".notification-badge")
    DIV_NOTIFICATIONS = (By.CSS_SELECTOR, ".notification-panel")

    # 公告区
    DIV_ANNOUNCEMENT = (By.CSS_SELECTOR, ".announcement-bar")
    BTN_CLOSE_ANNOUNCEMENT = (By.CSS_SELECTOR, ".announcement-bar .close-btn")

    # ---------- 页面操作 ----------

    @allure.step("搜索关键词: {keyword}")
    def search(self, keyword):
        """
        执行搜索

        Args:
            keyword: 搜索关键词

        Returns:
            SearchPage: 搜索结果页
        """
        self.input_text(self.INPUT_SEARCH, keyword)
        self.click(self.BTN_SEARCH)
        from pages.search_page import SearchPage
        return SearchPage(self.driver)

    @allure.step("清除搜索内容")
    def clear_search(self):
        """清空搜索框"""
        self.input_text(self.INPUT_SEARCH, "", clear_first=True)
        return self

    def go_to_products(self):
        """进入产品中心"""
        self.click(self.LINK_PRODUCTS)
        return self

    def go_to_orders(self):
        """进入我的订单"""
        self.click(self.LINK_ORDERS)
        from pages.order_page import OrderPage
        return OrderPage(self.driver)

    @allure.step("进入个人中心")
    def go_to_profile(self):
        """进入个人中心"""
        self.click(self.ICON_USER_AVATAR)
        self.click(self.LINK_PROFILE)
        return self

    @allure.step("退出登录")
    def logout(self):
        """退出登录"""
        self.click(self.ICON_USER_AVATAR)
        self.click(self.BTN_LOGOUT)
        from pages.login_page import LoginPage
        return LoginPage(self.driver)

    def close_announcement(self):
        """关闭公告栏"""
        if self.is_displayed(self.DIV_ANNOUNCEMENT):
            self.click(self.BTN_CLOSE_ANNOUNCEMENT)
        return self

    def open_notifications(self):
        """打开通知面板"""
        self.click(self.ICON_NOTIFICATION)
        return self

    # ---------- 页面信息获取 ----------

    def get_welcome_text(self):
        """获取欢迎语"""
        return self.get_text(self.LBL_WELCOME)

    def is_logged_in(self):
        """判断是否已登录（通过用户头像是否存在）"""
        return self.is_element_exist(self.ICON_USER_AVATAR, timeout=5)

    def get_notification_count(self):
        """获取通知数量"""
        if self.is_element_exist(self.BADGE_COUNT, timeout=3):
            return int(self.get_text(self.BADGE_COUNT))
        return 0

    def get_announcement_text(self):
        """获取公告文本"""
        if self.is_element_exist(self.DIV_ANNOUNCEMENT, timeout=3):
            return self.get_text(self.DIV_ANNOUNCEMENT)
        return ""

    def get_nav_menu_items(self):
        """获取所有导航菜单项文本"""
        return [item.text for item in self.find_elements(self.NAV_MENU_ITEMS)]

    # ---------- 页面验证 ----------

    def verify_page_loaded(self):
        """验证首页是否加载完成"""
        self.wait.for_page_loaded()
        assert self.is_displayed(self.INPUT_SEARCH) or self.is_displayed(self.ICON_USER_AVATAR), \
            "首页关键元素未加载完成"
        return self
