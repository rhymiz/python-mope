"""Typed details for HTTP errors returned by the Mopé API."""

from typing import Self

from requests import HTTPError, Response

from mope.json import JsonValue, json_integer, json_object, json_string


class MopeAPIError(HTTPError):
    """An HTTP rejection, with validated Mopé error details when available."""

    response: Response | None

    def __init__(
        self,
        message: str,
        *,
        response: Response | None = None,
        code: int | None = None,
        data: JsonValue = None,
    ) -> None:
        super().__init__(message, response=response)
        self.message = message
        self.code = code
        self.data = data

    @property
    def status_code(self) -> int | None:
        return self.response.status_code if self.response is not None else None

    @classmethod
    def from_response(cls, response: Response, *, fallback_message: str) -> Self:
        try:
            payload = json_object(response.json())
            # The schema wraps details in "error"; documented examples are unwrapped.
            details = json_object(payload.get("error", payload), path="error")
            code = json_integer(details["code"], path="error.code")
            message = json_string(details["message"], path="error.message")
        except (TypeError, ValueError, KeyError):
            return cls(fallback_message, response=response)
        return cls(message, response=response, code=code, data=details.get("data"))


def raise_for_status(response: Response) -> None:
    """Preserve HTTPError compatibility without letting a bad error body mask it."""
    try:
        response.raise_for_status()
    except HTTPError as error:
        raise MopeAPIError.from_response(
            response, fallback_message=str(error)
        ) from error
