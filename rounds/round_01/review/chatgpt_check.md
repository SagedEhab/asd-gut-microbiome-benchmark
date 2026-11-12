# Referee check of ChatGPT round 1 (done by Claude; for the human referee to accept or reject)

**Reproduction:** `code/run.py` rerun unchanged on `data/train` reproduces every submitted AUC exactly.

**Leakage review:**
- No holdout or outer-cohort labels are used.
- The genus vocabulary is a label-free union of names, but the 10% prevalence filter is fitted on the training fold only, so genera that appear only in the held-out cohort drop out.
- Network smoothing weights come from training correlations only.
- C is chosen by inner leave-one-training-cohort-out.
- Genus key is the genus name only, so taxa called e.g. "uncultured" in different families are merged. This is a design choice to note, not leakage.

**Gap in the submission:** a permutation null was run only for the abundance model, so the network and combined results were never compared with chance. The checks below fill that gap.

**Full-pipeline permutation null** (`verify_chatgpt_zou.py`): 200 permutations within each training cohort, with C re-chosen on each permuted set.

| Held out | Model | AUC | Null mean (95% range) | Perm p | AUC at C = 0.001 / 0.01 / 0.1 / 1 |
|---|---|---|---|---|---|
| Zou | network | 0.774 | 0.528 (0.228-0.829) | 0.124 | 0.774 / 0.661 / 0.563 / 0.556 |
| Zou | combined | 0.730 | 0.516 (0.174-0.824) | 0.134 | 0.730 / 0.573 / 0.511 / 0.533 |
| David | network | 0.591 | 0.508 (0.418-0.611) | 0.085 | 0.617 / 0.618 / 0.594 / 0.591 |
| David | combined | 0.605 | 0.510 (0.419-0.602) | **0.030** | 0.605 / 0.567 / 0.558 / 0.566 |
| Ding | network | 0.506 | 0.492 (0.328-0.649) | 0.423 | 0.506 / 0.490 / 0.473 / 0.461 |
| Ding | combined | 0.483 | 0.501 (0.288-0.714) | 0.582 | 0.483 / 0.454 / 0.470 / 0.505 |

**Sex check on David** (scores from `oof_predictions.csv`): the combined score barely tracks sex (score-vs-sex AUC 0.48). Within males (n = 65) the AUC is 0.62; within females (n = 44) it is 0.61. The David result is not a sex effect.

**Reading:**
- **Zou 0.774 is real code output but not distinguishable from chance.** With C = 0.001, random labels also reach AUC up to about 0.83 on Zou, and the score falls to 0.56 at larger C. It should not be reported as evidence of transfer.
- **David combined 0.605 is the strongest result in round 1.** The 95% cluster-bootstrap interval is 0.53-0.68, permutation p is 0.03, and it holds within each sex. Caveats: it is one of six network/combined tests (p = 0.03 does not survive a correction for six tests), it depends on C (0.56-0.57 at other values), and it was not prespecified.
