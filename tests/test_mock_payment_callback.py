# tests/test_mock_payment_callback.py
"""
演示使用 responses 库模拟第三方支付回调，实现依赖隔离。
不依赖真实后端接口，仅展示 Mock 思想，适合面试讲解。
"""

import requests
import pytest
import responses
from client.api_client import ApiClient
from config import settings


class TestMockExternalPayment:
    """模拟外部支付回调的测试集合"""

    @responses.activate
    def test_mock_payment_gateway_query(self):
        """
        场景：我们的系统需要调用第三方支付平台的查询接口。
        使用 responses 模拟该接口返回「支付成功」，避免真实网络请求。
        """
        # 外部支付查询接口 URL（假设）
        payment_query_url = "https://api.payment-gateway.com/v1/query"

        # 模拟返回的 JSON 数据
        mock_response = {
            "transaction_id": "TXN123456",
            "status": "SUCCESS",
            "amount": 99.99
        }

        # 注册 mock：对该 URL 的 GET 请求返回预设的 JSON 和 200 状态码
        responses.add(
            responses.GET,
            payment_query_url,
            json=mock_response,
            status=200,
        )

        # 执行请求（模拟我们的业务代码调用外部接口）
        response = requests.get(payment_query_url)

        # 断言：拿到的是 mock 的数据，不是真实网络数据
        assert response.status_code == 200
        assert response.json() == mock_response
        # 验证确实走了一次 mock（没有发真实请求）
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == payment_query_url

    @responses.activate
    def test_mock_payment_callback_endpoint(self):
        """
        场景：第三方支付平台主动回调我们的系统（例如 `/callback/payment`）。
        这里模拟回调请求的发送和接收，验证我们的回调处理逻辑是否正确。
        注：由于你的后端目前没有实际回调接口，这里只演示 Mock 回调的 HTTP 响应，
        实际使用时可以结合数据库验证。
        """
        callback_url = f"{settings.base_url}/callback/payment"

        # 模拟我们的回调接口返回成功
        responses.add(
            responses.POST,
            callback_url,
            json={"code": 0, "message": "Callback received"},
            status=200,
        )

        # 模拟发起回调请求（通常由支付平台发起，测试中我们手动模拟）
        callback_payload = {
            "transaction_id": "TXN789",
            "status": "SUCCESS",
            "sign": "abc123"
        }

        # 使用项目的 ApiClient 发送请求（或直接用 requests）
        client = ApiClient(base_url=settings.base_url)
        resp = client.post("/callback/payment", body=callback_payload)

        # 断言响应符合预期
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

        # 验证 mock 被调用了一次
        assert len(responses.calls) == 1

    @responses.activate
    def test_mock_payment_with_multiple_scenarios(self):
        """
        演示同一个接口模拟不同的返回结果，覆盖多种业务分支。
        """
        payment_url = "https://api.payment.com/status"

        # 场景1：第一次调用返回 "PROCESSING"
        responses.add(
            responses.GET,
            payment_url,
            json={"status": "PROCESSING"},
            status=200,
        )
        resp1 = requests.get(payment_url)
        assert resp1.json()["status"] == "PROCESSING"

        # 场景2：第二次调用返回 "SUCCESS"（模拟轮询场景）
        responses.replace(
            responses.GET,
            payment_url,
            json={"status": "SUCCESS"},
            status=200,
        )
        resp2 = requests.get(payment_url)
        assert resp2.json()["status"] == "SUCCESS"

        # 场景3：第三次调用模拟服务器错误
        responses.replace(
            responses.GET,
            payment_url,
            json={"error": "Internal Server Error"},
            status=500,
        )
        resp3 = requests.get(payment_url)
        assert resp3.status_code == 500

    def test_mock_with_context_manager(self):
        """
        使用 with 语句块管理 mock，更安全（自动清理）。
        """
        external_api = "https://api.external.com/points"
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                external_api,
                json={"points_added": 10},
                status=200,
            )
            response = requests.post(external_api, json={"user_id": 1})
            assert response.json()["points_added"] == 10

        # 退出 with 块后，mock 自动失效
        # 真实发送会失败（因为 URL 不存在），但这里不演示