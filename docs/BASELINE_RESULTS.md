# v0.2 Baseline Results

These results are **structural validation results on the synthetic v0.2 dataset**, not paper claims. They are intended to detect benchmark shortcuts, label imbalance, leakage, and trivial-policy failure modes before expensive model evaluation or human annotation.

The numbers below were produced by GitHub Actions from commit `e521f0e3f08cd55b7ba12e0b016079f38c880bfa` on Python 3.10, 3.11, and 3.12. All CI jobs passed.

## Results

| split | baseline | accuracy | macro F1 | BLOCK->ALLOW | ALLOW->BLOCK | ASK->ALLOW |
|---|---|---:|---:|---:|---:|---:|
| dev | always_allow | 0.333 | 0.167 | 1.000 | 0.000 | 1.000 |
| dev | always_ask | 0.333 | 0.167 | 0.000 | 0.000 | 0.000 |
| dev | always_block | 0.333 | 0.167 | 0.000 | 1.000 | 0.000 |
| dev | majority_train | 0.333 | 0.167 | 0.000 | 0.000 | 0.000 |
| dev | operation_majority_train | 0.333 | 0.167 | 0.000 | 0.000 | 0.000 |
| dev | deterministic_full_context_v0_1 | 0.500 | 0.461 | 0.500 | 0.000 | 0.500 |
| test | always_allow | 0.333 | 0.167 | 1.000 | 0.000 | 1.000 |
| test | always_ask | 0.333 | 0.167 | 0.000 | 0.000 | 0.000 |
| test | always_block | 0.333 | 0.167 | 0.000 | 1.000 | 0.000 |
| test | majority_train | 0.333 | 0.167 | 0.000 | 0.000 | 0.000 |
| test | operation_majority_train | 0.333 | 0.167 | 0.000 | 0.000 | 0.000 |
| test | deterministic_full_context_v0_1 | 0.444 | 0.407 | 0.500 | 0.000 | 0.667 |

## Interpretation

### Trivial policies do not exploit class prevalence

Because v0.2 is exactly balanced across `ALLOW`, `ASK`, and `BLOCK`, all constant policies and the training-majority policy achieve 1/3 accuracy. This is expected and is a useful validity check.

### Operation identity alone is insufficient

`operation_majority_train` also achieves only 1/3 accuracy on both dev and test. This baseline sees only the operation name learned from the training split. Its failure is desirable: the dataset is explicitly constructed so that the same class of tool action can be `ALLOW`, `ASK`, or `BLOCK` depending on context.

This does **not** prove that the benchmark has no lexical or template shortcuts. It only rules out one very shallow shortcut family.

### Narrow hand-written rules transfer poorly

The unchanged v0.1 deterministic policy reaches 0.444 test accuracy and 0.407 macro F1. More importantly, it incorrectly allows 50% of test cases whose correct label is `BLOCK` and allows 66.7% of test cases that should require confirmation.

This is evidence that a small set of operation-specific rules does not generalize well across the broader v0.2 action families. It is not evidence that LLM-based safety judges will perform well.

## What these results do not establish

The current dataset is generated from manually authored scenario recipes and lightweight paraphrase variants. Therefore these results do not establish:

- real-world agent safety;
- human-level annotation validity;
- robustness to naturally occurring language;
- robustness to adaptive adversaries;
- cross-model generalization;
- independence from template or lexical artifacts.

Before publication-quality claims, the benchmark needs independent annotation, stronger paraphrase diversity, held-out human-authored cases, model evaluation, and statistical uncertainty estimates.

## Reproduction

```bash
python -m pip install -e .
python scripts/run_v0_2_baselines.py --split both --output results/v0.2-baselines.json
```
