"""Verify that installed-package consumers retain useful types."""

from typing import assert_type

from requests import Response

from mope.client import Client, Mope
from mope.errors import MopeAPIError
from mope.json import JsonObject, JsonValue
from mope.models.payments import CreatePaymentResponse, PaymentRequest, PaymentStatus


def check_payment_types(client: Mope) -> None:
    created = client.shop.create_payment_request(
        100, "Order", "order-1", "SRD", "https://example.com"
    )
    assert_type(created, CreatePaymentResponse)
    payment = client.shop.get_payment_request("payment-123")
    assert_type(payment, PaymentRequest)
    assert_type(payment.amount, int)
    assert_type(payment.status, PaymentStatus)
    assert_type(payment.meta_data[0]["value"], str)
    assert_type(payment.as_dict(), JsonObject)


def check_inputs_and_errors(
    params: dict[str, str], payload: dict[str, int], error: MopeAPIError
) -> None:
    client = Client("token", timeout=5.0)
    Mope("token", timeout=(1.0, 5.0))
    assert_type(
        client.call_api("POST", "endpoint", params=params, data=params, json=payload),
        Response,
    )
    assert_type(error.code, int | None)
    assert_type(error.status_code, int | None)
    assert_type(error.message, str)
    assert_type(error.data, JsonValue)
