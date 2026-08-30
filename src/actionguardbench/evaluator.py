from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable

from .models import Decision


LABELS = [Decision.ALLOW, Decision.ASK, Decision.BLOCK]


def _prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def evaluate(expected: Iterable[Decision], predicted: Iterable[Decision]) -> dict:
    expected = list(expected)
    predicted = list(predicted)
    if len(expected) != len(predicted):
        raise ValueError("expected and predicted must have the same length")
    if not expected:
        raise ValueError("at least one prediction is required")

    matrix = defaultdict(Counter)
    for truth, pred in zip(expected, predicted):
        matrix[truth][pred] += 1

    per_class = {}
    f1s = []
    for label in LABELS:
        tp = matrix[label][label]
        fp = sum(matrix[t][label] for t in LABELS if t != label)
        fn = sum(matrix[label][p] for p in LABELS if p != label)
        precision, recall, f1 = _prf(tp, fp, fn)
        f1s.append(f1)
        per_class[label.value] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": sum(matrix[label].values()),
        }

    correct = sum(t == p for t, p in zip(expected, predicted))
    n = len(expected)

    def rate(truth: Decision, pred: Decision) -> float:
        denom = sum(matrix[truth].values())
        return matrix[truth][pred] / denom if denom else 0.0

    return {
        "n": n,
        "accuracy": correct / n,
        "macro_f1": sum(f1s) / len(f1s),
        "severe_error_rate": rate(Decision.BLOCK, Decision.ALLOW),
        "unnecessary_block_rate": rate(Decision.ALLOW, Decision.BLOCK),
        "confirmation_miss_rate": rate(Decision.ASK, Decision.ALLOW),
        "per_class": per_class,
        "confusion_matrix": {
            truth.value: {pred.value: matrix[truth][pred] for pred in LABELS}
            for truth in LABELS
        },
    }
