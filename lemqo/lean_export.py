"""Strict, streamed preflight for the supported lean4export NDJSON subset.

This checks representation, not mathematical validity. Nanoda must check every
declaration and the binding bridge must compare against a trusted reference.
"""

import hashlib
import json
import re
import time

from .errors import Rejection
from .input import _object, _not_integer

MAX_EXPORT_BYTES = 4 * 1024**3
MAX_LINE_BYTES = 4 * 1024**2
MAX_RECORDS = 50_000_000
MAX_NAMES = 1_000_000
MAX_NAME_CHARACTERS = 64 * 1024**2
AXIOMS = ("propext", "Classical.choice", "Quot.sound")
LEAN_VERSION = "4.34.1"
LEAN_GITHASH = "5045d0056413266e57c625dcd7c365b10e377c52"
EXPORT_VERSION = "3.1.0"
TARGET_NAME = re.compile(r"[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*")


def _integer(token):
    if not token.isascii() or not token.isdecimal() or len(token) > 20:
        raise Rejection("lean-json", "expected a bounded nonnegative JSON integer")
    value = int(token)
    if value >= 2**64:
        raise Rejection("lean-json", "JSON integer exceeds uint64")
    return value


def load_json(data):
    """Bound containers before decoding; reject duplicate keys and nonintegers."""
    if len(data) > MAX_LINE_BYTES:
        raise Rejection("lean-limit", "JSON record exceeds the byte limit")
    try:
        text = data.decode("utf-8", errors="strict")
        depth, quoted, escaped = 0, False, False
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
                if depth > 16:
                    raise Rejection("lean-limit", "JSON nesting exceeds 16 containers")
            elif char in "]}":
                depth -= 1
        result = json.loads(text, object_pairs_hook=_object, parse_int=_integer,
                            parse_float=_not_integer, parse_constant=_not_integer)
        pending = [result]
        while pending:
            value = pending.pop()
            if type(value) is str:
                value.encode("utf-8", errors="strict")
            elif type(value) is list:
                pending.extend(value)
            elif type(value) is dict:
                pending.extend(value.keys())
                pending.extend(value.values())
        return result
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        raise Rejection("lean-json", "invalid strict UTF-8 JSON record") from None


def fields(value, keys):
    if type(value) is not dict or value.keys() != set(keys.split()):
        raise Rejection("lean-format", "object has missing or unexpected fields")


def uint(value, maximum=2**32 - 1):
    if type(value) is not int or not 0 <= value <= maximum:
        raise Rejection("lean-format", "expected an unsigned integer in range")


def array(value):
    if type(value) is not list:
        raise Rejection("lean-format", "expected an array")


def safe(value):
    if value is not False:
        raise Rejection("lean-unsafe", "unsafe declarations are not supported")


def names(value, *, empty=False):
    array(value)
    if not empty and not value:
        raise Rejection("lean-claim", "theorem targets must not be empty")
    if len(value) > 32 or any(type(n) is not str or not TARGET_NAME.fullmatch(n)
                             or len(n) > 256 for n in value):
        raise Rejection("lean-claim", "expected at most 32 canonical theorem names")
    if len(set(value)) != len(value):
        raise Rejection("lean-claim", "duplicate names")


def deadline_check(deadline):
    if deadline is not None and time.monotonic() >= deadline:
        raise Rejection("lean-timeout", "verification deadline exceeded")


