"""Static contract checks, analyzed by ty without making network calls."""

from typing import assert_type

from requests import Response

from mope import Mope
from mope.client import Client
from mope.json import JsonObject
from mope.models.payments import (
    CreatePaymentResponse,
    Currency,
    PaymentMetadata,
    PaymentRequest,
    PaymentStatus,
)
from mope.resources.shop import ShopResource
from mope.transport import ApiTransport


class CustomPaymentRequest(PaymentRequest):
    pass


def check_public_types(client: Mope, transport: Client, payload: object) -> None:
    api_transport: ApiTransport = transport
    assert_type(
        api_transport.call_api("GET", "shop/payment_request/payment-1"), Response
    )
    assert_type(client.shop, ShopResource)
    created = client.shop.create_payment_request(
        100, "order", "order-1", "EUR", "https://example.com"
    )
    assert_type(created, CreatePaymentResponse)
    assert_type(created.id, str)
    assert_type(created.url, str)
    payment = client.shop.get_payment_request("payment-1")
    assert_type(payment, PaymentRequest)
    assert_type(payment.amount, int)
    assert_type(payment.currency, Currency)
    assert_type(payment.status, PaymentStatus)
    assert_type(payment.meta_data, list[PaymentMetadata])
    assert_type(payment.meta_data[0]["value"], str)
    assert_type(payment.as_dict(), JsonObject)
    assert_type(transport.call_api("GET", "shop/payment_request/payment-1"), Response)
    assert_type(CreatePaymentResponse.from_json(payload), CreatePaymentResponse)
    assert_type(Currency.from_json(payload), Currency)
    assert_type(PaymentRequest.from_json(payload), PaymentRequest)
    assert_type(CustomPaymentRequest.from_json(payload), CustomPaymentRequest)


def check_transport_inputs(
    transport: Client,
    query: dict[str, str],
    form: dict[str, str],
    payload: dict[str, int],
) -> None:
    assert_type(
        transport.call_api("POST", "endpoint", params=query, data=form, json=payload),
        Response,
    )
