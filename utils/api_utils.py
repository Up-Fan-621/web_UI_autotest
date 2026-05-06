# ============================
# API 工具封装
# ============================

import json
import time
import requests
from requests.exceptions import RequestException
from config.settings import API_BASE_URL, API_TOKEN, API_TIMEOUT
from utils.logger import logger


class APIUtils:
    """
    HTTP API 工具类
    用于：
    1. 绕过 UI 直接调用后端接口（造数据/清理数据）
    2. 接口数据验证（UI 测试结果与接口数据交叉验证）

    Usage:
        api = APIUtils()

        # 造数据 - 通过接口创建测试订单
        order = api.post("/api/orders", json={
            "user_id": 1001,
            "product_id": 2001,
            "quantity": 2
        })

        # 查询数据
        user = api.get("/api/users/1001")

        # 清理数据
        api.delete("/api/test/orders", params={"user_id": 1001})
    """

    def __init__(self, base_url=None, token=None, timeout=None):
        """
        Args:
            base_url: API 基础 URL
            token: 认证 token
            timeout: 请求超时时间
        """
        self.base_url = (base_url or API_BASE_URL).rstrip("/")
        self.timeout = timeout or API_TIMEOUT
        self.session = requests.Session()

        # 默认请求头
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Request-Source": "ui-auto-test"  # 标识来自自动化测试
        })

        # 设置认证 token
        token = token or API_TOKEN
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

        logger.info(f"APIUtils 初始化: base_url={self.base_url}")

    def _request(self, method, path, **kwargs):
        """
        统一请求方法

        Args:
            method: HTTP 方法 GET/POST/PUT/DELETE
            path: 接口路径
            **kwargs: requests 参数

        Returns:
            dict: 响应 JSON 数据

        Raises:
            AssertionError: 状态码非 2xx 时抛出
        """
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)

        logger.info(f"→ {method} {url}")
        if kwargs.get("json"):
            logger.debug(f"  请求体: {json.dumps(kwargs['json'], ensure_ascii=False)[:500]}")
        if kwargs.get("params"):
            logger.debug(f"  参数: {kwargs['params']}")

        try:
            start_time = time.time()
            response = self.session.request(method, url, **kwargs)
            elapsed = round((time.time() - start_time) * 1000)

            logger.info(f"← {response.status_code} ({elapsed}ms)")

            # 非 2xx 响应
            if not response.ok:
                logger.error(f"API 请求失败: {response.status_code} {response.text[:200]}")
                try:
                    error_detail = response.json()
                except ValueError:
                    error_detail = response.text
                raise AssertionError(
                    f"API 请求失败 [{method} {url}]: "
                    f"status={response.status_code}, body={error_detail}"
                )

            # 解析 JSON
            try:
                return response.json()
            except ValueError:
                return {"raw_text": response.text}

        except RequestException as e:
            logger.error(f"API 请求异常: {e}")
            raise

    def get(self, path, params=None, **kwargs):
        """GET 请求"""
        return self._request("GET", path, params=params, **kwargs)

    def post(self, path, json=None, data=None, **kwargs):
        """POST 请求"""
        return self._request("POST", path, json=json, data=data, **kwargs)

    def put(self, path, json=None, **kwargs):
        """PUT 请求"""
        return self._request("PUT", path, json=json, **kwargs)

    def delete(self, path, params=None, **kwargs):
        """DELETE 请求"""
        return self._request("DELETE", path, params=params, **kwargs)

    # ========== 常用测试数据准备方法 ==========

    def login_by_api(self, username, password):
        """
        通过 API 登录，获取 token（绕过 UI 登录流程）

        Returns:
            dict: {"token": "xxx", "user_id": 123}
        """
        result = self.post("/api/auth/login", json={
            "username": username,
            "password": password
        })
        token = result.get("data", {}).get("token") or result.get("token")
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        logger.info(f"API 登录成功: user={username}")
        return result

    def create_test_order(self, user_id, product_id, quantity=1):
        """通过 API 创建测试订单"""
        return self.post("/api/orders", json={
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity
        })

    def cleanup_test_data(self, user_id):
        """清理指定用户的测试数据"""
        return self.delete("/api/test/cleanup", params={"user_id": user_id})

    def set_user_balance(self, user_id, balance):
        """设置测试用户余额（仅限测试环境）"""
        return self.put("/api/test/users/balance", json={
            "user_id": user_id,
            "balance": balance
        })

    def upload_file(self, file_path, upload_path="/api/upload"):
        """
        上传文件

        Args:
            file_path: 本地文件路径
            upload_path: 上传接口路径

        Returns:
            dict: 上传结果
        """
        with open(file_path, "rb") as f:
            files = {"file": f}
            return self._request("POST", upload_path, files=files)
