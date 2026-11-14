import pytest

from mope.json import JsonObject, json_object
from mope.models.payments import (
    BaseModel,
    CreatePaymentResponse,
    Currency,
    PaymentRequest,
    PaymentStatus,
)


@pytest.fixture
def payment_payload() -> JsonObject:
    return {
        "id": "payment-123",
        "amount": 35638,
        "created_at": "2019-12-02T14:28:14+00:00",
        "description": "Order for a lot of beer",
        "expires_at": "2019-12-03T14:28:14+00:00",
        "currency": {"name": "Surinamese dollar", "code": "SRD", "symbol": "$"},
        "status": "paid",
        "meta_data": [{"key": "order_id", "value": "beer-order-123"}],
    }


@pytest.mark.parametrize("status", ["open", "scanned", "unconfirmed", "paid"])
def test_payment_round_trip(payment_payload: JsonObject, status: PaymentStatus) -> None:
    payment_payload["status"] = status
    payment = PaymentRequest.from_json(payment_payload)

    assert payment.amount == 35638
    assert isinstance(payment.currency, Currency)
    assert payment.currency.code == "SRD"
    assert payment.status == status
    assert payment.meta_data == [{"key": "order_id", "value": "beer-order-123"}]
    assert payment.as_dict() == payment_payload


@pytest.mark.parametrize("amount", [True, False, "100", 100.5, None])
def test_amount_is_not_coerced(payment_payload: JsonObject, amount: object) -> None:
    payload: dict[str, object] = dict(payment_payload)
    payload["amount"] = amount

    with pytest.raises(TypeError, match="amount must be an integer"):
        PaymentRequest.from_json(payload)


@pytest.mark.parametrize("field", ["id", "created_at", "description", "expires_at"])
def test_payment_string_fields_are_validated(
    payment_payload: JsonObject, field: str
) -> None:
    payment_payload[field] = 123

    with pytest.raises(TypeError, match=f"{field} must be a string"):
        PaymentRequest.from_json(payment_payload)


@pytest.mark.parametrize("status", ["expired", None, 1, True])
def test_invalid_status_is_rejected(
    payment_payload: JsonObject, status: object
) -> None:
    payload: dict[str, object] = dict(payment_payload)
    payload["status"] = status

    with pytest.raises(ValueError, match="status must be"):
        PaymentRequest.from_json(payload)


@pytest.mark.parametrize(
    "metadata",
    [None, {}, "metadata", [1], [{"key": 1, "value": "x"}], [{"key": "x", "value": 1}]],
)
def test_metadata_is_validated(payment_payload: JsonObject, metadata: object) -> None:
    payload: dict[str, object] = dict(payment_payload)
    payload["meta_data"] = metadata

    with pytest.raises(TypeError, match="meta_data"):
        PaymentRequest.from_json(payload)


@pytest.mark.parametrize("field", ["key", "value"])
def test_metadata_requires_both_fields(payment_payload: JsonObject, field: str) -> None:
    entry: JsonObject = {"key": "order_id", "value": "order-123"}
    del entry[field]
    payment_payload["meta_data"] = [entry]

    with pytest.raises(KeyError, match=field):
        PaymentRequest.from_json(payment_payload)


@pytest.mark.parametrize(
    "field",
    [
        "id",
        "amount",
        "created_at",
        "description",
        "expires_at",
        "currency",
        "status",
        "meta_data",
    ],
)
def test_payment_requires_all_fields(payment_payload: JsonObject, field: str) -> None:
    del payment_payload[field]

    with pytest.raises(KeyError, match=field):
        PaymentRequest.from_json(payment_payload)


@pytest.mark.parametrize("field", ["name", "code", "symbol"])
def test_currency_fields_are_validated(field: str) -> None:
    payload: JsonObject = {"name": "Surinamese dollar", "code": "SRD", "symbol": "$"}
    payload[field] = None

    with pytest.raises(TypeError, match=f"currency.{field} must be a string"):
        Currency.from_json(payload)


@pytest.mark.parametrize("field", ["id", "url"])
def test_creation_fields_are_validated(field: str) -> None:
    payload: JsonObject = {"id": "payment-123", "url": "https://mope.sr/p/payment-123"}
    payload[field] = 123

    with pytest.raises(TypeError, match=f"{field} must be a string"):
        CreatePaymentResponse.from_json(payload)


@pytest.mark.parametrize("model", [CreatePaymentResponse, Currency, PaymentRequest])
@pytest.mark.parametrize("payload", [None, [], "response", 1])
def test_models_require_objects(model: type[BaseModel], payload: object) -> None:
    with pytest.raises(TypeError, match="must be a JSON object"):
        model.from_json(payload)


@pytest.mark.parametrize("payload", [{1: "value"}, {"nested": {1: "value"}}])
def test_json_object_keys_must_be_strings(payload: object) -> None:
    with pytest.raises(TypeError, match="must have string keys"):
        json_object(payload)


@pytest.mark.parametrize("value", [object(), {1, 2}, (1, 2)])
def test_non_json_values_are_rejected(value: object) -> None:
    with pytest.raises(TypeError, match="must be a JSON value"):
        json_object({"nested": [value]})


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_json_numbers_are_rejected(value: float) -> None:
    with pytest.raises(ValueError, match="finite JSON number"):
        json_object({"nested": [value]})


def test_json_preserves_valid_nested_values() -> None:
    payload: JsonObject = {"nested": [None, True, 1, 1.5, "text", {"key": "value"}]}
    assert json_object(payload) == payload


def test_serialization_does_not_share_mutable_metadata(
    payment_payload: JsonObject,
) -> None:
    payment = PaymentRequest.from_json(payment_payload)
    serialized = payment.as_dict()
    payment.meta_data[0]["value"] = "changed"

    assert serialized == payment_payload
