# D110 Aggregation Provenance Measurement — Report

- Run timestamp (UTC): 20260730T095723Z
- Git commit at run time: `b1993d07ad3f6422df9e93c7649ca8d9eedd0f5a`
- NLI base model: `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli`
- Adapter path: none (zero-shot only, D89/D109)
- Thresholds: tau=0.5, tau_e=0.9, alpha=0.0, k=10

Per claim: `verdict_current` = `score_claim(max_e, max_c_independent, ...)` versus `verdict_if_same_chunk` = `score_claim(max_e, c_at_argmax_e, ...)` — same production `score_claim` function (scoring/aggregation.py) both times; only which chunk's contradiction probability is passed in differs.

## SE-028 (results/pipeline_demo/SE-028_v3.json)

| claim_index | max_e | max_c_independent | c_at_argmax_e | same_chunk | verdict_current | verdict_if_same_chunk |
|---|---|---|---|---|---|---|
| 0 | 0.989886 | 0.994264 | 0.001458 | False | VERIFIED (score=1.0000) | VERIFIED (score=1.0000) |
| 1 | 0.998438 | 0.991719 | 0.000348 | False | VERIFIED (score=1.0000) | VERIFIED (score=1.0000) |
| 2 | 0.998747 | 0.968310 | 0.000374 | False | VERIFIED (score=1.0000) | VERIFIED (score=1.0000) |
| 3 | 0.998663 | 0.998147 | 0.000355 | False | VERIFIED (score=1.0000) | VERIFIED (score=1.0000) |
| 4 | 0.882708 | 0.999570 | 0.093219 | False | CONTRADICTED (score=-0.9996) | NEUTRAL (score=0.0000) |
| 5 | 0.998436 | 0.000451 | 0.000167 | False | VERIFIED (score=1.0000) | VERIFIED (score=1.0000) |

max_e_per_keypoint: [0.943305, 0.018094]

| metric | current (independent max_c) | same-chunk substitution |
|---|---|---|
| precision | 0.666738 | 0.833333 |
| coverage | 0.480699 | 0.480699 |
| harmonic_f | 0.558637 | 0.609700 |
| score | 55.863729 | 60.970001 |

## GN-040 (results/pipeline_demo/GN-040_v3.json)

| claim_index | max_e | max_c_independent | c_at_argmax_e | same_chunk | verdict_current | verdict_if_same_chunk |
|---|---|---|---|---|---|---|
| 0 | 0.997134 | 0.031065 | 0.000212 | False | VERIFIED (score=1.0000) | VERIFIED (score=1.0000) |
| 1 | 0.994642 | 0.002565 | 0.000337 | False | VERIFIED (score=1.0000) | VERIFIED (score=1.0000) |
| 2 | 0.003683 | 0.999063 | 0.995033 | False | CONTRADICTED (score=-0.9991) | CONTRADICTED (score=-0.9950) |
| 3 | 0.998536 | 0.184274 | 0.000158 | False | VERIFIED (score=1.0000) | VERIFIED (score=1.0000) |
| 4 | 0.998428 | 0.004797 | 0.000173 | False | VERIFIED (score=1.0000) | VERIFIED (score=1.0000) |

max_e_per_keypoint: [0.02288, 0.000465]

| metric | current (independent max_c) | same-chunk substitution |
|---|---|---|
| precision | 0.600187 | 0.600993 |
| coverage | 0.011673 | 0.011673 |
| harmonic_f | 0.022900 | 0.022900 |
| score | 2.289965 | 2.290023 |
