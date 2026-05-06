# ============================
# OrderPage - 订单页面对象
# ============================

import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import logger


class OrderPage(BasePage):
    """
    订单页面 PO

    页面元素：订单列表、订单详情、筛选标签、操作按钮
    页面操作：查看订单、取消订单、筛选订单、分页
    """

    # ---------- 元素定位 ----------
    # 订单标签
    TAB_ALL       = (By.CSS_SELECTOR, "[data-tab='all']")
    TAB_PENDING   = (By.CSS_SELECTOR, "[data-tab='pending']")
    TAB_PAID      = (By.CSS_SELECTOR, "[data-tab='paid']")
    TAB_SHIPPED   = (By.CSS_SELECTOR, "[data-tab='shipped']")
    TAB_COMPLETED = (By.CSS_SELECTOR, "[data-tab='completed']")
    TAB_CANCELLED = (By.CSS_SELECTOR, "[data-tab='cancelled']")

    # 订单列表
    DIV_ORDER_ITEMS    = (By.CSS_SELECTOR, ".order-item")
    LBL_ORDER_COUNT    = (By.CSS_SELECTOR, ".order-count")
    LBL_NO_ORDER       = (By.CSS_SELECTOR, ".no-order")
    BTN_FIRST_ORDER    = (By.CSS_SELECTOR, ".order-item:first-child")

    # 订单操作
    BTN_ORDER_DETAIL   = (By.CSS_SELECTOR, ".order-item .btn-detail")
    BTN_CANCEL_ORDER   = (By.CSS_SELECTOR, ".order-item .btn-cancel")
    BTN_PAY_ORDER      = (By.CSS_SELECTOR, ".order-item .btn-pay")
    BTN_CONFIRM_RECEIVE = (By.CSS_SELECTOR, ".order-item .btn-confirm")

    # 订单详情弹窗
    MODAL_ORDER_DETAIL = (By.CSS_SELECTOR, ".order-detail-modal")
    LBL_ORDER_ID       = (By.CSS_SELECTOR, ".order-detail-modal .order-id")
    LBL_ORDER_AMOUNT   = (By.CSS_SELECTOR, ".order-detail-modal .order-amount")
    LBL_ORDER_STATUS   = (By.CSS_SELECTOR, ".order-detail-modal .order-status")
    BTN_CLOSE_MODAL    = (By.CSS_SELECTOR, ".order-detail-modal .close-btn")

    # 分页
    BTN_NEXT_PAGE      = (By.CSS_SELECTOR, ".order-pagination .next")

    # ---------- 页面操作 ----------

    @allure.step("切换订单标签: {tab_name}")
    def switch_tab(self, tab_name):
        """
        切换订单标签页

        Args:
            tab_name: 标签名 (all/pending/paid/shipped/completed/cancelled)
        """
        tab_map = {
            "all": self.TAB_ALL,
            "pending": self.TAB_PENDING,
            "paid": self.TAB_PAID,
            "shipped": self.TAB_SHIPPED,
            "completed": self.TAB_COMPLETED,
            "cancelled": self.TAB_CANCELLED
        }
        locator = tab_map.get(tab_name)
        if locator:
            self.click(locator)
            self.wait.for_ajax_complete()
        return self

    @allure.step("查看第一个订单详情")
    def view_first_order_detail(self):
        """查看第一个订单的详情"""
        self.click(self.BTN_ORDER_DETAIL)
        self.wait.for_element_invisible((By.CSS_SELECTOR, ".modal-loading"), timeout=5)
        return self

    @allure.step("取消第一个订单")
    def cancel_first_order(self):
        """取消第一个订单"""
        self.click(self.BTN_CANCEL_ORDER)
        self.accept_alert()
        return self

    @allure.step("支付第一个订单")
    def pay_first_order(self):
        """支付第一个待付款订单"""
        self.click(self.BTN_PAY_ORDER)
        return self

    @allure.step("确认收货")
    def confirm_receive(self):
        """确认收货"""
        self.click(self.BTN_CONFIRM_RECEIVE)
        self.accept_alert()
        return self

    def close_order_detail(self):
        """关闭订单详情弹窗"""
        if self.is_displayed(self.MODAL_ORDER_DETAIL):
            self.click(self.BTN_CLOSE_MODAL)
        return self

    def go_to_next_page(self):
        """翻到下一页"""
        if self.is_enabled(self.BTN_NEXT_PAGE):
            self.click(self.BTN_NEXT_PAGE)
        return self

    # ---------- 页面信息获取 ----------

    def get_order_count(self):
        """获取当前标签页的订单数量"""
        try:
            text = self.get_text(self.LBL_ORDER_COUNT)
            import re
            numbers = re.findall(r'\d+', text)
            return int(numbers[0]) if numbers else 0
        except Exception:
            return 0

    def get_order_ids(self):
        """获取当前页所有订单 ID"""
        ids = []
        for item in self.find_elements(self.DIV_ORDER_ITEMS):
            try:
                order_id = item.get_attribute("data-order-id")
                ids.append(order_id)
            except Exception:
                pass
        return ids

    def get_order_status_text(self):
        """获取订单详情中的状态文本"""
        if self.is_element_exist(self.LBL_ORDER_STATUS, timeout=3):
            return self.get_text(self.LBL_ORDER_STATUS)
        return ""

    def get_order_detail_info(self):
        """获取订单详情信息（字典）"""
        if not self.is_element_exist(self.MODAL_ORDER_DETAIL, timeout=3):
            return {}
        return {
            "order_id": self.get_text(self.LBL_ORDER_ID),
            "amount": self.get_text(self.LBL_ORDER_AMOUNT),
            "status": self.get_text(self.LBL_ORDER_STATUS)
        }

    def has_orders(self):
        """是否有订单"""
        return self.get_order_count() > 0 and not self.is_element_exist(self.LBL_NO_ORDER, timeout=3)

    def is_no_order(self):
        """是否显示"暂无订单""""
        return self.is_element_exist(self.LBL_NO_ORDER, timeout=3)
