# Referee check of Perplexity round 1 (done by Claude; for the human referee to accept or reject)

**Reproduction:** rerunning `code/run_all.py --perm 200` and `code/diagnostics.py` on `data/` reproduced:
- every logistic-regression leave-one-cohort-out AUC and every permutation p-value (the primary analyses);
- `depth_by_label.csv` exactly.

The secondary random-forest AUCs differ by up to 0.033, and the within-David metadata-only AUC is 0.660 against 0.644 submitted. The submission pins library versions newer than this laptop's (numpy 2.5, pandas 3.1, scikit-learn 1.9, against 2.2, 2.3 and 1.7 here), so these small differences are expected.

**Leakage review:**
- The prevalence filter (at least 10% in every training cohort), the scaling and the correlation network are fitted on training rows only.
- C is chosen by inner leave-one-training-cohort-out.
- The permutation null refits the full pipeline.
- The per-cohort standardisation variant uses held-out *features* (not labels) and says so.
- Holdout predictions, written only if the holdout file exists, use a fixed C = 0.01 and no labels.
- David's metadata baseline excludes incomplete rows rather than encoding missingness.
- No leakage found.

**Its depth finding, confirmed independently:**
- In Zou, depth-for-ASD AUC is 0.072 (that is, 0.93 with controls deeper); raw input reads give 0.23 (that is, 0.77).
- Ding shows a smaller depth difference (AUC 0.65, p = 0.005).
- David shows none (0.50).

**Its David sex-coding question:** `labels.tsv` matches the authors' metadata file. Whether the paper's text disagrees is not verified by the referee.
