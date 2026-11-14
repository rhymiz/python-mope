from collections.abc import Iterable, Mapping, Set
from typing import IO, Protocol, TypeAlias
from urllib.parse import urljoin

import requests

from mope.__version__ import __version__
from mope.json import json_value
from mope.resources.shop import ShopResource

QueryScalar: TypeAlias = str | bytes | int | float
QueryValue: TypeAlias = QueryScalar | Iterable[QueryScalar] | None


class QueryItems(Protocol):
    def items(self) -> Set[tuple[QueryScalar, QueryValue]]: ...


QueryParams: TypeAlias = (
    QueryItems | Iterable[tuple[QueryScalar, QueryValue]] | str | bytes
)
RequestData: TypeAlias = (
    Mapping[str, object]
    | list[tuple[str, object]]
    | tuple[tuple[str, object], ...]
    | Iterable[bytes]
    | IO[str]
    | IO[bytes]
    | str
    | bytes
)

_user_agent = f"Python Mope {__version__}"


class Client:
    def __init__(self, token: str) -> None:
        self._token = token
        self._headers = {
            "User-Agent": _user_agent,
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        self._base_url = "https://api.mope.sr/api"

    def call_api(
        self,
        method: str,
        endpoint: str,
        params: QueryParams | None = None,
        data: RequestData | None = None,
        json: object = None,
    ) -> requests.Response:
        url = urljoin(self._base_url, endpoint)
        return requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json_value(json, path="request"),
            headers=self._headers,
        )


class Mope:
    def __init__(self, token: str) -> None:
        self._token = token
        self._headers = {
            "User-Agent": _user_agent,
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        self.base_url = "https://api.mope.sr/api"

        self._client = Client(token)

        self.shop = ShopResource(self._client)

    def __str__(self) -> str:
        return _user_agent
