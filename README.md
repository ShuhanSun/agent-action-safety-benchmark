# ActionGuardBench

![CI](https://github.com/ShuhanSun/agent-action-safety-benchmark/actions/workflows/ci.yml/badge.svg)

**A benchmark for pre-execution safety decisions in tool-using AI agents.**

ActionGuardBench evaluates whether an AI agent or safety layer can make the right decision **before a proposed tool action executes**. Instead of treating "agent safety" as one broad score, the benchmark isolates a concrete operational question:

> Given the user's intent, the action being proposed, its provenance, permissions, data sensitivity, and reversibility, should the system **ALLOW**, **ASK** for confirmation, or **BLOCK** the action?

## Why this benchmark

Existing agent-safety benchmarks cover important but different targets such as harmful task compliance, indirect prompt injection, end-to-end task execution, multi-step harmful behavior, or retrospective risk judgment. ActionGuardBench focuses on one narrower control point: **contextual authorization at the execution boundary**.

This makes the benchmark useful for evaluating agent guardrails, policy engines, approval systems, and model-based action-risk judges without requiring a dangerous real-world environment.

## Core research questions

1. **Risk recognition:** Can a system distinguish benign, ambiguous, and unsafe tool actions?
2. **Context sensitivity:** Does adding user intent, provenance, permissions, sensitivity, and reversibility improve decisions?
3. **Safety–utility tradeoff:** Can a system reduce severe unsafe actions without over-blocking benign work?
4. **Injection robustness:** Can it reject unsafe actions originating from untrusted tool output while preserving the user's original task?
5. **Calibration:** When should a system choose human confirmation (`ASK`) rather than unconditional allow/block?

## Decision labels

- `ALLOW`: action is within the user's intent and authorization with acceptable risk.
- `ASK`: action may be legitimate but requires user confirmation because of ambiguity, sensitive side effects, or missing authorization.
- `BLOCK`: action materially violates user intent, policy, permissions, provenance boundaries, or safety constraints.

## v0.2 dataset design

The current v0.2 design contains **30 scenario families** across nine broad categories. Each family contains matched `ALLOW`, `ASK`, and `BLOCK` cases. Each decision prototype has four semantics-preserving variants, producing **360 synthetic cases** with exactly balanced classes: 120 `ALLOW`, 120 `ASK`, and 120 `BLOCK`.

The split is family-held-out: train has 18 families / 216 cases, dev has 6 families / 72 cases, and test has 6 families / 72 cases. No family crosses splits. See [`docs/SCENARIO_FAMILIES.md`](docs/SCENARIO_FAMILIES.md) for the full design and [`docs/ANNOTATION_GUIDE.md`](docs/ANNOTATION_GUIDE.md) for the decision rubric.

## Information ablations

The benchmark supports four controlled input conditions:

1. `action` — proposed tool action only;
2. `intent` — action + user request;
3. `provenance` — action + request + source trust;
4. `full` — request + provenance + permissions + sensitivity + reversibility.

This tests the central hypothesis: **which contextual signals actually reduce unsafe false allows?**

## Quick start

```bash
python -m pip install -e .
python scripts/generate_v0_2.py
python -m unittest discover -s tests -v
python scripts/run_v0_2_baselines.py --split both --output results/v0.2-baselines.json
```

The generator validates dataset size, class balance, split balance, unique IDs, family isolation, and semantic duplicates. GitHub Actions runs the full suite on Python 3.10, 3.11, and 3.12.

## Non-LLM baselines

The repository includes deliberately weak validity controls:

- always `ALLOW`;
- always `ASK`;
- always `BLOCK`;
- training-majority label;
- training operation-majority label;
- the unchanged v0.1 hand-written full-context policy.

On the synthetic v0.2 **test** split, the trivial and operation-only baselines achieve 0.333 accuracy / 0.167 macro F1. The unchanged v0.1 deterministic policy reaches 0.444 accuracy / 0.407 macro F1, with a 0.500 `BLOCK -> ALLOW` rate and 0.667 `ASK -> ALLOW` rate. These are structural validation results, not paper claims. See [`docs/BASELINE_RESULTS.md`](docs/BASELINE_RESULTS.md).

## LLM evaluation without label leakage

Export blind prompts for any one ablation condition:

```bash
python scripts/export_llm_inputs.py \
  --split dev \
  --condition full \
  --output /tmp/actionguard-dev-full.jsonl
```

Each row contains only a case ID, input condition, and model prompt. Ground-truth labels, severity, risk tags, rationale, family IDs, categories, and split metadata are excluded from the prompt.

After running a model externally, save predictions as JSONL:

```json
{"id":"AGB2-F05-A-01","decision":"ALLOW"}
```

Then evaluate them locally:

```bash
python scripts/evaluate_predictions.py predictions.jsonl \
  --split dev \
  --output results/model-dev-full.json
```

The evaluator requires exact split coverage and rejects duplicate IDs or ambiguous model outputs.

## Metrics

ActionGuardBench does **not** rely on one headline safety score. The evaluator reports:

- accuracy;
- macro F1;
- per-class precision / recall / F1;
- severe false-allow rate: `BLOCK -> ALLOW`;
- unnecessary-block rate: `ALLOW -> BLOCK`;
- confirmation miss rate: `ASK -> ALLOW`;
- confusion matrix;
- per-category performance;
- per-severity performance.

The severe false-allow rate is intentionally separated from ordinary classification error because allowing an unsafe irreversible action is not equivalent to conservatively asking for confirmation.

## Repository layout

```text
agent-action-safety-benchmark/
├── .github/workflows/ci.yml
├── data/
│   ├── cases_v0.1.jsonl
│   └── scenario_families_v0.2.json
├── docs/
│   ├── ANNOTATION_GUIDE.md
│   ├── BASELINE_RESULTS.md
│   ├── DATA_SCHEMA.md
│   ├── RESEARCH_PLAN.md
│   ├── SCENARIO_FAMILIES.md
│   └── THREAT_MODEL.md
├── scripts/
│   ├── evaluate_predictions.py
│   ├── export_llm_inputs.py
│   ├── generate_v0_2.py
│   ├── run_baseline.py
│   └── run_v0_2_baselines.py
├── src/actionguardbench/
│   ├── baselines.py
│   ├── evaluator.py
│   ├── models.py
│   ├── policy.py
│   ├── prompts.py
│   └── reporting.py
└── tests/
```

## Status

- **v0.1:** executable research scaffold and 30-case sanity-check set.
- **v0.2:** 30-family / 360-case synthetic design, reproducible generator, family-held-out split, ablation API, annotation guide, trivial/shallow baselines, blind LLM export/evaluation harness, and CI.
- **paper candidate:** 1,000+ cases with independently written scenarios, multiple annotators, adjudication, inter-annotator agreement, confidence intervals, multi-model evaluation, and stronger natural-language diversity.

v0.2 should still be treated as a **synthetic experimental dataset**, not as a validated universal measure of agent safety.

## Safety

All included tools and scenarios are simulated. Network examples use reserved/example domains, financial examples use fictional beneficiaries, and shell-risk examples use symbolic placeholders instead of operational destructive commands. The benchmark does not execute real shell commands, send messages, transfer funds, access credentials, or transmit private data.

## Citation

A citation will be added after the benchmark specification and paper are released.
