"""Independent, bounded finite Kripke-model testing of the public verifier.

The oracle below implements propositional forcing without importing kernel
rules, formula interners, or dependency calculations. Four small frames and
all persistent valuations of P and Q give 145 world/valuation observations.
An explicit two-world countermodel to excluded middle checks that implication
uses future worlds, rather than classical truth-table semantics.

The generated certificates exercise all ten rules and include changed
conclusions. For each accepted certificate, its reported retained premises
must semantically entail its goal in every observation. Rejected candidates
need not be logically invalid: this is a soundness check, not a completeness
check. Passing this finite sample is evidence, NOT a proof of general
soundness or correctness of the implementation.
"""

import itertools
import json
import random
import unittest

from lemqo import Rejection, verify_bytes


FRAMES = (
    ((0,),),
    ((0, 1), (1,)),
    ((0, 1, 2), (1, 2), (2,)),
    ((0, 1, 2), (1,), (2,)),
)
RULES = (
    "assume", "imp_intro", "imp_elim", "and_intro", "and_left",
    "and_right", "or_left", "or_right", "or_elim", "false_elim",
)
CASE_COUNT = 6_000


def forces(formula, world, frame, valuation):
    """Kripke forcing for the independent prefix-tree formula representation."""
    if isinstance(formula, str):
        return world in valuation[formula]
    connective = formula[0]
    if connective == "false":
        return False
    left, right = formula[1:]
    if connective == "and":
        return (forces(left, world, frame, valuation)
                and forces(right, world, frame, valuation))
    if connective == "or":
        return (forces(left, world, frame, valuation)
                or forces(right, world, frame, valuation))
    if connective == "imp":
        return all(
            not forces(left, future, frame, valuation)
            or forces(right, future, frame, valuation)
            for future in frame[world]
        )
    raise ValueError("unknown connective in test oracle")


def persistent_valuations(frame):
    """Enumerate upward-closed atom valuations on a finite reflexive frame."""
    subsets = (
        frozenset(world for world in range(len(frame)) if mask & (1 << world))
        for mask in range(1 << len(frame))
    )
    upsets = [
        subset for subset in subsets
        if all(set(frame[world]) <= subset for world in subset)
    ]
    for p_worlds, q_worlds in itertools.product(upsets, repeat=2):
        yield {"P": p_worlds, "Q": q_worlds}


def encode(document):
    return json.dumps(document, separators=(",", ":")).encode("utf-8")


def formula_fixture():
    """Thirty distinct formulas, with independently readable claim trees."""
    rows = [["atom", "P"], ["atom", "Q"], ["false"]]
    trees = ["P", "Q", ["false"]]
    groups = {}
    for connective in ("imp", "and", "or"):
        groups[connective] = []
        for left, right in itertools.product(range(3), repeat=2):
            groups[connective].append(len(rows))
            rows.append([connective, left, right])
            trees.append([connective, trees[left], trees[right]])
    return rows, trees, groups


def candidate(rule, rng, formulas, groups):
    """Build a rule application whose parents are explicit assumption steps."""
    conclusion = rng.randrange(len(formulas))
    parents = []
    if rule == "assume":
        pass
    elif rule == "imp_intro":
        conclusion = rng.choice(groups["imp"])
        parents = [formulas[conclusion][2]]
    elif rule == "imp_elim":
        function = rng.choice(groups["imp"])
        parents = [function, formulas[function][1]]
        conclusion = formulas[function][2]
    elif rule == "and_intro":
        conclusion = rng.choice(groups["and"])
        parents = formulas[conclusion][1:]
    elif rule in ("and_left", "and_right"):
        conjunction = rng.choice(groups["and"])
        parents = [conjunction]
        conclusion = formulas[conjunction][1 if rule == "and_left" else 2]
    elif rule in ("or_left", "or_right"):
        conclusion = rng.choice(groups["or"])
        parents = [formulas[conclusion][1 if rule == "or_left" else 2]]
    elif rule == "or_elim":
        parents = [rng.choice(groups["or"]), conclusion, conclusion]
    elif rule == "false_elim":
        parents = [2]
    else:
        raise ValueError("unknown rule in test generator")
    return [rule, conclusion] + parents


class FiniteKripkeTests(unittest.TestCase):
    def test_oracle_excluded_middle_countermodel(self):
        frame = FRAMES[1]
        valuation = {"P": frozenset((1,)), "Q": frozenset()}
        negation = ["imp", "P", ["false"]]
        excluded_middle = ["or", "P", negation]
        self.assertFalse(forces("P", 0, frame, valuation))
        self.assertFalse(forces(negation, 0, frame, valuation))
        self.assertFalse(forces(excluded_middle, 0, frame, valuation))
        self.assertTrue(forces(excluded_middle, 1, frame, valuation))
        self.assertFalse(forces(["false"], 1, frame, valuation))
        self.assertTrue(forces(["imp", "P", "P"], 0, frame, valuation))

    def test_generated_receipts_preserve_kripke_entailment(self):
        formulas, trees, groups = formula_fixture()
        observations = [
            tuple(forces(tree, world, frame, valuation) for tree in trees)
            for frame in FRAMES
            for valuation in persistent_valuations(frame)
            for world in range(len(frame))
        ]
        self.assertEqual(len(observations), 145)
        base_steps = [["assume", index] for index in range(len(formulas))]
        rng = random.Random(132311)
        accepted = dict.fromkeys(RULES, 0)
        rejected = 0
        for case_index in range(CASE_COUNT):
            rule = rng.choice(RULES)
            row = candidate(rule, rng, formulas, groups)
            if case_index % 2:
                row[1] = rng.randrange(len(formulas))
            claim = {
                "format": "lemqo-claim-v1", "logic": "ipl", "name": "finite-model",
                "premises": trees, "goal": trees[row[1]],
            }
            certificate = {
                "format": "lemqo-proof-v1", "logic": "ipl", "formulas": formulas,
                "steps": base_steps + [row], "root": len(base_steps),
            }
            try:
                receipt = verify_bytes(encode(claim), encode(certificate))
            except Rejection:
                rejected += 1
                continue
            accepted[rule] += 1
            self.assertEqual(receipt["goal"], claim["goal"])
            self.assertEqual(receipt["declared_premises"], trees)
            retained = receipt["used_premise_indices"]
            self.assertTrue(all(type(i) is int and 0 <= i < len(trees) for i in retained))
            self.assertEqual(len(retained), len(set(retained)))
            for truth in observations:
                self.assertTrue(
                    not all(truth[i] for i in retained) or truth[row[1]],
                    f"case {case_index}: {row!r}, retained={retained!r}, model={truth!r}",
                )
        for rule in RULES:
            with self.subTest(rule=rule, accepted=accepted[rule]):
                self.assertGreater(accepted[rule], 0)
        self.assertGreater(rejected, 0)
        self.assertEqual(sum(accepted.values()) + rejected, CASE_COUNT)


if __name__ == "__main__":
    unittest.main()