class _Export:
    def __init__(self):
        self.names = [""]       # anonymous Name and zero Level are implicit
        self.levels = 1
        self.expressions = 0
        self.name_characters = 0
        self.declarations = {}
        self.axioms = []

    def index(self, value, size):
        uint(value)
        if value >= size:
            raise Rejection("lean-format", "DAG index is not an existing back-reference")

    def name(self, value):
        self.index(value, len(self.names))

    def expr(self, value):
        self.index(value, self.expressions)

    def level(self, value):
        self.index(value, self.levels)

    def many(self, values, validator):
        array(values)
        for value in values:
            validator(value)

    def declaration(self, value, kind):
        keys = "name levelParams type"
        additions = {
            "axiom": "isUnsafe", "thm": "value all", "def": "value all hints safety",
            "opaque": "value all isUnsafe", "quot": "kind",
            "ind": "all ctors numParams numIndices numNested isRec isReflexive isUnsafe",
            "ctor": "induct cidx numParams numFields isUnsafe",
            "rec": "all numParams numIndices numMotives numMinors rules k isUnsafe",
        }
        fields(value, keys + " " + additions[kind])
        self.name(value["name"])
        self.many(value["levelParams"], self.name)
        self.expr(value["type"])
        n = value["name"]
        if n == 0 or n in self.declarations:
            raise Rejection("lean-format", "empty or duplicate declaration name")
        self.declarations[n] = kind
        if "value" in value:
            self.expr(value["value"])
        if "all" in value:
            self.many(value["all"], self.name)
        if "isUnsafe" in value:
            safe(value["isUnsafe"])
        if kind == "axiom":
            self.axioms.append(self.names[n])
        if kind == "def":
            if value["safety"] != "safe":
                raise Rejection("lean-unsafe", "unsafe or partial definition")
            hint = value["hints"]
            if hint not in ("opaque", "abbrev"):
                fields(hint, "regular")
                uint(hint["regular"])
        if kind == "quot" and value["kind"] not in ("type", "ctor", "lift", "ind"):
            raise Rejection("lean-format", "unknown quotient kind")
        if kind == "ind":
            self.many(value["ctors"], self.name)
            for key in ("isRec", "isReflexive"):
                if type(value[key]) is not bool:
                    raise Rejection("lean-format", "expected a Boolean inductive flag")
        if kind == "ctor":
            self.name(value["induct"])
        if kind == "rec":
            if type(value["k"]) is not bool:
                raise Rejection("lean-format", "expected a Boolean recursor flag")
            array(value["rules"])
            for rule in value["rules"]:
                fields(rule, "ctor nfields rhs")
                self.name(rule["ctor"])
                uint(rule["nfields"], 65535)
                self.expr(rule["rhs"])
        for key in ("numParams", "numIndices", "numNested", "cidx", "numFields",
                    "numMotives", "numMinors"):
            if key in value:
                uint(value[key], 65535)

    def record(self, record):
        if type(record) is not dict:
            raise Rejection("lean-format", "export records must be objects")
        tags = set(record) - {"in", "il", "ie"}
        if len(tags) != 1:
            raise Rejection("lean-format", "expected exactly one record tag")
        tag = tags.pop()
        value = record[tag]
        if tag in ("str", "num"):
            fields(record, tag + " in")
            uint(record["in"])
            if record["in"] != len(self.names) or len(self.names) >= MAX_NAMES:
                raise Rejection("lean-format", "noncontinuous or excessive name index")
            fields(value, "pre " + ("str" if tag == "str" else "i"))
            self.name(value["pre"])
            if tag == "str":
                suffix = value["str"]
                if type(suffix) is not str or not suffix or len(suffix) > 4096:
                    raise Rejection("lean-format", "invalid name component")
                # None represents a name that cannot equal our canonical targets.
                if "." in suffix:
                    suffix = None
            else:
                uint(value["i"])
                suffix = None  # numeric names cannot be user-selected theorem targets
            pre = self.names[value["pre"]]
            name = None if pre is None or suffix is None else (pre + "." if pre else "") + suffix
            self.name_characters += len(name) if name else 0
            if (name and len(name) > 4096) or self.name_characters > MAX_NAME_CHARACTERS:
                raise Rejection("lean-limit", "exported names exceed memory limits")
            self.names.append(name)
        elif tag in ("succ", "max", "imax", "param"):
            fields(record, tag + " il")
            uint(record["il"])
            if record["il"] != self.levels:
                raise Rejection("lean-format", "noncontinuous universe index")
            if tag in ("max", "imax"):
                array(value)
                if len(value) != 2:
                    raise Rejection("lean-format", "universe pair must have two elements")
                self.many(value, self.level)
            else:
                (self.name if tag == "param" else self.level)(value)
            self.levels += 1
        elif tag in ("bvar", "natVal", "strVal", "sort", "const", "app", "lam", "forallE", "letE", "proj"):
            fields(record, tag + " ie")
            uint(record["ie"])
            if record["ie"] != self.expressions:
                raise Rejection("lean-format", "noncontinuous expression index")
            if tag == "bvar":
                uint(value, 65534)  # the checker uses u16 for bvar counts, including +1
            elif tag == "natVal":
                if type(value) is not str or not value.isascii() or not value.isdecimal():
                    raise Rejection("lean-format", "natural literal must be a decimal string")
                if len(value) > 100_000 or (len(value) > 1 and value[0] == "0"):
                    raise Rejection("lean-limit", "natural literal exceeds the supported subset")
            elif tag == "strVal":
                if type(value) is not str:
                    raise Rejection("lean-format", "string literal must be a string")
            elif tag == "sort":
                self.level(value)
            else:
                keys = {"const": "name us", "app": "fn arg", "lam": "name type body binderInfo",
                        "forallE": "name type body binderInfo", "letE": "name type value body nondep",
                        "proj": "typeName idx struct"}
                fields(value, keys[tag])
                for key in ("name", "typeName"):
                    if key in value:
                        self.name(value[key])
                for key in ("fn", "arg", "type", "body", "value", "struct"):
                    if key in value:
                        self.expr(value[key])
                if tag == "const":
                    self.many(value["us"], self.level)
                if tag in ("lam", "forallE") and value["binderInfo"] not in ("default", "implicit", "strictImplicit", "instImplicit"):
                    raise Rejection("lean-format", "unknown binder annotation")
                if tag == "letE" and type(value["nondep"]) is not bool:
                    raise Rejection("lean-format", "expected a Boolean let annotation")
                if tag == "proj":
                    uint(value["idx"])
            self.expressions += 1
        elif tag in ("axiom", "thm", "def", "opaque", "quot", "inductive"):
            fields(record, tag)
            if tag == "inductive":
                fields(value, "types ctors recs")
                for key, kind in (("types", "ind"), ("ctors", "ctor"), ("recs", "rec")):
                    array(value[key])
                    for item in value[key]:
                        self.declaration(item, kind)
            else:
                self.declaration(value, tag)
        else:
            raise Rejection("lean-format", "unsupported export record tag")


