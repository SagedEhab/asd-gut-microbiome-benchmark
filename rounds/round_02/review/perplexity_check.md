# Referee check of Perplexity round 2 (done by Claude, a contestant; for the human referee to accept or reject)

**Reproduction.** The four steps of `code/run.sh` (`run_all.py`, `within.py`, `zou.py`, `summarise.py`) were rerun unchanged on `data/train`, with `python -I` and Windows paths (the script itself calls `python3`, which this laptop lacks). Environment here: Python 3.10.8, scikit-learn 1.7.2, pandas 2.3.3, numpy 2.2.6. Perplexity pinned Python 3.14.8, scikit-learn 1.9.1, pandas 3.1.1, numpy 2.5.4. Total run time about 10 minutes.

| Output | Result |
|---|---|
| Held-out AUCs in `loco_results.csv`, all `oof_scores.csv`, `harmonisation_log.csv`, `depth_by_label.csv` | identical |
| Numeric values in `zou_diagnostics.csv` | identical (only the quoted null ranges in the notes differ, as below) |
| Permutation p-values and null ranges (`loco_results.csv`, `c_sensitivity.csv`) | differ by up to 0.08; same conclusions |
| Within-cohort CV (`within_cohort_results.csv`, `david_delta.csv`) | **differ**, by up to 0.22 in AUC |

**Headline confirmed.** Mean held-out AUC 0.583 is identical; its permutation p is 0.216 in the rerun against 0.205 submitted. Without Zou: 0.544, p 0.318 against 0.343. Fails the preregistered rule either way.

**Best secondary result confirmed.** Network → David 0.617, p 0.008 in both runs; Holm 0.70 (LOCO family) or 0.78 (all 105). Network → Zou 0.845, p 0.034 against 0.031. Secondary tests with raw p < 0.05: 14 in the rerun against 15 submitted; none survives Holm in either.

**Within-cohort differences**, submitted against rerun:
- Ding abundance 0.937 → 0.948; Zou abundance 0.996 → 0.997. The "within-cohort fits reach 0.94–0.996" claim holds.
- Zou depth only 0.873 → 0.655; Ding depth only 0.563 → 0.491.
- **David metadata (sex + age) 0.603, p 0.010 → 0.552, p 0.094.** With control sex swapped: 0.521 → 0.506.
- David microbiome 0.492 → 0.510; combined 0.507 → 0.509. Adding the microbiome to metadata: −0.096 (CI −0.22 to 0.03) → −0.043 (CI −0.16 to 0.08).

**Likely causes (not confirmed: the pinned versions need Python ≥ 3.11 and were not installed here).**
- Within-cohort: `StratifiedGroupKFold(shuffle=True)` assigns sibling groups to folds differently across scikit-learn versions, as with ChatGPT; only 2 repeats are averaged, so fold luck is not smoothed out. Pooling out-of-fold scores across folds also makes a one-feature model (depth only) sensitive to per-fold intercepts.
- Permutation nulls: `permute_labels` iterates `value_counts()` groups, whose tie order can change between pandas versions, giving different permuted label sets from the same seed.

Neither is leakage. Both show the within-David numbers (from every agent) carry roughly ±0.05–0.09 of fold noise, so "metadata 0.60" in Perplexity's answer should be read as 0.55–0.60, and "the microbiome adds nothing beyond sex and age" holds in both runs.

**Leakage review.** No issues.
- Vocabulary (≥10% prevalence in every training cohort), CLR, z-scoring, network correlations, Louvain modules, module signs and hub choice are all fitted on training rows only (`Featuriser.fit`), separately for every outer and inner fold.
- C is chosen by inner leave-one-training-cohort-out; ties go to the smaller C, as preregistered.
- Every permutation refits the full pipeline with re-chosen C on training labels shuffled within cohort and within sibling families, and is scored against the true held-out labels.
- Depth matching uses held-out labels only to choose an evaluation subset, and says so.
- Rarefaction is per sample and label-free.
- `zou.py` uses public ENA run metadata for the Zou and Ding training cohorts only; it is descriptive and feeds no model.
- No holdout predictions (no holdout file).

**Presentation notes for the referee.**
- `answer.md` reports Zou's depth, submission order and distance-to-training separations as 0.93, 0.96 and 0.92. The computed AUCs are 0.072, 0.039 and 0.077 (ASD positive); the answer gives 1 − AUC, i.e. how well each separates the groups. The direction is stated in `zou_diagnostics.csv`.
- `PREREGISTRATION.md`'s timestamp and hash are self-reported; the run log discloses that all of round 1 was read first.
- `RUN_LOG.md` claims byte-identical reproduction in Perplexity's own environment. Here, with other library versions, the held-out results reproduce exactly and the within-cohort CV does not.
