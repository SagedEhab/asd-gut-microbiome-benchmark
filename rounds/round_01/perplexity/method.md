# Method, Track A, round 1 (Perplexity)

Research-use classification of sampled ASD and control children. This is not a diagnostic tool.

**Reproduce:**

```
pip install -r code/requirements.txt
bash code/run.sh <repo>/data
```

- Python 3.12 (tested).
- Seed 20261112, used for permutations, bootstraps, random forests and Louvain.
- About 12 minutes on 2 CPU cores. Rerunning from a clean directory reproduced every LOCO AUC and CI exactly. The within-David bootstrap CIs share the RNG stream after the permutations, so they reproduce exactly only with the default `--perm 200`.
- Writes `loco_results.csv`, `harmonisation_log.csv` and `depth_by_label.csv`, plus `predictions.csv` when `data/holdout/genus_counts.tsv` exists.
- The holdout file did not exist on 2026-11-12, so **no predictions.csv was produced this round.**

## Data handling
- **Genus harmonisation** (`genus_key`). The genus is the last field of the SILVA lineage, which must start with `g__`. It is lower-cased, spaces become `_`, and brackets are removed. Ambiguous names (uncultured, unidentified, metagenome, `*_bacterium`, incertae_sedis) are qualified by family, e.g. `lachnospiraceae|uncultured`. Columns that map to the same key are summed. Result: 392 (Ding), 222 (Zou) and 359 (David) genera, of which 175 are shared by all three (`harmonisation_log.csv`).
- **Unassigned reads (RULES 12).** Columns ending in `;__` or stopping above genus are **dropped as features**. They are about 2.4–2.7% of reads per cohort. Their reads **stay in the denominator**: relative abundance = genus reads / all reads. There is no renormalisation.
- **Transform.** log10(proportion + 1e-5).
- **Training-cohort scaling** (primary analysis). z-score using the training cohorts' mean and SD only.
- **Per-cohort scaling** (secondary, `per_cohort_std=True`). Each cohort, including the test cohort, is z-scored on its own features. This uses **test-cohort features (never labels)**, and the results are reported separately.

## Validation
- **Outer loop: leave-one-cohort-out (LOCO).** Train on two cohorts and test on the third, for all three.
- **Sibling grouping.** In David, siblings share a group id (`sibling_pair`). LOCO never splits a cohort. The bootstrap CIs (2,000 resamples) resample **sibling groups**, and the within-David CV uses GroupKFold on the same groups.
- **Fitted on training rows only, inside every outer fold:**
  - prevalence filter (≥10% non-zero in **every** training cohort);
  - scaling;
  - co-occurrence network;
  - modules;
  - hub set;
  - model;
  - hyperparameter C.
- **Hyperparameter C** (L2 logistic regression, grid 0.001–1). Chosen by an **inner leave-one-training-cohort-out** loop, so test-cohort labels are never used. The random forest has fixed settings (500 trees, min_samples_leaf = 3, balanced class weights), with no tuning.

## Feature sets (identical outer splits)
1. **abundance**: all filtered log-abundances.
2. **network**:
   - The network is built from training samples only. Its edge weight is the mean of the within-training-cohort Spearman correlations, which avoids batch-driven edges. An edge is kept if |ρ| ≥ 0.3.
   - Louvain modules (≥3 genera) are scored per child as the sign-aligned mean z-score. The signs come from the training first principal component.
   - Per-child summaries: fraction of training hubs present, degree-weighted presence, and "coherence" (z′ρz) with the training correlation matrix.
   - A new child is scored against the **training reference network only**.
3. **combined**: 1 + 2.

