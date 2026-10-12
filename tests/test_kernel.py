import copy
import unittest

from lemqo import Rejection, verify_bytes
from tests.support import claim, conjunction_tree, encoded, example, proof


class KernelTests(unittest.TestCase):
    def verify(self, c, p):
        return verify_bytes(encoded(c), encoded(p))

    def reject(self, c, p, code=None):
        with self.assertRaises(Rejection) as caught:
            self.verify(c, p)
        if code:
            self.assertEqual(caught.exception.code, code)
        return str(caught.exception)

    def test_all_positive_examples(self):
        for name in ("identity", "composition", "conjunction", "disjunction",
                     "distributivity", "modus_ponens", "ex_falso"):
            with self.subTest(name=name):
                result = self.verify(example(name, "claim"), example(name, "proof"))
                self.assertEqual(result["status"], "valid")
                self.assertEqual(result["kind"], "conditional" if name == "modus_ponens" else "closed")

    def test_invalid_examples(self):
        self.reject(example("identity", "claim"), example("identity", "invalid.proof"), "inference")
        self.reject(example("false", "claim"), example("false", "invalid.proof"), "assumptions")

    def test_each_inference_rejects_wrong_shape(self):
        formulas = [["atom", "P"], ["atom", "Q"], ["false"], ["imp", 0, 1],
                    ["and", 0, 1], ["or", 0, 1]]
        prefix = [["assume", i] for i in range(len(formulas))]
        bad = [
            ["imp_intro", 4, 1], ["imp_elim", 1, 0, 1], ["and_intro", 0, 0, 1],
            ["and_left", 0, 0], ["and_right", 0, 4], ["or_left", 5, 1],
            ["or_right", 5, 0], ["or_elim", 0, 5, 0, 1], ["false_elim", 1, 0],
        ]
        for row in bad:
            with self.subTest(rule=row[0]):
                self.reject(claim("P"), proof(formulas, prefix + [row]), "inference")

    def test_vacuous_discharge_is_valid(self):
        p = proof([["atom", "P"], ["atom", "Q"], ["imp", 1, 1], ["imp", 0, 2]],
                  [["assume", 1], ["imp_intro", 2, 0], ["imp_intro", 3, 1]])
        self.verify(claim(["imp", "P", ["imp", "Q", "Q"]]), p)

    def test_shared_assumption_not_mutated_by_discharge(self):
        p = proof([["atom", "P"], ["imp", 0, 0], ["and", 0, 1]],
                  [["assume", 0], ["imp_intro", 1, 0], ["and_intro", 2, 0, 1]])
        goal = ["and", "P", ["imp", "P", "P"]]
        self.reject(claim(goal), p, "assumptions")
        self.assertEqual(self.verify(claim(goal, ["P"]), p)["used_premise_indices"], [0])

    def test_or_elimination_retains_other_branch_assumption(self):
        p = proof([["atom", "P"], ["atom", "Q"], ["or", 0, 1]],
                  [["assume", 2], ["assume", 0], ["or_elim", 0, 0, 1, 1]])
        self.reject(claim("P", [["or", "P", "Q"]]), p, "assumptions")
        result = self.verify(claim("P", [["or", "P", "Q"], "P"]), p)
        self.assertEqual(result["used_premise_indices"], [0, 1])

    def test_or_elimination_keeps_source_assumptions(self):
        p = proof([["atom", "P"], ["atom", "Q"], ["or", 0, 1]],
                  [["assume", 0], ["or_left", 2, 0], ["or_elim", 0, 1, 0, 0]])
        self.reject(claim("P"), p, "assumptions")

    def test_identical_disjuncts_are_permitted(self):
        p = proof([["atom", "P"], ["or", 0, 0]],
                  [["assume", 1], ["assume", 0], ["or_elim", 0, 0, 1, 1]])
        self.verify(claim("P", [["or", "P", "P"]]), p)

    def test_structural_aliases_are_canonical(self):
        p = proof([["atom", "P"], ["atom", "P"], ["and", 0, 1],
                   ["and", 1, 0], ["imp", 3, 2]],
                  [["assume", 2], ["imp_intro", 4, 0]])
        self.verify(claim(["imp", ["and", "P", "P"], ["and", "P", "P"]]), p)

    def test_claim_and_certificate_ids_are_independent(self):
        p = example("conjunction", "proof")
        self.verify(example("conjunction", "claim"), p)
        c = example("conjunction", "claim")
        c["premises"] = ["Fresh"]
        self.assertEqual(self.verify(c, p)["used_premise_indices"], [])

    def test_goal_replacement_rejected(self):
        p = example("identity", "proof")
        for goal in ("P", ["false"], ["imp", "Q", "Q"], ["imp", "P", "Q"]):
            with self.subTest(goal=goal):
                self.reject(claim(goal), p, "goal")

    def test_false_premise_is_conditional_only(self):
        p = proof([["false"], ["atom", "P"]], [["assume", 0], ["false_elim", 1, 0]])
        result = self.verify(claim("P", [["false"]]), p)
        self.assertEqual(result["kind"], "conditional")
        self.assertEqual(result["used_premise_indices"], [0])
        self.reject(claim("P"), p, "assumptions")

    def test_atom_spelling_does_not_define_false(self):
        p = proof([["atom", "false"]], [["assume", 0]])
        self.verify(claim("false", ["false"]), p)
        self.reject(claim(["false"], ["false"]), p, "goal")

    def test_duplicate_premises_rejected(self):
        self.reject(claim(["imp", "P", "P"], ["Q", "Q"]), example("identity", "proof"), "schema")

    def test_bad_root_indices(self):
        for value in (True, False, -1, 2, "1", None):
            p = example("identity", "proof")
            p["root"] = value
            with self.subTest(value=value):
                self.reject(example("identity", "claim"), p, "reference")

    def test_bad_formula_indices(self):
        for value in (True, False, -1, 1, 99, "0", None):
            p = example("identity", "proof")
            p["formulas"][1][1] = value
            with self.subTest(value=value):
                self.reject(example("identity", "claim"), p, "reference")

    def test_bad_step_indices(self):
        for value in (True, False, -1, 1, 99, "0", None):
            p = example("identity", "proof")
            p["steps"][1][2] = value
            with self.subTest(value=value):
                self.reject(example("identity", "claim"), p, "reference")

    def test_all_steps_checked_even_after_root(self):
        p = example("identity", "proof")
        p["steps"].append(["false_elim", 0, 0])
        self.reject(example("identity", "claim"), p, "inference")

    def test_all_formulas_checked_even_unused(self):
        p = example("identity", "proof")
        p["formulas"].append(["imp", 999, 0])
        self.reject(example("identity", "claim"), p, "reference")

    def test_selected_root_need_not_be_last(self):
        p = example("identity", "proof")
        p["steps"].append(["assume", 0])
        self.verify(example("identity", "claim"), p)

    def test_exact_schema_and_versions(self):
        c, p = example("identity", "claim"), example("identity", "proof")
        for target, key, value in (("proof", "axioms", []), ("claim", "definitions", {}),
                                   ("proof", "logic", "classical"), ("claim", "format", "lemqo-claim-v2")):
            cc, pp = copy.deepcopy(c), copy.deepcopy(p)
            (cc if target == "claim" else pp)[key] = value
            with self.subTest(key=key):
                self.reject(cc, pp, "schema")

    def test_rule_and_formula_arity(self):
        for row in (["sorry", 1], ["assume", 0, 0], ["imp_intro", 1], ["imp_intro", 1, 0, []]):
            p = example("identity", "proof")
            p["steps"][1] = row
            self.reject(example("identity", "claim"), p, "schema")
        for row in (["false", 0], ["atom", "P", 0], ["not", 0], ["imp", 0]):
            p = example("identity", "proof")
            p["formulas"][1] = row
            self.reject(example("identity", "claim"), p, "schema")

    def test_claim_formula_shape_and_atom_policy(self):
        for goal in (True, 0, None, {}, [], ["atom", "P"], ["false", 1],
                     ["imp", "P"], ["and", "P", "P", "P"], "", "é", "P Q", "P\n", "P" * 65):
            with self.subTest(goal=goal):
                self.reject(claim(goal), example("identity", "proof"), "schema")

    def test_context_size_bound(self):
        p, _, _, goal = conjunction_tree(257)
        message = self.reject(claim(goal), p, "limit")
        self.assertIn("context is too large", message)

    def test_cumulative_context_work_bound(self):
        p, f, s, expr = conjunction_tree(128)
        left = p["formulas"][f][1]
        p["steps"].extend([["and_left", left, s]] * 1556)
        p["root"] = len(p["steps"]) - 1
        self.assertIn("memberships", self.reject(claim(expr[1]), p, "limit"))

    def test_shared_formula_dag_is_not_expanded(self):
        p = example("identity", "proof")
        previous = 0
        for _ in range(63):
            p["formulas"].append(["and", previous, previous])
            previous = len(p["formulas"]) - 1
        result = self.verify(example("identity", "claim"), p)
        self.assertLess(len(encoded(result)), 1000)
        p["formulas"].append(["and", previous, previous])
        self.reject(example("identity", "claim"), p, "limit")

    def test_formula_step_and_claim_limits(self):
        p = example("identity", "proof")
        p["formulas"] = [["atom", "P"]] * 10001
        self.reject(example("identity", "claim"), p, "limit")
        p = example("identity", "proof")
        p["steps"] = [["assume", 0]] * 20001
        self.reject(example("identity", "claim"), p, "limit")
        c = example("identity", "claim")
        c["premises"] = [f"P{i}" for i in range(257)]
        self.reject(c, example("identity", "proof"), "limit")

    def test_claim_tree_occurrence_and_depth_limits(self):
        def tree(leaves):
            if leaves == 1:
                return "P"
            left = leaves // 2
            return ["and", tree(left), tree(leaves - left)]

        # 5,001 leaves give 10,001 occurrences; interning cannot hide them.
        message = self.reject(claim(tree(5001)), example("identity", "proof"), "limit")
        self.assertIn("claim formula occurrences", message)
        deep = "P"
        for _ in range(64):
            deep = ["imp", "P", deep]
        message = self.reject(claim(deep), example("identity", "proof"), "limit")
        self.assertIn("too deep", message)

    def test_receipt_identifies_exact_inputs(self):
        import hashlib
        c, p = encoded(example("identity", "claim")), encoded(example("identity", "proof"))
        result = verify_bytes(c, p)
        self.assertEqual(result["claim_sha256"], hashlib.sha256(c).hexdigest())
        self.assertEqual(result["proof_sha256"], hashlib.sha256(p).hexdigest())
        other = verify_bytes(c + b"\n", p)
        self.assertNotEqual(other["claim_sha256"], result["claim_sha256"])
        self.assertEqual(other["goal"], result["goal"])
