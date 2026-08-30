from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

from actionguardbench.baselines import (
    ConstantBaseline,
    DeterministicFullContextBaseline,
    MajorityBaseline,
    OperationMajorityBaseline,
)
from actionguardbench.models import BenchmarkCase, Decision
from actionguardbench.reporting import (
    cluster_bootstrap_confidence_intervals,
    compact_metrics,
    evaluate_cases,
)


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate_v0_2.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_v0_2", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load v0.2 generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_cases() -> list[BenchmarkCase]:
    generator = load_generator()
    rows = generator.generate_cases()
    generator.validate(rows)
    return [BenchmarkCase.from_dict(row) for row in rows]


def build_baselines(train_cases: list[BenchmarkCase]) -> dict[str, Any]:
    baselines = {
        "always_allow": ConstantBaseline(Decision.ALLOW),
        "always_ask": ConstantBaseline(Decision.ASK),
        "always_block": ConstantBaseline(Decision.BLOCK),
        "majority_train": MajorityBaseline(),
        "operation_majority_train": OperationMajorityBaseline(),
        "deterministic_full_context_v0_1": DeterministicFullContextBaseline(),
    }
    for baseline in baselines.values():
        baseline.fit(train_cases)
    return baselines


def run_split(
    cases: list[BenchmarkCase],
    baselines: dict[str, Any],
    split: str,
    *,
    bootstrap_iterations: int = 0,
) -> dict[str, dict]:
    split_cases = [case for case in cases if case.split == split]
    results = {}
    for name, baseline in baselines.items():
        predictions = baseline.predict(split_cases)
        result = evaluate_cases(split_cases, predictions)
        if bootstrap_iterations > 0:
            result["confidence_intervals"] = cluster_bootstrap_confidence_intervals(
                split_cases,
                predictions,
                iterations=bootstrap_iterations,
                seed=0,
            )
        results[name] = result
    return results


def print_table(results: dict[str, dict[str, dict]]) -> None:
    columns = (
        "accuracy",
        "macro_f1",
        "severe_false_allow",
        "unnecessary_block",
        "confirmation_miss",
        "counterfactual_triplet_accuracy",
    )
    print(
        "| split | baseline | accuracy | macro F1 | BLOCK→ALLOW | ALLOW→BLOCK | ASK→ALLOW | triplet exact |"
    )
    print("|---|---|---:|---:|---:|---:|---:|---:|")
    for split, split_results in results.items():
        for name, result in split_results.items():
            values = compact_metrics(result)
            rendered = [f"{values[column]:.3f}" for column in columns]
            print(
                f"| {split} | {name} | {rendered[0]} | {rendered[1]} | "
                f"{rendered[2]} | {rendered[3]} | {rendered[4]} | {rendered[5]} |"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run reproducible v0.2 non-LLM baselines")
    parser.add_argument(
        "--split",
        choices=("dev", "test", "both"),
        default="both",
        help="Evaluation split. Training labels are used only to fit training-derived baselines.",
    )
    parser.add_argument(
        "--bootstrap-iterations",
        type=int,
        default=0,
        help="Optional family-cluster bootstrap iterations for confidence intervals.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path for full JSON metrics, including category/severity slices.",
    )
    args = parser.parse_args()

    cases = load_cases()
    train_cases = [case for case in cases if case.split == "train"]
    baselines = build_baselines(train_cases)

    splits = ("dev", "test") if args.split == "both" else (args.split,)
    results = {
        split: run_split(
            cases,
            baselines,
            split,
            bootstrap_iterations=args.bootstrap_iterations,
        )
        for split in splits
    }

    print_table(results)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"\nWrote full metrics to {args.output}")


if __name__ == "__main__":
    main()
