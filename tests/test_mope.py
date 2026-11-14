import unittest
from unittest import mock
from unittest.mock import Mock

from requests import HTTPError, Response

from mope import Mope
from mope.__version__ import __version__
from mope.json import JsonObject
from mope.models.payments import CreatePaymentResponse, Currency, PaymentRequest

mock_payment_request: JsonObject = {
    "id": "c43f24a3-df4f-43b7-9045-b454529369dc",
    "amount": 35638,
    "created_at": "2019-12-02T14:28:14+00:00",
    "description": "Order for a lot of beer",
    "expires_at": "2019-12-03T14:28:14+00:00",
    "currency": {"name": "Surinamese dollar", "code": "SRD", "symbol": "$"},
    "status": "paid",
    "meta_data": [],
}


class MopeTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mope = Mope("fake-token")
        self.client = self.mope._client

    @mock.patch("requests.request")
    def test_call_api(self, mock_request: Mock) -> None:
        expected_response = Response()
        mock_request.return_value = expected_response
        response = self.client.call_api(
            "POST", "https://api.mope.sr/api", json={"amount": 1000}
        )
        self.assertIs(response, expected_response)

        mock_request.assert_called_once_with(
            url="https://api.mope.sr/api",
            json={"amount": 1000},
            data=None,
            method="POST",
            params=None,
            headers={
                "User-Agent": f"Python Mope {__version__}",
                "Content-Type": "application/json",
                "Authorization": "Bearer fake-token",
            },
        )

    @mock.patch("requests.request")
    def test_shop_create_payment_request(self, mock_request: Mock) -> None:
        payload = {"id": "payment-123", "url": "https://api.mope.sr/pay/payment-123"}
        mock_request.return_value.json.return_value = payload

        response = self.mope.shop.create_payment_request(
            amount=1000,
            description="test",
            order_id="test-1",
            currency="SRD",
            redirect_url="https://www.sup.com/products/1",
        )
        self.assertIsInstance(response, CreatePaymentResponse)
        self.assertEqual(response.as_dict(), payload)
        mock_request.assert_called_once_with(
            method="POST",
            url="https://api.mope.sr/shop/payment_request",
            params=None,
            data=None,
            json={
                "amount": 1000,
                "order_id": "test-1",
                "currency": "SRD",
                "description": "test",
                "redirect_url": "https://www.sup.com/products/1",
            },
            headers={
                "User-Agent": f"Python Mope {__version__}",
                "Content-Type": "application/json",
                "Authorization": "Bearer fake-token",
            },
        )

    @mock.patch("requests.request")
    def test_shop_get_payment_request(self, mock_request: Mock) -> None:
        mock_request.return_value = Mock(ok=True)
        mock_request.return_value.json.return_value = mock_payment_request

        mock_response = self.mope.shop.get_payment_request(
            payment_id="c43f24a3-df4f-43b7-9045-b454529369dc"
        )

        self.assertTrue(isinstance(mock_response, PaymentRequest))
        self.assertTrue(isinstance(mock_response.currency, Currency))

        self.assertEqual(mock_response.as_dict(), mock_payment_request)

    @mock.patch("requests.request")
    def test_invalid_response_is_rejected(self, mock_request: Mock) -> None:
        mock_request.return_value.json.return_value = {
            **mock_payment_request,
            "amount": True,
        }

        with self.assertRaisesRegex(TypeError, "amount must be an integer"):
            self.mope.shop.get_payment_request("payment-123")

    @mock.patch("requests.request")
    def test_invalid_request_json_is_rejected(self, mock_request: Mock) -> None:
        with self.assertRaisesRegex(TypeError, "request.amount must be a JSON value"):
            self.client.call_api("POST", "endpoint", json={"amount": object()})

        mock_request.assert_not_called()

    @mock.patch("requests.request")
    def test_http_errors_are_raised_before_parsing(self, mock_request: Mock) -> None:
        mock_request.return_value.raise_for_status.side_effect = HTTPError("Not found")

        with self.assertRaises(HTTPError):
            self.mope.shop.get_payment_request("payment-123")
        with self.assertRaises(HTTPError):
            self.mope.shop.create_payment_request(
                100, "order", "order-1", "SRD", "https://example.com"
            )

        mock_request.return_value.json.assert_not_called()
