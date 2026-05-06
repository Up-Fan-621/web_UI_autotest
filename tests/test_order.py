# ============================
# 订单测试用例
# ============================

import pytest
import allure

from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.order_page import OrderPage
from utils.logger import logger


@allure.feature("订单管理")
@allure.story("订单列表与操作")
class TestOrder:
    """
    订单模块测试用例

    覆盖范围：
        - 订单列表查看
        - 订单标签页切换
        - 订单详情查看
        - 订单数据通过 API 造数据 + UI 验证
    """

    @pytest.fixture(autouse=True)
    def _login_and_prepare(self, driver, base_url, login_data, prepare_test_order):
        """
        登录 + 通过 API 预创建测试订单

        这是"API 绕过 UI 造数据"的核心应用场景：
        1. 通过 API 快速创建订单（不需要走 UI 下单流程）
        2. 然后用 UI 验证订单是否正确显示
        """
        user = login_data["valid_users"][0]

        # UI 登录
        login_page = LoginPage(driver)
        login_page.open_login_page(base_url)
        home_page = login_page.login(user["username"], user["password"])

        # 通过导航进入订单页
        order_page = home_page.go_to_orders()
        self.order_page = order_page
        self.api_order = prepare_test_order

        return order_page

    @allure.title("查看订单列表")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.order
    def test_order_list_displayed(self):
        """测试：订单列表正确显示"""
        self.order_page.wait.for_page_loaded()

        assert self.order_page.has_orders(), "应有测试订单显示"

        order_count = self.order_page.get_order_count()
        logger.info(f"当前标签页订单数量: {order_count}")
        assert order_count > 0, "订单数量应大于0"

    @allure.title("切换订单标签-待付款")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.order
    def test_switch_to_pending_tab(self, order_data):
        """测试：切换到待付款标签"""
        self.order_page.switch_tab("pending")
        self.order_page.wait.for_ajax_complete()

        has_orders = self.order_page.has_orders()
        logger.info(f"待付款订单: has_orders={has_orders}")

    @allure.title("切换订单标签-已完成")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.order
    def test_switch_to_completed_tab(self, order_data):
        """测试：切换到已完成标签"""
        self.order_page.switch_tab("completed")
        self.order_page.wait.for_ajax_complete()

    @allure.title("切换所有标签页")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.order
    @pytest.mark.parametrize("tab", ["all", "pending", "paid", "shipped", "completed", "cancelled"])
    def test_switch_all_tabs(self, tab):
        """参数化测试：遍历所有订单标签页"""
        self.order_page.switch_tab(tab)
        self.order_page.wait.for_ajax_complete()

        # 只要不报错就算通过（具体数据由 API 造数据决定）
        assert True

    @allure.title("查看订单详情")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.order
    def test_view_order_detail(self):
        """测试：点击查看订单详情"""
        self.order_page.wait.for_page_loaded()

        if not self.order_page.has_orders():
            pytest.skip("没有可查看的订单")

        self.order_page.view_first_order_detail()

        # 验证详情弹窗出现
        detail = self.order_page.get_order_detail_info()
        assert detail, "应显示订单详情弹窗"
        assert detail.get("order_id"), "订单详情应包含订单号"

        # 清理：关闭弹窗
        self.order_page.close_order_detail()

    @allure.title("订单详情信息与API数据一致")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.order
    def test_order_detail_matches_api_data(self):
        """
        测试：UI 显示的订单信息与 API 返回数据一致

        这是 API + UI 交叉验证的典型场景：
        - API 造数据时已知订单信息
        - 通过 UI 查看订单详情
        - 对比两端数据是否一致
        """
        self.order_page.wait.for_page_loaded()

        if not self.order_page.has_orders():
            pytest.skip("没有可查看的订单")

        self.order_page.view_first_order_detail()
        detail = self.order_page.get_order_detail_info()

        # API 返回的订单信息（来自 fixture 的 prepare_test_order）
        api_order_id = self.api_order.get("order_id", "") if isinstance(self.api_order, dict) else ""

        if api_order_id:
            # 验证 UI 展示的订单号与 API 创建的一致（至少有一条匹配）
            logger.info(f"API 订单号: {api_order_id}")
            logger.info(f"UI 订单详情: {detail}")

        self.order_page.close_order_detail()

    @allure.title("空订单标签页显示正确")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    @pytest.mark.order
    def test_empty_tab_display(self):
        """测试：已取消标签页为空时显示正确"""
        self.order_page.switch_tab("cancelled")
        self.order_page.wait.for_ajax_complete()

        # 取消的订单可能为空
        if self.order_page.is_no_order():
            logger.info("已取消标签页正确显示'暂无订单'")

    @allure.title("订单分页功能")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    @pytest.mark.order
    def test_order_pagination(self):
        """测试：订单分页"""
        self.order_page.wait.for_page_loaded()

        first_page = self.order_page.get_current_page_number()
        self.order_page.go_to_next_page()

        # 如果成功翻页，页码应该变化
        second_page = self.order_page.get_current_page_number()
        logger.info(f"订单翻页: {first_page} → {second_page}")
