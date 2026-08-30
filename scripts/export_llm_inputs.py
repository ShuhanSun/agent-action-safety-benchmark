from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from actionguardbench.models import BenchmarkCase
from actionguardbench.prompts import render_judge_prompt


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Export blind LLM-judge inputs")
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    parser.add_argument(
        "--condition",
        choices=("action", "intent", "provenance", "full"),
        default="full",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cases = [case for case in load_cases() if case.split == args.split]
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8") as handle:
        for case in cases:
            # Intentionally exclude expected_decision, severity, category, family, rationale,
            # and all other annotation-only fields from the exported blind input.
            row = {
                "id": case.id,
                "condition": args.condition,
                "prompt": render_judge_prompt(case, args.condition),
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"wrote {len(cases)} blind prompts to {args.output}")


if __name__ == "__main__":
    main()
