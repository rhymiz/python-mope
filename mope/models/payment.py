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
        return cls(data['id'], data['url'])


@dataclass
class Current(BaseModel):
    name: str
    code: str
    symbol: str

    @classmethod
    def from_json(cls, data: Dict[str, str]):
        return cls(data['name'], data['code'], data['symbol'])


@dataclass
class PaymentRequest(BaseModel):
    id: str
    amount: int
    created_at: str
    description: str
    expires_at: str
    currency: Current
    status: str
    meta_data: List[Dict[str, Any]]

    @classmethod
    def from_json(cls, data: Dict[str, Any]):
        return cls(data['id'], data['amount'], data['created_at'],
                   data['description'], data['expires_at'], Current.from_json(data['currency']),
                   data['status'], data['meta_data'])
