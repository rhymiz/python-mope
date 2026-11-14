from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Event, Thread
from unittest.mock import patch

import pytest
from requests import ConnectionError, ReadTimeout, Timeout

from mope.client import Client, Mope, RequestTimeout


@pytest.mark.parametrize("timeout", [2, 2.5, (1, 3), (1.5, 3.5)])
def test_configured_timeout_reaches_transport(timeout: RequestTimeout) -> None:
    with patch("requests.request") as request:
        client = Client("token", timeout=timeout)
        client.call_api("GET", "shop/payment_request/payment-123")
        assert request.call_args.kwargs["timeout"] == timeout
        assert request.call_args.kwargs["url"] == (
            "https://api.mope.sr/api/shop/payment_request/payment-123"
        )

        api = Mope("token", timeout=timeout)
        request.return_value.json.return_value = {
            "id": "payment-123",
            "url": "https://mope.sr/p/payment-123",
        }
        api.shop.create_payment_request(
            100, "order", "order-1", "SRD", "https://example.com"
        )
        assert request.call_args.kwargs["timeout"] == timeout


@pytest.mark.parametrize(
    "timeout", [0.0, -1.0, float("inf"), float("nan"), (1.0, 0.0), (float("inf"), 2.0)]
)
@pytest.mark.parametrize("client_type", [Client, Mope])
def test_non_positive_or_unbounded_timeout_is_rejected(
    client_type: type[Client] | type[Mope], timeout: RequestTimeout
) -> None:
    with pytest.raises(ValueError, match="finite and greater than zero"):
        client_type("token", timeout=timeout)


@pytest.mark.parametrize(
    "failure", [Timeout("timeout"), ConnectionError("connection failed")]
)
def test_network_errors_propagate_without_retry(failure: Exception) -> None:
    with patch("requests.request", side_effect=failure) as request:
        with pytest.raises(type(failure)) as raised:
            Mope("token").shop.create_payment_request(
                100, "order", "order-1", "SRD", "https://example.com"
            )
        assert raised.value is failure
        request.assert_called_once()


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
