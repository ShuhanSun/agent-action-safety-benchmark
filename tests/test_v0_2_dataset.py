from __future__ import annotations

import importlib.util
import unittest
from collections import Counter, defaultdict
from pathlib import Path

from actionguardbench.models import BenchmarkCase


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate_v0_2.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_v0_2", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load v0.2 generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class V02DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = load_generator()
        cls.cases = cls.generator.generate_cases()
        cls.generator.validate(cls.cases)

    def test_expected_size_and_balance(self):
        self.assertEqual(len(self.cases), 360)
        self.assertEqual(
            Counter(case["expected_decision"] for case in self.cases),
            Counter({"ALLOW": 120, "ASK": 120, "BLOCK": 120}),
        )
        self.assertEqual(
            Counter(case["split"] for case in self.cases),
            Counter({"train": 216, "dev": 72, "test": 72}),
        )

    def test_families_do_not_cross_splits(self):
        family_splits = defaultdict(set)
        for case in self.cases:
            family_splits[case["family_id"]].add(case["split"])
        self.assertEqual(len(family_splits), 30)
        self.assertTrue(all(len(splits) == 1 for splits in family_splits.values()))

    def test_each_family_has_counterfactual_decisions(self):
        family_labels = defaultdict(set)
        for case in self.cases:
            family_labels[case["family_id"]].add(case["expected_decision"])
        self.assertTrue(
            all(labels == {"ALLOW", "ASK", "BLOCK"} for labels in family_labels.values())
        )

    def test_model_inputs_never_expose_annotation_fields(self):
        annotation_only = {
            "expected_decision",
            "severity",
            "risk_tags",
            "rationale",
            "family_id",
            "category",
            "split",
            "variant_index",
        }
        case = BenchmarkCase.from_dict(self.cases[0])
        for condition in ("action", "intent", "provenance", "full"):
            payload = case.model_input(condition)
            self.assertTrue(annotation_only.isdisjoint(payload.keys()))

    def test_ablation_inputs_are_monotonic(self):
        case = BenchmarkCase.from_dict(self.cases[0])
        action = case.model_input("action")
        intent = case.model_input("intent")
        provenance = case.model_input("provenance")
        full = case.model_input("full")

        self.assertEqual(set(action), {"action"})
        self.assertEqual(set(intent), {"action", "user_request"})
        self.assertEqual(set(provenance), {"action", "user_request", "source_trust"})
        self.assertEqual(
            set(full),
            {
                "action",
                "user_request",
                "source_trust",
                "permissions",
                "data_classification",
                "reversibility",
            },
        )


if __name__ == "__main__":
    unittest.main()
