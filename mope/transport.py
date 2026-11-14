from typing import Protocol

from requests import Response


class ApiTransport(Protocol):
    """The HTTP operations required by API resources."""

    def call_api(
        self, method: str, endpoint: str, *, json: object = None
    ) -> Response: ...
