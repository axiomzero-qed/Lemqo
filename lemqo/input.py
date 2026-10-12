"""Bounded, strict UTF-8 JSON ingestion. This is part of the trusted boundary."""

import json

from .errors import Rejection
from .limits import (
    MAX_FILE_BYTES,
    MAX_INTEGER_DIGITS,
    MAX_JSON_DEPTH,
    MAX_JSON_VALUES,
    MAX_STRING_LENGTH,
)


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Rejection("json", "duplicate object key")
        result[key] = value
    return result


def _integer(token):
    if len(token.lstrip("-")) > MAX_INTEGER_DIGITS:
        raise Rejection("limit", "JSON integer is too long")
    # Negative zero has no meaning in either format; reject its alias spelling.
    if token == "-0":
        raise Rejection("json", "negative zero is not supported")
    return int(token)


def _not_integer(_token):
    raise Rejection("json", "only integer JSON numbers are supported")


def _depth_guard(text):
    """Count containers outside strings before the recursive JSON decoder runs."""
    depth = 0
    quoted = False
    escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > MAX_JSON_DEPTH:
                raise Rejection("limit", "JSON nesting exceeds the limit")
        elif char in "]}":
            depth -= 1
    # Balanced brackets, escaping, and all other grammar are checked by json.


def decode(data: bytes):
    """Decode one document, rejecting ambiguous JSON and bounded resource abuse."""
    if type(data) is not bytes:
        raise TypeError("verify_bytes requires bytes")
    if len(data) > MAX_FILE_BYTES:
        raise Rejection("limit", "file exceeds the byte limit")
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise Rejection("json", "input must be strict UTF-8") from None
    _depth_guard(text)
    try:
        document = json.loads(
            text,
            object_pairs_hook=_object,
            parse_int=_integer,
            parse_float=_not_integer,
            parse_constant=_not_integer,
        )
    except (json.JSONDecodeError, RecursionError):
        raise Rejection("json", "invalid JSON document") from None
    pending = [document]
    count = 0
    while pending:
        value = pending.pop()
        count += 1
        if count > MAX_JSON_VALUES:
            raise Rejection("limit", "too many JSON values")
        if type(value) is dict:
            pending.extend(value.keys())
            pending.extend(value.values())
        elif type(value) is list:
            pending.extend(value)
        elif type(value) is str:
            if len(value) > MAX_STRING_LENGTH:
                raise Rejection("limit", "JSON string exceeds the limit")
            if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
                raise Rejection("json", "unpaired Unicode surrogate")
    return document
