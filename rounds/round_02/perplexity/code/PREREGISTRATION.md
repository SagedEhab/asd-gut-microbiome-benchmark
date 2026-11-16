# Prespecified headline (written 2026-11-12, before any round-2 model was run)

**Headline model (the only primary result):**
- **Features.** Abundance only. Genera keyed by **family|genus**: the last `f__` and `g__` fields of the SILVA lineage, lower-cased. Columns with no genus (`;__` or stopping above genus) are dropped as features. Counts of identical keys are summed.
- **Vocabulary.** Genera with non-zero counts in ≥10% of samples in **every** training cohort of the split.
- **Transform.** Per-sample CLR over the vocabulary with pseudocount 0.5 on raw counts, then z-scoring with the training-row mean and SD.
- **Model.** L2 logistic regression with C chosen from {0.001, 0.01, 0.1, 1} by inner leave-one-training-cohort-out mean AUC. Ties go to the smaller C.
- **Samples.** No rarefaction, no per-cohort scaling, no metadata.
- **Evaluation.** Leave-one-cohort-out over Ding, Zou and David. David stays whole, so sibling pairs are never split.

**Headline statistic:**
- The **mean of the three held-out-cohort AUCs**.
- One-sided permutation p from **1,000** full-pipeline permutations. Training labels are shuffled within each training cohort (and within sibling pairs in David), and C is re-chosen in every permutation.
- Per-cohort AUCs, with sibling-grouped bootstrap 95% CIs, are reported next to it.

**Decision rule (stated in advance):**
- The headline counts as evidence of cross-cohort signal only if:
  - permutation p < 0.05 for the mean AUC; and
  - the result still holds when Zou is excluded (mean of Ding and David), because of the known Zou depth confound.
- Everything else is secondary and is reported with Holm-adjusted p-values. This includes network and combined features, the genus-name-only key, rarefied data, technical baselines, the within-David models, and per-C results.
