"""The fixed IPL rule checker and structural claim binding.

Invariant: every stored (conclusion, context) is a derivable sequent.
Contexts are immutable sets of canonical FORMULAS, not proof-node identifiers.
No file I/O, search, evaluation, axioms, imports, or user extensions occur here.
"""

import re

from .errors import Rejection
from .limits import (
    MAX_CLAIM_NODES,
    MAX_CONTEXT,
    MAX_CONTEXT_MEMBERSHIPS,
    MAX_FORMULA_DEPTH,
    MAX_FORMULAS,
    MAX_PREMISES,
    MAX_STEPS,
)

ATOM = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,63}", re.ASCII)
NAME = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,63}", re.ASCII)
BINARY = ("imp", "and", "or")
# Total row length, including rule name and explicit conclusion formula ID.
ARITIES = {
    "assume": 2, "imp_intro": 3, "imp_elim": 4,
    "and_intro": 4, "and_left": 3, "and_right": 3,
    "or_left": 3, "or_right": 3, "or_elim": 5, "false_elim": 3,
}


def _require(condition, code, message):
    if not condition:
        raise Rejection(code, message)


def _fields(value, expected, label):
    _require(type(value) is dict and set(value) == set(expected),
             "schema", f"{label}: exact fields required")


def _index(value, bound, label):
    _require(type(value) is int and 0 <= value < bound,
             "reference", f"{label}: index must reference an existing earlier item")
    return value


def _atom(value):
    _require(type(value) is str and ATOM.fullmatch(value) is not None,
             "schema", "atom must be an ASCII identifier of 1 to 64 characters")
    return value


class _Formulas:
    """Exact hash-consing: full tuple equality, never digest equality.

    Node keys contain canonical child IDs, so even shared exponential DAGs
    can be compared without recursively expanding their trees.
    """

    def __init__(self):
        self.nodes = []
        self.depths = []
        self.ids = {}
        self.claim_nodes = 0

    def intern(self, key):
        depth = 1 if key[0] in ("atom", "false") else (
            1 + max(self.depths[key[1]], self.depths[key[2]]))
        _require(depth <= MAX_FORMULA_DEPTH, "limit", "formula depth exceeds the limit")
        if key not in self.ids:
            self.ids[key] = len(self.nodes)
            self.nodes.append(key)
            self.depths.append(depth)
        return self.ids[key]

    def expression(self, expr, depth=1):
        """Claim trees only; recursion is guarded before descent."""
        self.claim_nodes += 1
        _require(self.claim_nodes <= MAX_CLAIM_NODES,
                 "limit", "too many claim formula occurrences")
        _require(depth <= MAX_FORMULA_DEPTH, "limit", "claim formula is too deep")
        if type(expr) is str:
            return self.intern(("atom", _atom(expr)))
        _require(type(expr) is list and len(expr) > 0 and type(expr[0]) is str,
                 "schema", "invalid claim formula")
        if expr == ["false"]:
            return self.intern(("false",))
        _require(expr[0] in BINARY and len(expr) == 3,
                 "schema", "invalid claim connective or arity")
        left = self.expression(expr[1], depth + 1)
        right = self.expression(expr[2], depth + 1)
        return self.intern((expr[0], left, right))

    def table(self, rows):
        _require(type(rows) is list and 1 <= len(rows) <= MAX_FORMULAS,
                 "limit", "formula table must contain 1 to 10000 rows")
        mapping = []
        for i, row in enumerate(rows):
            _require(type(row) is list and len(row) > 0 and type(row[0]) is str,
                     "schema", f"formula {i}: invalid row")
            tag = row[0]
            if tag == "atom" and len(row) == 2:
                key = (tag, _atom(row[1]))
            elif tag == "false" and len(row) == 1:
                key = (tag,)
            else:
                _require(tag in BINARY and len(row) == 3,
                         "schema", f"formula {i}: invalid connective or arity")
                left = mapping[_index(row[1], i, f"formula {i}")]
                right = mapping[_index(row[2], i, f"formula {i}")]
                key = (tag, left, right)
            mapping.append(self.intern(key))
        return mapping


