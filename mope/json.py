"""JSON types and validation at the API boundary."""

from math import isfinite
from typing import TypeAlias

JsonValue: TypeAlias = (
    str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
)
JsonObject: TypeAlias = dict[str, JsonValue]


def json_value(value: object, *, path: str = "response") -> JsonValue:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not isfinite(value):
            raise ValueError(f"{path} must contain a finite JSON number")
        return value
    if isinstance(value, list):
        return [
            json_value(item, path=f"{path}[{index}]")
            for index, item in enumerate(value)
        ]
    if isinstance(value, dict):
        return json_object(value, path=path)
    raise TypeError(f"{path} must be a JSON value")


def json_object(value: object, *, path: str = "response") -> JsonObject:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be a JSON object")
    result: JsonObject = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise TypeError(f"{path} must have string keys")
        result[key] = json_value(item, path=f"{path}.{key}")
    return result


def json_string(value: object, *, path: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{path} must be a string")
    return value


def json_integer(value: object, *, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{path} must be an integer")
    return value