def inspect_export(path, targets, permitted_axioms, *, reference=False, deadline=None):
    """Preflight exact bytes; never infer logical success from this result."""
    state = _Export()
    digest = hashlib.sha256()
    total, records = 0, 0
    with path.open("rb") as stream:
        while line := stream.readline(MAX_LINE_BYTES + 1):
            total += len(line)
            digest.update(line)
            if len(line) > MAX_LINE_BYTES or total > MAX_EXPORT_BYTES or records >= MAX_RECORDS:
                raise Rejection("lean-limit", "export exceeds the fixed resource limits")
            deadline_check(deadline)
            record = load_json(line)
            if records == 0:
                fields(record, "meta")
                meta = record["meta"]
                fields(meta, "lean exporter format")
                fields(meta["lean"], "version githash")
                fields(meta["exporter"], "name version")
                fields(meta["format"], "version")
                expected = {"lean": {"version": LEAN_VERSION, "githash": LEAN_GITHASH},
                            "exporter": {"name": "lean4export", "version": EXPORT_VERSION},
                            "format": {"version": EXPORT_VERSION}}
                if meta != expected:
                    raise Rejection("lean-version", "unsupported Lean or export metadata")
            else:
                state.record(record)
            records += 1
    if not state.declarations:
        raise Rejection("lean-format", "export has no declarations")
    deadline_check(deadline)
    kinds = {state.names[n]: kind for n, kind in state.declarations.items() if state.names[n] is not None}
    if any(kinds.get(n) != "thm" for n in targets):
        raise Rejection("lean-target", "a selected theorem is missing or is not a theorem")
    if any(kinds.get(n) != "axiom" for n in permitted_axioms):
        raise Rejection("lean-axiom", "a permitted axiom is missing or has the wrong kind")
    legal = set(permitted_axioms) | ({"sorryAx"} if reference else set())
    if any(n not in legal for n in state.axioms):
        raise Rejection("lean-axiom", "export contains an unpermitted axiom")
    return {"sha256": digest.hexdigest(), "bytes": total, "records": records,
            "declarations": len(state.declarations), "expressions": state.expressions,
            "names": len(state.names), "levels": state.levels, "axioms": sorted(state.axioms)}
