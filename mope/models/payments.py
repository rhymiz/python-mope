from abc import abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass
class BaseModel:
    @classmethod
    @abstractmethod
    def from_json(cls, data: Dict[str, Any]):
        pass

    def as_dict(self):
        return asdict(self)


@dataclass
class CreatePaymentResponse(BaseModel):
    id: str
    url: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]):
        return cls(id=data['id'], url=data['url'])


@dataclass
class Currency(BaseModel):
    name: str
    code: str
    symbol: str

    @classmethod
    def from_json(cls, data: Dict[str, str]):
        return cls(
            name=data['name'],
            code=data['code'],
            symbol=data['symbol'],
        )


@dataclass
class PaymentRequest(BaseModel):
    id: str
    amount: int
    created_at: str
    description: str
    expires_at: str
    currency: Currency
    status: str
    meta_data: List[Dict[str, Any]]

    @classmethod
    def from_json(cls, data: Dict[str, Any]):
        return cls(
            id=data['id'],
            amount=data['amount'],
            created_at=data['created_at'],
            description=data['description'],
            expires_at=data['expires_at'],
            currency=Currency.from_json(data['currency']),
            status=data['status'],
            meta_data=data['meta_data'],
        )
