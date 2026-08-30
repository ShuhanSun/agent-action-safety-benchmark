# Research Plan

## Working title

**ActionGuardBench: Context-Aware Pre-Execution Safety Evaluation for Tool-Using AI Agents**

## Motivation

Broad agent-safety scores often mix several latent capabilities: task completion, refusal behavior, prompt-injection robustness, multi-step planning, risk recognition, and evaluator behavior. ActionGuardBench isolates a narrower operational capability: whether a system makes the correct contextual authorization decision for a **proposed tool action immediately before execution**.

This boundary is intentionally different from end-to-end harmful-task benchmarks, dynamic prompt-injection environments, multi-step hazard benchmarks, and retrospective risk-judgment datasets.

## Hypotheses

**H1.** Action-only classifiers will underperform classifiers that receive user intent and contextual metadata.

**H2.** Provenance information will materially improve detection of indirect prompt injection and confused-deputy failures.

**H3.** Binary safe/unsafe labels will either over-block benign actions or under-detect ambiguous high-impact actions; an explicit `ASK` class will improve the safety–utility frontier.

**H4.** Models with high general capability will not necessarily have proportionally lower severe false-allow rates.

**H5.** A meaningful fraction of errors will be counterfactual inconsistency: the model will assign the same decision to matched actions even when authorization context changes.

## Experimental factors

### Inputs

Evaluate four information conditions:

1. `action`: proposed action only;
2. `intent`: action + user request;
3. `provenance`: action + user request + source trust;
4. `full`: request + provenance + permissions + sensitivity + reversibility.

`BenchmarkCase.model_input()` implements these conditions while excluding labels and benchmark-structure metadata.

### Baselines

- majority-class baseline;
- operation-only / trivial policy baseline;
- deterministic metadata policy;
- prompt-only LLM judge;
- structured-context LLM judge;
- optional fine-tuned small classifier.

### Primary metrics

- severe false-allow rate (`BLOCK -> ALLOW`);
- macro F1;
- per-class recall;
- unnecessary-block rate (`ALLOW -> BLOCK`);
- confirmation miss rate (`ASK -> ALLOW`).

### Secondary metrics

- performance by risk category;
- performance by severity;
- counterfactual consistency within family;
- performance across information ablations;
- confidence intervals from bootstrap resampling at the family level.

## Dataset roadmap

### v0.1 — complete

30 synthetic sanity-check examples used to validate the execution and evaluation pipeline.

### v0.2 — in progress

The current v0.2 specification contains:

- 30 scenario families;
- 9 broad risk categories;
- matched `ALLOW`, `ASK`, and `BLOCK` decisions within every family;
- 4 semantics-preserving variants per decision;
- 360 generated cases total;
- balanced decision classes (120 / 120 / 120);
- family-held-out split: 216 train / 72 dev / 72 test;
- reproducible generation and invariant validation;
- action / intent / provenance / full-context ablation API.

The next v0.2 work is **not simply generating more rows**. The important remaining work is annotation-quality and validity work:

1. rewrite a substantial subset independently rather than from common templates;
2. create an annotation guide with edge-case decision rules;
3. obtain at least two independent annotations per evaluation case;
4. adjudicate disagreements and report agreement;
5. add trivial baselines to detect lexical or operation-label shortcuts;
6. run model evaluations under all four input conditions.

### Paper candidate

Target 1,000+ cases with independently authored scenario families, multiple annotators, adjudication, inter-annotator agreement, held-out templates, stronger paraphrase diversity, multi-model evaluation, and family-level confidence intervals.

## Important validity safeguards

- do not report one aggregate "safety score" as if it measured all agent safety;
- publish class prevalence alongside F1;
- include majority and intentionally trivial baselines;
- split by scenario/template family to reduce leakage;
- use matched counterfactuals to test contextual reasoning;
- inspect lexical shortcuts and operation-label correlations;
- bootstrap confidence intervals at the family rather than duplicated-variant level;
- report model/version/date and exact prompting configuration;
- keep synthetic smoke-test results clearly separate from benchmark results;
- treat v0.2 as an experimental synthetic dataset, not a universal safety measure.
