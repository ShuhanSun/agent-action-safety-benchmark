from __future__ import annotations

import json
from pathlib import Path

from actionguardbench import BaselinePolicy, BenchmarkCase, evaluate


def main() -> None:
    dataset = Path(__file__).resolve().parents[1] / "data" / "cases_v0.1.jsonl"
    policy = BaselinePolicy()
    cases = []

    with dataset.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(BenchmarkCase.from_dict(json.loads(line)))

    predicted = [policy.decide(case) for case in cases]
    metrics = evaluate([case.expected_decision for case in cases], predicted)

    print(json.dumps(metrics, indent=2))
    print("\nErrors:")
    for case, pred in zip(cases, predicted):
        if pred != case.expected_decision:
            print(f"- {case.id}: expected={case.expected_decision.value}, predicted={pred.value}")


if __name__ == "__main__":
    main()
