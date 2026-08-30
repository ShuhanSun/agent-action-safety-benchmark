from __future__ import annotations

import unittest

from actionguardbench.models import BenchmarkCase, Decision
from actionguardbench.reporting import (
    cluster_bootstrap_confidence_intervals,
    counterfactual_triplet_accuracy,
)


def make_case(case_id: str, family: str, variant: int, label: Decision) -> BenchmarkCase:
    return BenchmarkCase(
        id=case_id,
        scenario="statistics-test",
        user_request="synthetic request",
        source_trust="trusted",
        action={"tool": "demo", "operation": "demo_action", "args": {}},
        permissions=["demo_action"],
        data_classification="internal",
        reversibility="reversible",
        expected_decision=label,
        severity=2,
        risk_tags=[],
        rationale="test",
        family_id=family,
        category="test",
        split="test",
        variant_index=variant,
    )


def triplet(family: str, variant: int) -> list[BenchmarkCase]:
    return [
        make_case(f"{family}-A-{variant}", family, variant, Decision.ALLOW),
        make_case(f"{family}-Q-{variant}", family, variant, Decision.ASK),
        make_case(f"{family}-B-{variant}", family, variant, Decision.BLOCK),
    ]


class StatisticsTests(unittest.TestCase):
    def test_counterfactual_triplet_requires_all_three_correct(self):
        cases = triplet("F1", 1) + triplet("F2", 1)
        predictions = [
            Decision.ALLOW,
            Decision.ASK,
            Decision.BLOCK,
            Decision.ALLOW,
            Decision.ALLOW,  # one error makes the entire second triplet fail
            Decision.BLOCK,
        ]
        result = counterfactual_triplet_accuracy(cases, predictions)
        self.assertEqual(result["triplets"], 2)
        self.assertEqual(result["exact_matches"], 1)
        self.assertEqual(result["exact_match_accuracy"], 0.5)

    def test_cluster_bootstrap_counts_families_not_rows(self):
        cases = triplet("F1", 1) + triplet("F2", 1)
        predictions = [case.expected_decision for case in cases]
        intervals = cluster_bootstrap_confidence_intervals(
            cases,
            predictions,
            iterations=50,
            seed=7,
        )
        self.assertEqual(intervals["clusters"], 2)
        self.assertEqual(intervals["iterations"], 50)
        self.assertEqual(intervals["accuracy"]["low"], 1.0)
        self.assertEqual(intervals["accuracy"]["high"], 1.0)

    def test_counterfactual_metric_ignores_incomplete_group(self):
        cases = triplet("F1", 1)[:2]
        predictions = [Decision.ALLOW, Decision.ASK]
        result = counterfactual_triplet_accuracy(cases, predictions)
        self.assertEqual(result["triplets"], 0)
        self.assertEqual(result["exact_match_accuracy"], 0.0)


if __name__ == "__main__":
    unittest.main()
