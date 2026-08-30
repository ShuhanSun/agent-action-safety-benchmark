from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from actionguardbench.models import BenchmarkCase
from actionguardbench.prompts import parse_decision
from actionguardbench.reporting import compact_metrics, evaluate_cases


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate_v0_2.py"


def load_cases() -> list[BenchmarkCase]:
    spec = importlib.util.spec_from_file_location("generate_v0_2", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load v0.2 generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = module.generate_cases()
    module.validate(rows)
    return [BenchmarkCase.from_dict(row) for row in rows]


def load_predictions(path: Path) -> dict[str, object]:
    predictions = {}
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            case_id = row.get("id")
            if not isinstance(case_id, str) or not case_id:
                raise ValueError(f"line {line_number}: missing string id")
            if case_id in predictions:
                raise ValueError(f"duplicate prediction id: {case_id}")
            raw = row.get("decision", row.get("raw_output"))
            if not isinstance(raw, str):
                raise ValueError(f"line {line_number}: expected decision or raw_output string")
            predictions[case_id] = parse_decision(raw)
    return predictions


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate blind model predictions")
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    cases = [case for case in load_cases() if case.split == args.split]
    predictions = load_predictions(args.predictions)

    expected_ids = {case.id for case in cases}
    supplied_ids = set(predictions)
    missing = sorted(expected_ids - supplied_ids)
    extra = sorted(supplied_ids - expected_ids)
    if missing or extra:
        raise ValueError(
            f"prediction coverage mismatch: missing={len(missing)}, extra={len(extra)}; "
            f"first_missing={missing[:3]}, first_extra={extra[:3]}"
        )

    ordered_predictions = [predictions[case.id] for case in cases]
    result = evaluate_cases(cases, ordered_predictions)
    compact = compact_metrics(result)

    print(f"split: {args.split}")
    for key, value in compact.items():
        print(f"{key}: {value:.4f}")

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"wrote full metrics to {args.output}")


if __name__ == "__main__":
    main()
