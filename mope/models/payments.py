from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Literal, Self, TypeAlias, TypedDict

from mope.json import JsonValue, json_integer, json_object, json_string

CurrencyCode: TypeAlias = Literal["SRD", "EUR", "USD"]
PaymentStatus: TypeAlias = Literal["open", "scanned", "unconfirmed", "paid"]


class PaymentMetadata(TypedDict):
    key: str
    value: str


def _payment_status(value: object) -> PaymentStatus:
    match value:
        case "open":
            return "open"
        case "scanned":
            return "scanned"
        case "unconfirmed":
            return "unconfirmed"
        case "paid":
            return "paid"
        case _:
            raise ValueError("status must be open, scanned, unconfirmed, or paid")


def _payment_metadata(value: object) -> list[PaymentMetadata]:
    if not isinstance(value, list):
        raise TypeError("meta_data must be an array")
    result: list[PaymentMetadata] = []
    for index, entry in enumerate(value):
        path = f"meta_data[{index}]"
        item = json_object(entry, path=path)
        result.append(
            PaymentMetadata(
                key=json_string(item["key"], path=f"{path}.key"),
                value=json_string(item["value"], path=f"{path}.value"),
            )
        )
    return result


@dataclass
class BaseModel(ABC):
    @classmethod
    @abstractmethod
    def from_json(cls, data: object) -> Self:
        pass

    def as_dict(self) -> dict[str, JsonValue]:
        return json_object(asdict(self))


@dataclass
class CreatePaymentResponse(BaseModel):
    id: str
    url: str

    @classmethod
    def from_json(cls, data: object) -> Self:
        payload = json_object(data)
        return cls(
            id=json_string(payload["id"], path="id"),
            url=json_string(payload["url"], path="url"),
        )


@dataclass
class Currency(BaseModel):
    name: str
    code: str
    symbol: str

    @classmethod
    def from_json(cls, data: object) -> Self:
        payload = json_object(data, path="currency")
        return cls(
            name=json_string(payload["name"], path="currency.name"),
            code=json_string(payload["code"], path="currency.code"),
            symbol=json_string(payload["symbol"], path="currency.symbol"),
        )


@dataclass
class PaymentRequest(BaseModel):
    id: str
    amount: int
    created_at: str
    description: str
    expires_at: str
    currency: Currency
    status: PaymentStatus
    meta_data: list[PaymentMetadata]

    @classmethod
    def from_json(cls, data: object) -> Self:
        payload = json_object(data)
        return cls(
            id=json_string(payload["id"], path="id"),
            amount=json_integer(payload["amount"], path="amount"),
            created_at=json_string(payload["created_at"], path="created_at"),
            description=json_string(payload["description"], path="description"),
            expires_at=json_string(payload["expires_at"], path="expires_at"),
            currency=Currency.from_json(payload["currency"]),
            status=_payment_status(payload["status"]),
            meta_data=_payment_metadata(payload["meta_data"]),
        )
