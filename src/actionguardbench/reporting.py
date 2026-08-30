from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .evaluator import evaluate
from .models import BenchmarkCase, Decision


def evaluate_cases(
    cases: Iterable[BenchmarkCase], predicted: Iterable[Decision]
) -> dict:
    """Evaluate overall performance plus benchmark-relevant slices."""
    cases = list(cases)
    predicted = list(predicted)
    if len(cases) != len(predicted):
        raise ValueError("cases and predicted must have the same length")

    expected = [case.expected_decision for case in cases]
    result = {"overall": evaluate(expected, predicted)}

    category_rows: dict[str, list[tuple[Decision, Decision]]] = defaultdict(list)
    severity_rows: dict[int, list[tuple[Decision, Decision]]] = defaultdict(list)

    for case, pred in zip(cases, predicted):
        category_rows[case.category or "unspecified"].append((case.expected_decision, pred))
        severity_rows[case.severity].append((case.expected_decision, pred))

    result["by_category"] = {
        category: evaluate(
            [truth for truth, _ in rows],
            [pred for _, pred in rows],
        )
        for category, rows in sorted(category_rows.items())
    }
    result["by_severity"] = {
        str(severity): evaluate(
            [truth for truth, _ in rows],
            [pred for _, pred in rows],
        )
        for severity, rows in sorted(severity_rows.items())
    }
    return result


def compact_metrics(result: dict) -> dict[str, float]:
    overall = result["overall"]
    return {
        "accuracy": overall["accuracy"],
        "macro_f1": overall["macro_f1"],
        "severe_false_allow": overall["severe_error_rate"],
        "unnecessary_block": overall["unnecessary_block_rate"],
        "confirmation_miss": overall["confirmation_miss_rate"],
    }
