from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

from .models import BenchmarkCase, Decision
from .policy import BaselinePolicy


# A deterministic tie-break is important because v0.2 is intentionally class-balanced.
# ASK is the least committal middle action, but this choice is reported explicitly rather
# than treated as a learned property of the benchmark.
TIE_BREAK = (Decision.ASK, Decision.ALLOW, Decision.BLOCK)


def _majority_label(counts: Counter[Decision]) -> Decision:
    if not counts:
        return Decision.ASK
    best = max(counts.values())
    winners = {label for label, count in counts.items() if count == best}
    return next(label for label in TIE_BREAK if label in winners)


@dataclass
class ConstantBaseline:
    """Always emit the same decision.

    These deliberately weak policies are useful validity controls. A benchmark should
    not look strong merely because a trivial always-ALLOW/ASK/BLOCK strategy scores well.
    """

    decision: Decision

    def fit(self, cases: Iterable[BenchmarkCase]) -> "ConstantBaseline":
        return self

    def predict_one(self, case: BenchmarkCase) -> Decision:
        return self.decision

    def predict(self, cases: Iterable[BenchmarkCase]) -> list[Decision]:
        return [self.predict_one(case) for case in cases]


class MajorityBaseline:
    """Predict the majority label observed in the training split only."""

    def __init__(self) -> None:
        self.decision = Decision.ASK

    def fit(self, cases: Iterable[BenchmarkCase]) -> "MajorityBaseline":
        counts = Counter(case.expected_decision for case in cases)
        self.decision = _majority_label(counts)
        return self

    def predict_one(self, case: BenchmarkCase) -> Decision:
        return self.decision

    def predict(self, cases: Iterable[BenchmarkCase]) -> list[Decision]:
        return [self.decision for _ in cases]


class OperationMajorityBaseline:
    """Learn P(label | operation) from the training split.

    This is intentionally shallow: it sees only the proposed operation name and no user
    intent, provenance, permissions, sensitivity, or reversibility. It tests whether a
    benchmark can be gamed by learning that some tool names are generally "safe" or
    "unsafe" rather than reasoning about context.
    """

    def __init__(self) -> None:
        self.default = Decision.ASK
        self.by_operation: dict[str, Decision] = {}

    @staticmethod
    def _operation(case: BenchmarkCase) -> str:
        return str(case.action.get("operation", case.action.get("tool", ""))).lower()

    def fit(self, cases: Iterable[BenchmarkCase]) -> "OperationMajorityBaseline":
        cases = list(cases)
        self.default = _majority_label(Counter(case.expected_decision for case in cases))

        counts: dict[str, Counter[Decision]] = defaultdict(Counter)
        for case in cases:
            counts[self._operation(case)][case.expected_decision] += 1

        self.by_operation = {
            operation: _majority_label(label_counts)
            for operation, label_counts in counts.items()
        }
        return self

    def predict_one(self, case: BenchmarkCase) -> Decision:
        return self.by_operation.get(self._operation(case), self.default)

    def predict(self, cases: Iterable[BenchmarkCase]) -> list[Decision]:
        return [self.predict_one(case) for case in cases]


class DeterministicFullContextBaseline:
    """Adapter around the hand-written v0.1 policy.

    It is evaluated unchanged on v0.2 on purpose. This measures how badly a narrow set
    of hand-authored rules transfers to held-out action families and prevents us from
    silently tuning the policy against the test set.
    """

    def __init__(self) -> None:
        self.policy = BaselinePolicy()

    def fit(self, cases: Iterable[BenchmarkCase]) -> "DeterministicFullContextBaseline":
        return self

    def predict_one(self, case: BenchmarkCase) -> Decision:
        return self.policy.decide(case)

    def predict(self, cases: Iterable[BenchmarkCase]) -> list[Decision]:
        return [self.predict_one(case) for case in cases]
