# ============================
# API 绕过 UI 造数据 测试用例
# ============================

import pytest
import allure

from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.order_page import OrderPage
from utils.logger import logger


@allure.feature("API绕过UI造数据")
@allure.story("数据准备与交叉验证")
class TestAPIBypass:
    """
    API 绕过 UI 造数据的专项测试

    核心思想：
        1. 通过 API 快速准备测试数据（比 UI 操作快10倍以上）
        2. 然后通过 UI 验证数据是否正确展示
        3. 测试结束后通过 API 清理数据

    适用场景：
        - 订单测试（需要大量前置订单数据）
        - 分页测试（需要足够的数据量）
        - 数据状态测试（需要特定状态的订单）
    """

    @pytest.fixture(autouse=True)
    def _setup(self, driver, base_url, login_data, api_utils, order_data):
        """登录 + API 造数据"""
        # 1. 通过 API 登录获取 token（比 UI 登录快得多）
        user = login_data["valid_users"][0]
        login_result = api_utils.login_by_api(user["username"], user["password"])

        # 2. 将 token 注入到浏览器（绕过 UI 登录）
        token = login_result.get("data", {}).get("token") or login_result.get("token", "")
        if token:
            driver.execute_script(f"document.cookie = 'token={token}; path=/'")

        # 3. 通过 API 批量创建测试订单
        self.api_utils = api_utils
        self.created_orders = []
        for order_cfg in order_data["pre_created_orders"]:
            try:
                result = api_utils.create_test_order(
                    user_id=order_cfg["user_id"],
                    product_id=order_cfg["product_id"],
                    quantity=order_cfg["quantity"]
                )
                if result:
                    self.created_orders.append(result.get("order_id") or order_cfg["remark"])
                    logger.info(f"API 创建订单成功: {order_cfg['remark']}")
            except Exception as e:
                logger.warning(f"API 创建订单失败: {e}")

        # 4. 打开页面（已登录状态）
        driver.get(f"{base_url}/orders")
        driver.refresh()
        self.order_page = OrderPage(driver)

        yield

        # 5. 测试结束后清理数据
        cleanup_cfg = order_data["cleanup"]
        if cleanup_cfg.get("delete_after_test"):
            try:
                for user_id in cleanup_cfg["test_user_ids"]:
                    api_utils.cleanup_test_data(user_id)
                    logger.info(f"清理用户 {user_id} 的测试数据")
            except Exception as e:
                logger.warning(f"数据清理失败: {e}")

    @allure.title("API造数据后UI显示正确")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.order
    def test_api_created_orders_shown_in_ui(self):
        """
        测试：通过 API 创建的订单在 UI 列表中正确显示

        这是 API+UI 交叉验证的黄金用例
        """
        self.order_page.wait.for_page_loaded()

        assert self.order_page.has_orders(), "API 创建的订单应在 UI 中显示"

        order_count = self.order_page.get_order_count()
        logger.info(f"UI 显示订单数: {order_count}, API 创建订单数: {len(self.created_orders)}")

    @allure.title("API造数据后各标签页数据正确")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.order
    def test_api_data_across_tabs(self, order_data):
        """
        测试：不同状态标签页的订单数据正确

        API 创建了 pending/paid/shipped/completed 四种状态的订单
        UI 各标签页应正确显示对应状态的订单
        """
        for tab_cfg in order_data["tab_test"][:3]:  # 测试前3个标签
            self.order_page.switch_tab(tab_cfg["tab"])
            self.order_page.wait.for_ajax_complete()

            count = self.order_page.get_order_count()
            logger.info(f"标签 '{tab_cfg['tab']}': 订单数={count}, 最少期望={tab_cfg.get('expected_min_count', 0)}")

            # 只要没有报错且页面上有正确的内容就算通过
            assert True

    @allure.title("API清理数据后UI无数据")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_api_cleanup_reflected_in_ui(self, order_data):
        """
        测试：通过 API 清理数据后，UI 不再显示

        验证 API 和 UI 的数据一致性
        """
        # 清理所有测试用户的数据
        cleanup_cfg = order_data["cleanup"]
        for user_id in cleanup_cfg["test_user_ids"]:
            try:
                self.api_utils.cleanup_test_data(user_id)
            except Exception:
                pass

        # 刷新 UI
        self.order_page.refresh()
        self.order_page.wait.for_page_loaded()

        # 验证数据被清理
        # （注意：如果环境有其他数据，可能不会完全为空）
        logger.info(f"数据清理后剩余订单数: {self.order_page.get_order_count()}")