def check(claim, certificate):
    """Check decoded documents. All schema, rule, and claim checks occur here.

    External callers should use verify_bytes, which also checks byte-level JSON.
    Returns used premise indices (not a claim about their truth or consistency).
    """
    _fields(claim, ("format", "logic", "name", "premises", "goal"), "claim")
    _fields(certificate, ("format", "logic", "formulas", "steps", "root"), "proof")
    _require(claim["format"] == "lemqo-claim-v1" and
             certificate["format"] == "lemqo-proof-v1", "schema", "unsupported format")
    _require(claim["logic"] == certificate["logic"] == "ipl",
             "schema", "only fixed logic 'ipl' is supported")
    _require(type(claim["name"]) is str and NAME.fullmatch(claim["name"]) is not None,
             "schema", "claim name must be an ASCII identifier")
    premises = claim["premises"]
    _require(type(premises) is list and len(premises) <= MAX_PREMISES,
             "limit", "premises must be a list with at most 256 formulas")
    formulas = _Formulas()
    goal = formulas.expression(claim["goal"])
    allowed = [formulas.expression(p) for p in premises]
    _require(len(set(allowed)) == len(allowed), "schema", "duplicate claim premise")
    mapping = formulas.table(certificate["formulas"])
    rows = certificate["steps"]
    _require(type(rows) is list and 1 <= len(rows) <= MAX_STEPS,
             "limit", "proof must contain 1 to 20000 steps")
    root = _index(certificate["root"], len(rows), "root")
    judgments = []
    memberships = 0
    for i, row in enumerate(rows):
        _require(type(row) is list and len(row) >= 2 and type(row[0]) is str,
                 "schema", f"step {i}: invalid row")
        rule = row[0]
        _require(rule in ARITIES and len(row) == ARITIES[rule],
                 "schema", f"step {i}: unknown rule or wrong arity")
        conclusion = mapping[_index(row[1], len(mapping), f"step {i} conclusion")]
        node = formulas.nodes[conclusion]
        parents = [judgments[_index(ref, i, f"step {i}")] for ref in row[2:]]
        good = True
        if rule == "assume":
            context = frozenset((conclusion,))
        elif rule == "imp_intro":
            source, deps = parents[0]
            good = node[0] == "imp" and node[2] == source
            context = deps - frozenset((node[1],)) if good else frozenset()
        elif rule == "imp_elim":
            function, left = parents[0]
            argument, right = parents[1]
            good = formulas.nodes[function] == ("imp", argument, conclusion)
            context = left | right
        elif rule == "and_intro":
            left, ldeps = parents[0]
            right, rdeps = parents[1]
            good = node == ("and", left, right)
            context = ldeps | rdeps
        elif rule in ("and_left", "and_right"):
            source, context = parents[0]
            pair = formulas.nodes[source]
            position = 1 if rule == "and_left" else 2
            good = pair[0] == "and" and pair[position] == conclusion
        elif rule in ("or_left", "or_right"):
            source, context = parents[0]
            position = 1 if rule == "or_left" else 2
            good = node[0] == "or" and node[position] == source
        elif rule == "or_elim":
            disjunction, ddeps = parents[0]
            left, ldeps = parents[1]
            right, rdeps = parents[2]
            choice = formulas.nodes[disjunction]
            good = choice[0] == "or" and left == right == conclusion
            context = (ddeps | (ldeps - frozenset((choice[1],))) |
                       (rdeps - frozenset((choice[2],)))) if good else frozenset()
        else:  # false_elim is the only remaining rule in the exact arity table.
            source, context = parents[0]
            good = formulas.nodes[source] == ("false",)
        _require(good, "inference", f"step {i}: {rule} does not derive its conclusion")
        _require(len(context) <= MAX_CONTEXT, "limit", f"step {i}: context is too large")
        memberships += len(context)
        _require(memberships <= MAX_CONTEXT_MEMBERSHIPS,
                 "limit", "total context memberships exceed the limit")
        judgments.append((conclusion, context))
    result, context = judgments[root]
    _require(result == goal, "goal", "root conclusion differs from the supplied claim")
    _require(context <= frozenset(allowed), "assumptions", "root has undeclared open assumptions")
    return [i for i, premise in enumerate(allowed) if premise in context]
