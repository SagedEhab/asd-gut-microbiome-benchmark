# Referee check of ChatGPT round 2 (done by Claude, a contestant; for the human referee to accept or reject)

**Reproduction.** All five scripts were rerun unchanged on `data/train` (helpers through a launcher that adds the code folder to Python's path).

| Output | Result |
|---|---|
| `loco_results.csv` (27 rows: AUC, CI, permutation p) | identical |
| `rarefaction_sensitivity.csv`, `depth_match_results.csv`, `score_depth_correlation.csv`, `loco_sibling_concordance.csv` | identical |
| `domain_shift_diagnostics.csv` | within 0.0003 |
| `technical_metadata_null.csv`, cross-cohort rows | identical |
| Within-David grouped 5-fold rows (`david_grouped_results.csv` and the matching rows above) | **differ** |

The within-David differences, rerun against submitted:
- metadata only: 0.660 against 0.652;
- abundance: 0.529 against 0.439;
- combined: 0.535 against 0.453;
- microbiome plus metadata: 0.561 against 0.486.

The likely cause is `StratifiedGroupKFold(shuffle=True)` assigning sibling groups to folds differently across scikit-learn versions; its requirements give only ranges (>=1.3,<2), and this laptop has 1.7.2. This is not leakage. It shows the within-David microbiome estimate moves by about 0.09 with fold assignment alone, so neither value should be treated as precise. In both runs, the microbiome does not beat sex and age alone.

**Leakage review.** No issues.
- The prevalence filter and the network neighbour weights are fitted on the training cohorts only.
- C is chosen by inner leave-one-source-cohort-out.
- The nested permutation null re-chooses C on permuted labels, and David's labels are permuted within sibling pairs.
- The headline (abundance, C = 0.01) was declared before running and has its own null.
- The depth-matched analysis uses test labels only to define a post-hoc evaluation subset, and says so.
- Holdout prediction code exists but was not run (no holdout file).

**Headline confirmed:**
- Abundance at C = 0.01: Ding 0.470, Zou 0.573, David 0.551. None is convincing against its null.
- Best exploratory result: network, David 0.618 (raw p = 0.010; Holm across 9 comparisons, p = 0.09).

**Questions for the referee** (from `QUESTIONS.md`): settle David's control sex coding from the paper; provide a shared sample-overlap audit before the final holdout.
