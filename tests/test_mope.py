import json
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Event, Thread
from unittest.mock import Mock, patch

import pytest
from requests import HTTPError, ReadTimeout, Response, Timeout

from mope.client import Client, Mope, RequestTimeout
from mope.errors import MopeAPIError
from mope.json import JsonObject


@pytest.fixture
def payment() -> JsonObject:
    return {
        "id": "payment-123",
        "amount": 35638,
        "created_at": "2019-12-02T14:28:14+00:00",
        "description": "Order",
        "expires_at": "2019-12-03T14:28:14+00:00",
        "currency": {"name": "Surinamese dollar", "code": "SRD", "symbol": "$"},
        "status": "paid",
        "meta_data": [{"key": "order_id", "value": "order-1"}],
    }


@pytest.fixture
def http_request() -> Iterator[Mock]:
    with patch("requests.request") as request:
        yield request


def response_for(payload: object, status: int = 200) -> Response:
    response = Response()
    response.status_code = status
    response._content = json.dumps(payload).encode()
    return response


def test_create_payment_sends_correct_request(http_request: Mock) -> None:
    created = {"id": "payment-123", "url": "https://mope.sr/p/payment-123"}
    http_request.return_value = response_for(created)
    result = Mope("token").shop.create_payment_request(
        100, "Order", "order-1", "SRD", "https://example.com/return"
    )

    assert result.as_dict() == created
    http_request.assert_called_once()
    sent = http_request.call_args.kwargs
    assert sent["method"] == "POST"
    assert sent["url"] == "https://api.mope.sr/api/shop/payment_request"
    assert sent["headers"]["Authorization"] == "Bearer token"
    assert sent["timeout"] == (5.0, 30.0)
    assert sent["json"] == {
        "amount": 100,
        "description": "Order",
        "order_id": "order-1",
        "currency": "SRD",
        "redirect_url": "https://example.com/return",
    }


@pytest.mark.parametrize("timeout", [2.5, (1.0, 3.0)])
def test_fetch_payment_preserves_details_and_configured_timeout(
    http_request: Mock, payment: JsonObject, timeout: RequestTimeout
) -> None:
    http_request.return_value = response_for(payment)
    result = Mope("token", timeout=timeout).shop.get_payment_request("payment-123")

    assert result.as_dict() == payment
    assert result.currency.code == "SRD"
    http_request.assert_called_once()
    sent = http_request.call_args.kwargs
    assert sent["method"] == "GET"
    assert sent["url"] == "https://api.mope.sr/api/shop/payment_request/payment-123"
    assert sent["timeout"] == timeout


@pytest.mark.parametrize("create", [True, False])
def test_shop_errors_preserve_api_details_and_http_error_compatibility(
    http_request: Mock, create: bool
) -> None:
    code = 1033 if create else 1002
    details: JsonObject = {
        "code": code,
        "message": "API rejected request",
        "data": {"reason": "test"},
    }
    # Exercise both shapes shown in Mopé's schema and examples.
    response = response_for({"error": details} if create else details, status=400)
    http_request.return_value = response
    client = Mope("token")

    with pytest.raises(HTTPError) as raised:
        if create:
            client.shop.create_payment_request(
                100, "Order", "order-1", "SRD", "https://example.com"
            )
        else:
            client.shop.get_payment_request("payment-123")

    error = raised.value
    assert isinstance(error, MopeAPIError)
    assert error.status_code == 400
    assert error.code == code
    assert error.message == details["message"]
    assert error.data == details["data"]
    assert error.response is response
    assert isinstance(error.__cause__, HTTPError)


@pytest.mark.parametrize(
    "body",
    [
        b"<html>Service unavailable</html>",
        b'{"error": {"code": "invalid", "message": "Error"}}',
    ],
)
def test_malformed_error_body_does_not_mask_http_failure(
    http_request: Mock, body: bytes
) -> None:
    response = response_for(None, status=503)
    response._content = body
    http_request.return_value = response

    with pytest.raises(MopeAPIError) as raised:
        Mope("token").shop.get_payment_request("payment-123")

    assert raised.value.status_code == 503
    assert raised.value.code is None
    assert "503" in raised.value.message
    assert raised.value.response is response


@pytest.mark.parametrize(
    "invalid, expected",
    [
        ("json", ValueError),
        ("missing", KeyError),
        ("amount", TypeError),
        ("status", ValueError),
        ("meta_data", TypeError),
    ],
)
def test_invalid_payment_response_is_rejected(
    http_request: Mock, payment: JsonObject, invalid: str, expected: type[Exception]
) -> None:
    changes: JsonObject = {
        "amount": True,
        "status": "unknown",
        "meta_data": [{"key": "order_id", "value": 1}],
    }
    if invalid in changes:
        payment[invalid] = changes[invalid]
    response = response_for({} if invalid == "missing" else payment)
    if invalid == "json":
        response._content = b"not JSON"
    http_request.return_value = response

    with pytest.raises(expected):
        Mope("token").shop.get_payment_request("payment-123")


@pytest.mark.parametrize("timeout", [0.0, (1.0, float("inf"))])
def test_timeout_must_be_positive_and_finite(timeout: RequestTimeout) -> None:
    with pytest.raises(ValueError, match="finite and greater than zero"):
        Mope("token", timeout=timeout)


def test_payment_creation_timeout_is_not_retried(http_request: Mock) -> None:
    failure = Timeout("Server stopped responding")
    http_request.side_effect = failure
    with pytest.raises(Timeout) as raised:
        Mope("token").shop.create_payment_request(
            100, "Order", "order-1", "SRD", "https://example.com"
        )
    assert raised.value is failure
    http_request.assert_called_once()


def test_read_timeout_interrupts_a_stalled_http_response() -> None:
    received = Event()
    release = Event()

    class StalledHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            received.set()
            release.wait(timeout=5)

    with ThreadingHTTPServer(("127.0.0.1", 0), StalledHandler) as server:
        worker = Thread(target=server.serve_forever)
        worker.start()
        try:
            with pytest.raises(ReadTimeout):
                Client("token", timeout=(1.0, 0.1)).call_api(
                    "GET", f"http://127.0.0.1:{server.server_port}/stalled"
                )
            assert received.is_set()
        finally:
            release.set()
            server.shutdown()
            worker.join(timeout=5)
