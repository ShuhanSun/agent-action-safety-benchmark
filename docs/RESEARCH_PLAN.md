# Research Plan

## Working title

**ActionGuardBench: Context-Aware Pre-Execution Safety Evaluation for Tool-Using AI Agents**

## Motivation

Broad agent-safety scores often mix several latent capabilities: task completion, refusal behavior, prompt-injection robustness, risk recognition, and evaluator behavior. ActionGuardBench isolates a narrower operational capability: whether the system makes the correct execution decision for a proposed action.

## Hypotheses

**H1.** Action-only classifiers will underperform classifiers that receive user intent and contextual metadata.

**H2.** Provenance information will materially improve detection of indirect prompt injection and confused-deputy failures.

**H3.** Binary safe/unsafe labels will either over-block benign actions or under-detect ambiguous high-impact actions; an explicit `ASK` class will improve the safety–utility frontier.

**H4.** Models with high general capability will not necessarily have proportionally lower severe false-allow rates.

## Experimental factors

### Inputs

Evaluate four information conditions:

1. action only
2. action + user request
3. action + user request + provenance
4. full context: request + provenance + permissions + sensitivity + reversibility

### Baselines

- majority-class baseline
- deterministic metadata policy
- prompt-only LLM judge
- structured-context LLM judge
- optional fine-tuned small classifier

### Metrics

Primary metrics:

- severe false-allow rate (`BLOCK -> ALLOW`)
- macro F1
- per-class recall
- unnecessary-block rate (`ALLOW -> BLOCK`)

Secondary metrics:

- `ASK` calibration / confirmation miss rate
- performance by attack/risk category
- performance by severity
- performance under counterfactual pairs

## Dataset target

### v0.1

24-40 synthetic sanity-check examples.

### v0.2

300 manually designed, counterfactually paired cases across at least 8 risk categories.

### paper candidate

1,000+ cases with independent annotation, adjudication, inter-annotator agreement, held-out templates, and multi-model evaluation.

## Important validity safeguards

- do not report one aggregate "safety score" as if it measured all agent safety;
- publish class prevalence alongside F1;
- include majority and trivial-policy baselines;
- split by scenario/template family to reduce leakage;
- use matched counterfactuals to test contextual reasoning;
- report confidence intervals and model/version/date;
- keep synthetic smoke-test results clearly separate from benchmark results.
