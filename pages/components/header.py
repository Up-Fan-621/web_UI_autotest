# ============================
# Header - 顶部导航栏组件
# ============================

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import logger


class Header(BasePage):
    """
    顶部导航栏（可复用组件）
    几乎每个页面都有，独立封装方便多处引用

    元素：Logo、导航菜单、搜索框、用户头像、通知铃铛
    """

    # ---------- 元素定位 ----------
    LOGO             = (By.CSS_SELECTOR, ".header-logo")
    NAV_ITEMS        = (By.CSS_SELECTOR, ".header-nav li a")
    INPUT_GLOBAL_SEARCH = (By.CSS_SELECTOR, ".header-search input")
    BTN_GLOBAL_SEARCH = (By.CSS_SELECTOR, ".header-search button")
    ICON_USER_MENU   = (By.CSS_SELECTOR, ".header-user-menu")
    ICON_NOTIFICATION = (By.CSS_SELECTOR, ".header-notification")
    BTN_SETTING      = (By.CSS_SELECTOR, ".header-setting")

    # ---------- 组件操作 ----------

    def click_logo(self):
        """点击 Logo 回首页"""
        self.click(self.LOGO)
        from pages.home_page import HomePage
        return HomePage(self.driver)

    def navigate_to(self, menu_text):
        """
        通过导航菜单导航到指定页面

        Args:
            menu_text: 菜单文本（如"产品中心"、"我的订单"）

        Returns:
            BasePage: 目标页面对象
        """
        for item in self.find_elements(self.NAV_ITEMS):
            if item.text.strip() == menu_text:
                item.click()
                logger.info(f"导航到: {menu_text}")
                break
        return self

    def global_search(self, keyword):
        """使用顶部搜索框搜索"""
        self.input_text(self.INPUT_GLOBAL_SEARCH, keyword)
        self.click(self.BTN_GLOBAL_SEARCH)
        from pages.search_page import SearchPage
        return SearchPage(self.driver)

    def is_header_displayed(self):
        """判断 header 是否显示"""
        return self.is_displayed(self.LOGO)
