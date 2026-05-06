# ============================
# 数据库工具封装
# ============================

import pymysql
from contextlib import contextmanager
from config.settings import DB_CONFIG, ENV, ENV_URLS
from utils.logger import logger


class DBUtils:
    """
    数据库工具类
    用于测试数据的准备、清理和验证

    Usage:
        db = DBUtils()

        # 查询
        result = db.fetch_one("SELECT * FROM users WHERE id = %s", (1,))

        # 执行
        db.execute("DELETE FROM orders WHERE user_id = %s", (user_id,))

        # 上下文管理器（自动关闭连接）
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM users")
    """

    def __init__(self, db_config=None):
        """
        Args:
            db_config: 数据库配置字典，默认读取 settings
        """
        config = db_config or DB_CONFIG.copy()
        # 根据 ENV 覆盖 db_name
        env_db = ENV_URLS.get(ENV, {}).get("db_name")
        if env_db:
            config["database"] = env_db
        self.config = config

    def get_connection(self):
        """获取数据库连接（支持上下文管理器）"""
        @contextmanager
        def _connect():
            conn = None
            try:
                conn = pymysql.connect(
                    host=self.config["host"],
                    port=self.config["port"],
                    user=self.config["user"],
                    password=self.config["password"],
                    database=self.config["database"],
                    charset=self.config.get("charset", "utf8mb4"),
                    cursorclass=pymysql.cursors.DictCursor
                )
                logger.debug(f"数据库连接成功: {self.config['host']}:{self.config['port']}/{self.config['database']}")
                yield conn
            except Exception as e:
                logger.error(f"数据库连接失败: {e}")
                raise
            finally:
                if conn:
                    conn.close()
                    logger.debug("数据库连接已关闭")
        return _connect()

    def fetch_one(self, sql, params=None):
        """
        查询单条记录

        Args:
            sql: SQL 语句
            params: 参数元组

        Returns:
            dict: 查询结果字典，无结果返回 None
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchone()

    def fetch_all(self, sql, params=None):
        """
        查询多条记录

        Args:
            sql: SQL 语句
            params: 参数元组

        Returns:
            list[dict]: 查询结果列表
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()

    def execute(self, sql, params=None, commit=True):
        """
        执行 SQL 语句（INSERT/UPDATE/DELETE）

        Args:
            sql: SQL 语句
            params: 参数元组
            commit: 是否自动提交

        Returns:
            int: 影响的行数
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                affected = cursor.execute(sql, params)
                if commit:
                    conn.commit()
                    logger.debug(f"SQL 执行成功，影响 {affected} 行: {sql}")
                return affected

    def execute_many(self, sql, params_list, commit=True):
        """
        批量执行 SQL

        Args:
            sql: SQL 语句
            params_list: 参数列表 [[params1], [params2], ...]
            commit: 是否自动提交

        Returns:
            int: 总影响行数
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                total = cursor.executemany(sql, params_list)
                if commit:
                    conn.commit()
                return total

    # ========== 常用测试数据操作 ==========

    def get_test_user(self, user_id):
        """获取测试用户信息"""
        return self.fetch_one(
            "SELECT * FROM users WHERE id = %s AND is_test = 1",
            (user_id,)
        )

    def clean_test_orders(self, user_id):
        """清理测试用户的订单数据"""
        return self.execute(
            "DELETE FROM orders WHERE user_id = %s AND is_test = 1",
            (user_id,)
        )

    def get_user_balance(self, user_id):
        """查询用户余额"""
        result = self.fetch_one(
            "SELECT balance FROM accounts WHERE user_id = %s",
            (user_id,)
        )
        return result["balance"] if result else 0.0
