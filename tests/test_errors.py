import json
import pickle
from unittest.mock import patch

import pytest
from requests import HTTPError, Request, Response

from mope.client import Mope
from mope.errors import MopeAPIError, raise_for_status
from mope.json import JsonObject


def error_response(body: bytes, status_code: int = 400) -> Response:
    response = Response()
    response.status_code = status_code
    response.reason = "Bad Request" if status_code == 400 else "Service Unavailable"
    response.url = "https://api.mope.sr/api/shop/payment_request"
    response.request = Request("POST", response.url).prepare()
    response._content = body
    return response


@pytest.mark.parametrize("wrapped", [True, False])
def test_api_error_exposes_validated_details_and_preserves_http_error(
    wrapped: bool,
) -> None:
    details: JsonObject = {
        "code": 1033,
        "message": "Account limits exceeded",
        "data": {"limit": 100},
    }
    payload: JsonObject = {"error": details} if wrapped else details
    response = error_response(json.dumps(payload).encode())

    with pytest.raises(HTTPError) as raised:
        raise_for_status(response)

    error = raised.value
    assert isinstance(error, MopeAPIError)
    assert error.code == 1033
    assert error.message == "Account limits exceeded"
    assert str(error) == "Account limits exceeded"
    assert error.data == {"limit": 100}
    assert error.status_code == 400
    assert error.response is response
    assert error.request is response.request
    assert isinstance(error.__cause__, HTTPError)
    assert error.__cause__.response is response


@pytest.mark.parametrize(
    "body",
    [
        b"",
        b"<html>Service unavailable</html>",
        b"null",
        b"[]",
        b"{}",
        b'{"error": null}',
        b'{"error": {"code": "1033", "message": "Invalid code"}}',
        b'{"error": {"code": true, "message": "Invalid code"}}',
        b'{"error": {"code": 1033, "message": 42}}',
        b'{"error": {"message": "Missing code"}}',
        b'{"error": {"code": 1033}}',
        b'{"error": {"code": 1033, "message": "Invalid data", "data": NaN}}',
    ],
)
def test_bad_error_body_preserves_http_failure(body: bytes) -> None:
    response = error_response(body, status_code=503)

    with pytest.raises(MopeAPIError) as raised:
        raise_for_status(response)

    error = raised.value
    assert error.status_code == 503
    assert error.code is None
    assert error.data is None
    assert "503" in error.message
    assert "Service Unavailable" in error.message
    assert error.response is response
    assert isinstance(error.__cause__, HTTPError)


@pytest.mark.parametrize("create", [True, False])
def test_shop_methods_raise_typed_api_errors(create: bool) -> None:
    response = error_response(
        b'{"error": {"code": 1033, "message": "Account limits exceeded"}}'
    )
    with patch("requests.request", return_value=response):
        with pytest.raises(MopeAPIError) as raised:
            client = Mope("token")
            if create:
                client.shop.create_payment_request(
                    100, "order", "order-1", "SRD", "https://example.com"
                )
            else:
                client.shop.get_payment_request("payment-123")

    assert raised.value.code == 1033


@pytest.mark.parametrize(
    "body, expected",
    [
        (b"<html>OK</html>", ValueError),
        (b"{}", KeyError),
        (b'{"id": 1, "url": "https://mope.sr/p/1"}', TypeError),
    ],
)
def test_invalid_success_response_keeps_validation_exceptions(
    body: bytes, expected: type[Exception]
) -> None:
    response = error_response(body, status_code=200)
    with patch("requests.request", return_value=response):
        with pytest.raises(expected):
            Mope("token").shop.create_payment_request(
                100, "order", "order-1", "SRD", "https://example.com"
            )


def test_api_error_survives_serialization() -> None:
    response = error_response(
        b'{"error": {"code": 1033, "message": "Account limits exceeded", "data": null}}'
    )
    error = MopeAPIError.from_response(response, fallback_message="HTTP error")
    restored: object = pickle.loads(pickle.dumps(error))
    assert isinstance(restored, MopeAPIError)
    assert restored.status_code == 400
    assert restored.code == 1033
    assert restored.message == "Account limits exceeded"
    assert restored.data is None
