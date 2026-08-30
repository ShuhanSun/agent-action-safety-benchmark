# ActionGuardBench

**A benchmark for pre-execution safety decisions in tool-using AI agents.**

ActionGuardBench evaluates whether an AI agent or safety layer can make the right decision **before a proposed tool action executes**. Instead of treating "agent safety" as one broad score, the benchmark isolates a concrete operational question:

> Given the user's intent, the action being proposed, its provenance, permissions, data sensitivity, and reversibility, should the system **ALLOW**, **ASK** for confirmation, or **BLOCK** the action?

## Why this benchmark

Existing agent-safety benchmarks cover important but different targets such as harmful task compliance, indirect prompt injection, end-to-end task execution, or retrospective risk judgment. ActionGuardBench focuses on the execution boundary: the moment immediately before a tool call can create an external side effect.

This makes the benchmark useful for evaluating agent guardrails, policy engines, approval systems, and model-based action-risk judges without requiring a dangerous real-world environment.

## Core research questions

1. **Risk recognition:** Can a system distinguish benign, ambiguous, and unsafe tool actions?
2. **Context sensitivity:** Does adding provenance, authorization, data sensitivity, and reversibility improve safety decisions?
3. **Safety–utility tradeoff:** Can a system reduce severe unsafe actions without over-blocking benign work?
4. **Injection robustness:** Can it reject unsafe actions that originate from untrusted tool output while preserving the user's original task?
5. **Calibration:** When should a system choose human confirmation (`ASK`) rather than unconditional allow/block?

## Decision labels

- `ALLOW`: action is within the user's intent and authorization with acceptable risk.
- `ASK`: action may be legitimate but requires user confirmation because of ambiguity, sensitive side effects, or missing authorization.
- `BLOCK`: action materially violates user intent, policy, permissions, or safety constraints.

## Initial threat categories

- indirect prompt injection
- data exfiltration
- destructive or irreversible action
- over-privileged tool use
- external communication / impersonation
- financial or commitment-bearing action
- permission escalation / confused deputy
- unsafe shell or system modification

## Repository layout

```text
agent-action-safety-benchmark/
├── data/
│   └── cases_v0.1.jsonl
├── docs/
│   ├── DATA_SCHEMA.md
│   ├── RESEARCH_PLAN.md
│   └── THREAT_MODEL.md
├── scripts/
│   └── run_baseline.py
├── src/actionguardbench/
│   ├── __init__.py
│   ├── evaluator.py
│   ├── models.py
│   └── policy.py
├── tests/
│   └── test_policy.py
├── LICENSE
├── pyproject.toml
└── README.md
```

## Quick start

```bash
python -m pip install -e .
python scripts/run_baseline.py
python -m unittest discover -s tests
```

## Metrics

ActionGuardBench does **not** rely on one headline F1 score. The evaluator reports:

- accuracy
- macro F1
- per-class precision / recall / F1
- severe-error rate: `BLOCK -> ALLOW`
- unnecessary-block rate: `ALLOW -> BLOCK`
- confirmation miss rate: `ASK -> ALLOW`
- confusion matrix

The benchmark will later add a cost-sensitive risk score that weights dangerous false allows more heavily than conservative false blocks.

## Status

`v0.1` is a research scaffold and synthetic sanity-check dataset. It is **not** yet a validated benchmark or a publishable result. The next milestone is dataset design and independent annotation before running model comparisons.

## Safety

All included tools and scenarios are simulated. The benchmark does not execute real shell commands, send messages, transfer funds, access credentials, or transmit private data.

## Citation

A citation will be added after the benchmark specification and paper are released.
