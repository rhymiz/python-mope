from collections.abc import Iterable, Mapping, Set
from math import isfinite
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
RequestTimeout: TypeAlias = float | tuple[float, float]

_user_agent = f"Python Mope {__version__}"
_BASE_URL = "https://api.mope.sr/api/"
_DEFAULT_TIMEOUT = (5.0, 30.0)


def _timeout_seconds(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("timeout must contain numbers of seconds")
    try:
        seconds = float(value)
    except OverflowError as error:
        raise ValueError("timeout must be finite and greater than zero") from error
    if not isfinite(seconds) or seconds <= 0:
        raise ValueError("timeout must be finite and greater than zero")
    return seconds


def _request_timeout(value: object) -> RequestTimeout:
    if isinstance(value, tuple):
        if len(value) != 2:
            raise ValueError("timeout must be a (connect, read) pair")
        return (_timeout_seconds(value[0]), _timeout_seconds(value[1]))
    return _timeout_seconds(value)


class Client:
    def __init__(
        self, token: str, *, timeout: RequestTimeout = _DEFAULT_TIMEOUT
    ) -> None:
        self._timeout = _request_timeout(timeout)
        self._token = token
        self._headers = {
            "User-Agent": _user_agent,
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        self._base_url = _BASE_URL

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
            timeout=self._timeout,
        )


class Mope:
    def __init__(
        self, token: str, *, timeout: RequestTimeout = _DEFAULT_TIMEOUT
    ) -> None:
        self._token = token
        self._headers = {
            "User-Agent": _user_agent,
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        self.base_url = _BASE_URL

        self._client = Client(token, timeout=timeout)

        self.shop = ShopResource(self._client)

    def __str__(self) -> str:
        return _user_agent