## Baselines and controls
- **depth_only**: log10 total reads (a technical/batch baseline), run through the same LOCO.
- **metadata_only (sex, age)**: only David has these. Within-David 5-fold sibling-grouped CV, on **complete cases only** (n = 107). The 8 children with missing sex are all controls, so encoding missingness would leak the label. abundance and abundance+metadata are run on the same splits (C fixed at 0.1).
- **Label-permutation null**: 200 permutations for each logistic-regression feature set and test cohort (9 settings). Training labels are permuted within cohort, and the **whole pipeline is refitted**: filter, network, inner C search and model. Each permuted model is scored against the **true** test labels. p = (1 + #null ≥ observed) / 201.

## Results (`loco_results.csv`)

LOCO AUC with sibling-grouped bootstrap 95% CI, L2 logistic regression, training-cohort scaling:

| Test cohort | abundance | network | combined | depth only |
|---|---|---|---|---|
| Ding (V4, n = 122) | 0.51 (0.40–0.61), p = 0.52 | 0.48 (0.38–0.58), p = 0.60 | 0.51 (0.40–0.61), p = 0.50 | 0.35 |
| Zou (V3–V4, n = 92) | 0.71 (0.59–0.81), p = 0.17 | 0.73 (0.62–0.82), p = 0.19 | 0.71 (0.60–0.80), p = 0.14 | 0.07 |
| David (V4, siblings, n = 117) | 0.58 (0.51–0.66), p = 0.08 | 0.58 (0.50–0.67), p = 0.025 | 0.58 (0.51–0.65), p = 0.10 | 0.51 |
| Mean of 3 | 0.60 | 0.60 | 0.60 | 0.31 |

- **Random forest.** Mean LOCO AUC 0.45 (abundance), 0.62 (network) and 0.50 (combined). For Ding and Zou the random forest was worse than logistic regression or close to chance. The exception is network features for Zou (0.72).
- **Per-cohort scaling.** No improvement; mean 0.57–0.60.
- **Within David** (complete cases, n = 107): metadata-only AUC **0.64 (0.54–0.74)**, abundance 0.48 (0.38–0.59), abundance + metadata 0.52 (0.43–0.61).
- **Sibling-pair concordance** in David LOCO: across 55 discordant pairs, the ASD child scored higher than their sibling 0.56 of the time (abundance) and 0.58 (network). Chance is 0.5.

## Interpretation
- **Ding.** Transfer is at chance for every feature set. The published within-cohort AUC is 0.94 (Ding et al. 2020).
- **Zou.** The AUC of about 0.71 is **not evidence of transferable ASD signal**:
  - Permuted-label models reach a 95th-percentile null AUC of 0.80–0.82 on Zou, so p is 0.14–0.19.
  - Sequencing depth alone separates Zou's ASD and control samples with AUC 0.93: median 32,168 reads for ASD vs 43,289 for controls, Mann–Whitney p = 1.6e-12 (`depth_by_label.csv`).
  - This points to case and control samples being processed in different batches. Any composition axis correlated with that batch "predicts" the label.
  - In Ding, depth gives AUC 0.65 and observed-genus richness 0.69, which is also a technical warning.
- **David.** This is the only cohort without a depth confound (depth AUC 0.50). It shows a weak signal: AUC 0.58, CI lower bound about 0.50, network p = 0.025. That p-value is one of 9 uncorrected tests; a Bonferroni threshold would be 0.0056. Sibling concordance is 0.56–0.58.
- **Network vs abundance.** No difference beyond uncertainty on identical splits.
- **Overall.** There is no evidence of an honest cross-cohort classifier this round. Mean LOCO AUC is about 0.60, and that mean is inflated by Zou's batch structure.
- **Metadata.** In David, sex and age predict the label better than the microbiome does (0.64 vs 0.48). ASD is male-skewed, and siblings differ in sex. Note also the possible swapped control sex coding (QUESTIONS.md).

## Holdout plan (pre-registered, not yet run)
If `data/holdout/genus_counts.tsv` appears, the script will:
- fit the **abundance, L2 logistic regression, C = 0.01** model on all three training cohorts, with training-only filter and scaling;
- use no holdout features for any fitting step;
- write `sample_id,score`.

C = 0.01 was fixed in advance, before seeing any holdout data. It sits in the middle of the low end of the inner-CV choices (0.001 was usually chosen). Given the results above, this model's holdout AUC is expected to be near 0.5.

## Limitations
- Only three cohorts, so each LOCO estimate has a CI about ±0.10 wide.
- Labels for Ding and Zou are provisional (taken from sample names).
- Different 16S regions (V4 vs V3–V4).
- No diet, stool-consistency or GI covariates.
- Genus-level 16S only.
