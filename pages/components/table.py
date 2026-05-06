# ============================
# Table - 通用表格组件
# ============================

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.base_page import BasePage
from utils.logger import logger


class Table(BasePage):
    """
    通用表格组件（可复用）
    适用于列表页、数据展示页等场景

    功能：获取表头、获取行数据、按列排序、翻页、搜索表格
    """

    # ---------- 元素定位（传入具体的 table 容器） ----------
    def __init__(self, driver, container_locator):
        """
        Args:
            driver: WebDriver 实例
            container_locator: 表格容器的定位器
        """
        super().__init__(driver)
        self.container = container_locator
        self.TH = f"{container_locator[1]} thead th"
        self.TR = f"{container_locator[1]} tbody tr"
        self.TD = f"{container_locator[1]} tbody td"
        self.PAGER = f"{container_locator[1]} .pagination"
        self.PAGER_NEXT = f"{container_locator[1]} .pagination .next"
        self.PAGER_INFO = f"{container_locator[1]} .pagination .page-info"

    # ---------- 信息获取 ----------

    def get_headers(self):
        """获取所有表头文本"""
        headers = []
        by = self.container[0]
        for th in self.driver.find_elements(by, self.TH):
            headers.append(th.text.strip())
        return headers

    def get_row_count(self):
        """获取表格行数"""
        by = self.container[0]
        return len(self.driver.find_elements(by, self.TR))

    def get_cell_text(self, row_index, col_index):
        """
        获取指定单元格的文本

        Args:
            row_index: 行索引（从0开始）
            col_index: 列索引（从0开始）
        """
        by = self.container[0]
        rows = self.driver.find_elements(by, self.TR)
        if row_index >= len(rows):
            raise IndexError(f"行索引 {row_index} 超出范围，共 {len(rows)} 行")
        cells = rows[row_index].find_elements(By.TAG_NAME, "td")
        if col_index >= len(cells):
            raise IndexError(f"列索引 {col_index} 超出范围，共 {len(cells)} 列")
        return cells[col_index].text.strip()

    def get_row_data(self, row_index):
        """获取一行的所有单元格数据"""
        by = self.container[0]
        rows = self.driver.find_elements(by, self.TR)
        if row_index >= len(rows):
            raise IndexError(f"行索引 {row_index} 超出范围")
        cells = rows[row_index].find_elements(By.TAG_NAME, "td")
        return [cell.text.strip() for cell in cells]

    def get_all_data(self):
        """获取整个表格的数据（二维列表）"""
        data = []
        for i in range(self.get_row_count()):
            data.append(self.get_row_data(i))
        return data

    def get_column_data(self, col_index):
        """获取指定列的所有数据"""
        return [self.get_cell_text(i, col_index) for i in range(self.get_row_count())]

    def find_row_by_column(self, col_index, value):
        """
        根据列值查找行索引

        Args:
            col_index: 列索引
            value: 期望的值

        Returns:
            int: 行索引，未找到返回 -1
        """
        for i in range(self.get_row_count()):
            if self.get_cell_text(i, col_index) == str(value):
                return i
        return -1

    # ---------- 操作 ----------

    def click_row(self, row_index):
        """点击指定行"""
        by = self.container[0]
        rows = self.driver.find_elements(by, self.TR)
        rows[row_index].click()
        logger.info(f"点击第 {row_index + 1} 行")

    def click_cell_button(self, row_index, button_text):
        """
        点击某行中指定的按钮

        Args:
            row_index: 行索引
            button_text: 按钮文本
        """
        by = self.container[0]
        rows = self.driver.find_elements(by, self.TR)
        buttons = rows[row_index].find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if btn.text.strip() == button_text:
                btn.click()
                logger.info(f"点击第 {row_index + 1} 行的 '{button_text}' 按钮")
                return

    def sort_by_column(self, col_index):
        """点击表头进行排序"""
        by = self.container[0]
        headers = self.driver.find_elements(by, self.TH)
        if col_index < len(headers):
            headers[col_index].click()
            logger.info(f"按第 {col_index + 1} 列排序")

    def is_empty(self):
        """表格是否为空"""
        return self.get_row_count() == 0
