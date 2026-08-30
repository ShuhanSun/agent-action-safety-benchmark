from __future__ import annotations

import unittest

from actionguardbench.baselines import (
    ConstantBaseline,
    MajorityBaseline,
    OperationMajorityBaseline,
)
from actionguardbench.models import BenchmarkCase, Decision
from actionguardbench.reporting import evaluate_cases


def case(
    case_id: str,
    operation: str,
    label: Decision,
    *,
    category: str = "test_category",
    severity: int = 2,
) -> BenchmarkCase:
    return BenchmarkCase(
        id=case_id,
        scenario="synthetic-test",
        user_request="synthetic request",
        source_trust="trusted",
        action={"tool": "demo", "operation": operation, "args": {}},
        permissions=[operation],
        data_classification="internal",
        reversibility="reversible",
        expected_decision=label,
        severity=severity,
        risk_tags=[],
        rationale="test only",
        family_id="TEST",
        category=category,
        split="train",
        variant_index=1,
    )


class BaselineTests(unittest.TestCase):
    def test_constant_baseline(self):
        cases = [case("1", "send_email", Decision.BLOCK)]
        predictions = ConstantBaseline(Decision.ALLOW).predict(cases)
        self.assertEqual(predictions, [Decision.ALLOW])

    def test_majority_baseline_uses_training_labels(self):
        train = [
            case("1", "read_file", Decision.ALLOW),
            case("2", "read_file", Decision.ALLOW),
            case("3", "read_file", Decision.BLOCK),
        ]
        baseline = MajorityBaseline().fit(train)
        self.assertEqual(baseline.decision, Decision.ALLOW)

    def test_balanced_majority_tie_is_deterministic(self):
        train = [
            case("1", "a", Decision.ALLOW),
            case("2", "b", Decision.ASK),
            case("3", "c", Decision.BLOCK),
        ]
        baseline = MajorityBaseline().fit(train)
        self.assertEqual(baseline.decision, Decision.ASK)

    def test_operation_majority_falls_back_for_unseen_operation(self):
        train = [
            case("1", "send_email", Decision.BLOCK),
            case("2", "send_email", Decision.BLOCK),
            case("3", "read_file", Decision.ALLOW),
        ]
        baseline = OperationMajorityBaseline().fit(train)
        self.assertEqual(
            baseline.predict_one(case("4", "send_email", Decision.ALLOW)),
            Decision.BLOCK,
        )
        self.assertEqual(
            baseline.predict_one(case("5", "unseen_tool", Decision.ALLOW)),
            Decision.BLOCK,
        )

    def test_reporting_includes_category_and_severity_slices(self):
        cases = [
            case("1", "read_file", Decision.ALLOW, category="data", severity=0),
            case("2", "send_email", Decision.BLOCK, category="external", severity=4),
        ]
        result = evaluate_cases(cases, [Decision.ALLOW, Decision.ALLOW])
        self.assertIn("overall", result)
        self.assertIn("data", result["by_category"])
        self.assertIn("external", result["by_category"])
        self.assertIn("0", result["by_severity"])
        self.assertIn("4", result["by_severity"])
        self.assertEqual(result["overall"]["severe_error_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
