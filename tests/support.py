import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def encoded(document):
    return json.dumps(document, separators=(",", ":")).encode("utf-8")


def claim(goal, premises=()):
    return {"format": "lemqo-claim-v1", "logic": "ipl", "name": "test",
            "premises": list(premises), "goal": goal}


def proof(formulas, steps, root=None):
    return {"format": "lemqo-proof-v1", "logic": "ipl", "formulas": formulas,
            "steps": steps, "root": len(steps) - 1 if root is None else root}


def example(name, suffix):
    return json.loads((ROOT / "examples" / f"{name}.{suffix}.json").read_bytes())


def conjunction_tree(count):
    """A balanced conjunction proof with count distinct open atom assumptions."""
    formulas, steps = [], []

    def tree(start, stop):
        if stop - start == 1:
            name = f"P{start}"
            f = len(formulas)
            formulas.append(["atom", name])
            s = len(steps)
            steps.append(["assume", f])
            return f, s, name
        mid = (start + stop) // 2
        left, ls, le = tree(start, mid)
        right, rs, re = tree(mid, stop)
        f = len(formulas)
        formulas.append(["and", left, right])
        s = len(steps)
        steps.append(["and_intro", f, ls, rs])
        return f, s, ["and", le, re]

    formula, step, expr = tree(0, count)
    return proof(formulas, steps), formula, step, expr
