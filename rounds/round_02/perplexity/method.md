# Method, round 2 (Perplexity), Track A

Research use only: this is classification of sampled ASD and control children from public 16S data. It is not a diagnostic test and has not been clinically validated.

No holdout exists (`data/holdout/` is absent at repo HEAD e1c4754), so `predictions.csv` is not delivered. Holdout labels were not sought.

## 0. Prespecified headline (verbatim)

The block below was written to `PREREGISTRATION.md` at 2026-11-12 14:29:55 UTC, before any round-2 model was run. Its sha256 is `abc45b070c7d1980768c51df516679a452115a79a10f30e17130b9e71b535815`, and the file itself is in `code/`.

Caveat: I wrote it after seeing my own round-1 results, which came from a similar pipeline (log-proportion features, mean LOCO AUC about 0.60). So it is prespecified relative to round 2, not blind to the data.

How I apply the rule "still holds when Zou is excluded": the mean of the Ding and David AUCs must also have a permutation p below 0.05.

> # Prespecified headline (written 2026-11-12, before any round-2 model was run)
> 
> **Headline model (the only primary result):**
> - **Features.** Abundance only. Genera keyed by **family|genus**: the last `f__` and `g__` fields of the SILVA lineage, lower-cased. Columns with no genus (`;__` or stopping above genus) are dropped as features. Counts of identical keys are summed.
> - **Vocabulary.** Genera with non-zero counts in ≥10% of samples in **every** training cohort of the split.
> - **Transform.** Per-sample CLR over the vocabulary with pseudocount 0.5 on raw counts, then z-scoring with the training-row mean and SD.
> - **Model.** L2 logistic regression with C chosen from {0.001, 0.01, 0.1, 1} by inner leave-one-training-cohort-out mean AUC. Ties go to the smaller C.
> - **Samples.** No rarefaction, no per-cohort scaling, no metadata.
> - **Evaluation.** Leave-one-cohort-out over Ding, Zou and David. David stays whole, so sibling pairs are never split.
> 
> **Headline statistic:**
> - The **mean of the three held-out-cohort AUCs**.
> - One-sided permutation p from **1,000** full-pipeline permutations. Training labels are shuffled within each training cohort (and within sibling pairs in David), and C is re-chosen in every permutation.
> - Per-cohort AUCs, with sibling-grouped bootstrap 95% CIs, are reported next to it.
> 
> **Decision rule (stated in advance):**
> - The headline counts as evidence of cross-cohort signal only if:
>   - permutation p < 0.05 for the mean AUC; and
>   - the result still holds when Zou is excluded (mean of Ding and David), because of the known Zou depth confound.
> - Everything else is secondary and is reported with Holm-adjusted p-values. This includes network and combined features, the genus-name-only key, rarefied data, technical baselines, the within-David models, and per-C results.
> 

## 1. Result of the headline

| statistic | AUC | null mean [95% range] (1,000 perms) | one-sided p |
|---|---|---|---|
| **Mean of 3 LOCO AUCs (headline)** | **0.583** | 0.526 [0.402–0.649] | **0.205** |
| Mean excluding Zou (Ding, David) | 0.544 | 0.515 [0.393–0.634] | 0.343 |
| Ding | 0.500 [0.396–0.599] | 0.516 [0.291–0.732] | 0.572 |
| Zou | 0.662 [0.548–0.772] | 0.549 [0.257–0.833] | 0.256 |
| David | 0.587 [0.518–0.659] | 0.513 [0.417–0.606] | 0.079 |

**Decision:** the preregistered rule is **not met** (p = 0.205), so there is no evidence of cross-cohort signal under the headline model.

**Sensitivity:** at a fixed C = 1, the mean is 0.620 with fixed-C p = 0.017. That is the only C value where the result holds, and it was not the preregistered procedure. I report it as an isolated, single-setting result and do not count it.

## 2. Pipeline (all secondary models share it)

**Loading and harmonisation (`common.py`):**
- Columns with no genus (a last field that is not `g__` or is an empty `g__`) are dropped as features. They hold 2.4–2.7% of reads per cohort (`harmonisation_log.csv`). Depth still counts all reads.
- **Two keys are compared.**
  - `famgenus` (headline): the last `f__` field plus genus, lower-cased.
  - `genus`: the genus name only.
- **The keys differ only in `g__uncultured`.** It is the only genus name that occurs under more than one family across the three cohorts (35 families). The genus-only key pools all 35 into one feature, while family|genus keeps them apart. Ding has 392 vs 370 keys, Zou 222 vs 210, David 359 vs 341. All three cohorts share 175 vs 168 keys.

**Featurisation (`Featuriser`, fitted on training rows only):**
- Vocabulary: keys at ≥10% prevalence in every training cohort.
- Abundance: CLR with pseudocount 0.5, then training z-score.
- Network:
  - mean of within-training-cohort Spearman matrices; edges at |ρ| ≥ 0.3;
  - Louvain modules (seeded) of size ≥ 3, with module scores = signed PC1 loadings from training rows;
  - hub presence, weighted-degree presence and a coherence term;
  - all network features z-scored on training rows.
- Combined: abundance and network concatenated.

**Technical baselines:**
- `depth_only`: log10 total reads.
- `richness_only`: observed keys, computed after rarefying when the variant is rarefied.
- Each is a one-feature L2-LR fitted on the training cohorts. Under the null, a one-feature model can only produce AUC = a or 1−a, so its null is two-point and its one-sided p is not informative. The AUC itself, with the training-learned sign, is the useful number.

**Rarefied variants:** every sample is subsampled without replacement to 5,000 reads (seeded, label-free; minimum depth is 5,896). Depth-only is undefined after rarefying and is dropped.

**Model:** L2 logistic regression (lbfgs) with C ∈ {0.001, 0.01, 0.1, 1}. C is chosen by inner leave-one-training-cohort-out mean AUC; ties go to the smaller C.

**LOCO:** each of Ding, Zou and David is held out in turn. David is never split, so siblings stay together.

**Permutation null (FEEDBACK 1):**
- The full pipeline is rerun, including C selection, on labels shuffled within each training cohort.
- In David, labels are shuffled within sibling families, and singletons are shuffled among themselves. This is ChatGPT's round-1 idea.
- Label-free features are cached per split and reused, which is valid because they never see labels.
- AUC is always computed against the true held-out labels.
- Counts: 1,000 permutations for the `famgenus`-raw variant (every feature kind), and 200 for each other variant.
- p = (1 + #null ≥ obs) / (1 + n).

**Depth-matched check (FEEDBACK 8):**
- Each held-out cohort is also scored on a 1:1 depth-matched subset (log10 depth caliper 0.05) with its own matched null.
- Matching uses held-out labels only to choose which samples are evaluated, never to fit.
- Zou keeps only 24 of 92 samples.

**Within-cohort CV (`within.py`, FEEDBACK 6 and 8):**
- StratifiedGroupKFold(5) × 2 repeats; families are groups. Inner GroupKFold(3) chooses C.
- AUC = mean over repeats of the pooled out-of-fold AUC.
- The vocabulary (≥10% prevalence in training rows), CLR and scaling are refit per fold.
- The null uses the same fixed splits, 200 within-family permutations, and C re-chosen each time.
- Because fold-wise sign flips are pooled, null means fall below 0.5 (about 0.4 for one-feature models). The comparison with the null remains valid.
- David is restricted to complete cases: n = 107, after dropping 8 controls missing sex and 2 missing age. Missingness is never encoded.

## 3. Multiplicity (FEEDBACK 3)

Held-out comparisons with a permutation p: 106 = 1 headline + 105 secondary (89 LOCO, 16 within-cohort). Per-C sensitivity rows (descriptive, fixed-C p): 424. Secondary raw p<0.05: 15; Holm-adjusted p<0.05: 0.

- Holm is applied once across all 105 secondary permutation p-values (`multiplicity.csv`).
- With 200 permutations the smallest attainable p is 0.005, and 0.005 × 105 > 0.05. Even the obviously strong within-cohort fits (Ding 0.94, Zou 0.996) cannot survive Holm. This is a resolution limit, not evidence against them.
- The 1,000-permutation `famgenus` rows have a floor of 0.001.

**Strongest secondary cross-cohort results:**
- network → David: 0.617, p = 0.008, Holm 0.78.
- network → Zou: 0.845, p = 0.031, Holm 1.0, flagged † because fixed-C p < 0.05 at only 1 of 4 C values.

No secondary result survives Holm.

## 4. Hyperparameter sensitivity (FEEDBACK 2)

- Every LOCO row in the table below shows the AUC at all four C values. `c_sensitivity.csv` adds a fixed-C null 97.5th percentile and fixed-C p for every row (360 rows); `within_c_sensitivity.csv` does the same for the within-cohort models (64 rows).
- **†** marks a result whose chosen-C p is < 0.05 while fixed-C p < 0.05 at ≤ 1 of the 4 C values.
- The headline mean reaches fixed-C p < 0.05 only at C = 1.

**Sensitivity of the network results:**
- network → David holds at C = 0.001, 0.01 and 0.1 (fixed-C p 0.008, 0.006, 0.043), not at C = 1 (0.10).
- network → Zou holds only at C = 0.001 in the `famgenus` raw variant. It holds at all 4 C values in both rarefied variants and at 2 of 4 with the genus key.

## 5. Zou (FEEDBACK 4), from `zou.py` → `zou_diagnostics.csv`

No score was re-signed after seeing its direction. Label-free PCs are reported as computed, with |AUC − 0.5| next to each because the sign of a PC is arbitrary.

**Depth / batch:**
- Processed depth gives AUC 0.072, i.e. controls are deeper (median 43,289 vs 32,168).
- Raw ENA read count gives 0.225.
- The fraction of raw reads retained after processing gives 0.322 (median 0.545 ASD vs 0.650 control).
- **Run accession number gives 0.039.** ENA library names are literally "case…" and "control…", so cases and controls were submitted as near-separate blocks. I cannot tell from ENA whether they were also sequenced on separate runs, but the data are consistent with case/control being confounded with a processing or submission batch.

**16S region:**
- All 92 Zou runs are MiSeq paired, about 592 bases per spot. Peralta-Marzal 2024 (full text, Track B 1.4) states Zou = V3–V4 and Ding = V4; David 2021 states V4.
- Region is constant within Zou, so it cannot create Zou's internal case/control separation. It can, however, change which genera are recovered and therefore whether a direction learned on V4 transfers.
- The fraction of Zou genus-assigned reads in keys shared with Ding+David is about 99.5% in both groups (AUC 0.63), so harmonisation does not discard a label-dependent share of reads.

**Overall composition:**
- Zou's label-free PC1 (17.6% of variance) has AUC 0.132 (|AUC − 0.5| = 0.37) and Spearman 0.49 with log depth. PC1 after rarefying to 5,000 reads gives 0.116, so the shift survives rarefaction.
- Aitchison distance of each Zou sample to the Ding+David centroid, a label-free score, has **AUC 0.077**: Zou controls sit much further from the other cohorts than Zou ASD samples do. This is a large, label-aligned overall composition shift.
- Across 118 genera, the ASD effect correlates with the depth sensitivity estimated in controls at Spearman −0.36.

**Within Zou:**
- Depth-only CV AUC 0.873; microbiome CV AUC 0.996 raw and 0.988 rarefied.
- Richness is not involved: observed genera AUC 0.49 raw and 0.52 rarefied.

**LOCO scores vs depth:**

| variant / features | Zou AUC | Spearman(score, log depth) | AUC of depth-residualised score |
|---|---|---|---|
| famgenus / abundance | 0.662 | −0.08 | 0.636 |
| famgenus / network | 0.845 | −0.38 | 0.699 |
| famgenus rarefied / abundance | 0.426 | 0.23 | 0.530 |
| famgenus rarefied / network | 0.770 | −0.29 | 0.668 |
| genus / abundance | 0.761 | −0.25 | 0.657 |
| genus / network | 0.836 | −0.35 | 0.704 |

**Why submissions disagree on Zou:** the LOCO null for Zou is very wide (abundance 0.257–0.833; network 0.209–0.850). Any single Zou AUC between about 0.25 and 0.85 is compatible with shuffled training labels, so round-1 values of 0.27, 0.70 and 0.77 are all within noise.

**Verdict:**
- Zou's case/control separation is real inside Zou, but it is aligned with a depth/processing difference and with a block-wise submission order.
- The same network direction that scores Zou at 0.84 scores Ding at 0.41 (0.33 rarefied).
- I therefore read Zou's separation as **cohort structure (batch-confounded), not demonstrated ASD signal**. The data cannot exclude some ASD contribution, but nothing here isolates one.

## 6. David: metadata vs microbiome (FEEDBACK 6, 9); sex results PROVISIONAL

Complete cases: n = 107 (60 ASD, 47 controls), 47 discordant families.

| model (within-David CV) | AUC | null 95% range | p | sibling concordance (47 families), p |
|---|---|---|---|---|
| metadata (sex, age) | 0.603 | 0.399–0.568 | 0.010 | 0.750, p < 0.001 |
| microbiome (CLR abundance) | 0.492 | 0.396–0.609 | 0.527 | 0.479, p = 0.67 |
| combined | 0.507 | 0.388–0.609 | 0.413 | 0.479, p = 0.67 |
| metadata, control sex swapped m↔f | 0.521 | 0.398–0.561 | 0.169 | — |

**Does the microbiome add anything beyond sex and age? No:**
- Δ AUC (combined − metadata) = −0.096 (family-bootstrap 95% CI −0.219 to 0.031).
- Conditional null: microbiome rows were shuffled within sex × age-tertile strata and the combined model refit, 100 times. It gave mean Δ −0.078 and 97.5th percentile 0.022, so p = 0.61.
- The microbiome score is also at chance within each sex: 0.47 in males and 0.58 in females.

**The metadata AUC depends on the disputed sex coding.** With control sex swapped to match the paper's text (Track B), it falls to 0.52 (p = 0.17). It is provisional.

**Sibling-pair test of the LOCO models** (trained on Ding+Zou, scored on all 117 David samples, 55 discordant families; fraction of ASD-vs-sibling comparisons in which the ASD child scores higher; sign-flip p):

| model | concordance | 95% CI | p |
|---|---|---|---|
| abundance (headline model) | 0.564 | 0.436–0.691 | 0.21 |
| network | 0.582 | — | 0.14 |
| combined | 0.582 | — | 0.14 |
| genus-key network | 0.618 | — | 0.053 |
| rarefied variants | 0.46–0.55 | — | — |

None is significant.

## 7. Technical baselines in every cohort (FEEDBACK 8)

| cohort | depth: AUC by label | richness: AUC by label | LOCO depth-only | LOCO richness-only | within-CV depth-only | within-CV richness (rarefied) | within-CV microbiome raw / rarefied |
|---|---|---|---|---|---|---|---|
| Ding | 0.651 | 0.691 | 0.349 | 0.690 | 0.563 | 0.571 | 0.937 / 0.909 |
| Zou | 0.072 | 0.479 | 0.072 | 0.493 | 0.873 | 0.436 | 0.996 / 0.988 |
| David | 0.495 | 0.504 | 0.505 | 0.496 | 0.488 | 0.461 | 0.492 / 0.519 |

**Reading:**
- Within Ding and Zou, the microbiome fits far exceed the depth and richness baselines, but those fits do not transfer (Section 1).
- In LOCO, richness-only scores Ding at 0.69, higher than any LOCO microbiome model for Ding. Its null is two-point, so it is not testable.
- Rarefying moves the cross-cohort abundance results down (headline-equivalent mean 0.487, p = 0.78).

## 8. Leakage audit

- Vocabulary, CLR, scaling, network edges, modules, signs, hubs and rarefaction are label-free and fitted on training rows only, per split.
- C is chosen on training cohorts (LOCO) or on inner folds (within-cohort).
- The held-out cohort's labels are used only to compute AUC and to pick the depth-matched evaluation subset.
- No holdout data were touched.

## 9. Full tables

### LOCO, all variants (chosen C; null = full pipeline on within-training-cohort shuffled labels)

| variant | features | test | AUC [group-bootstrap 95% CI] | null mean [95% range] | one-sided p | Holm (all 105 secondary) | n perms | C chosen | AUC at C = 0.001 / 0.01 / 0.1 / 1 | depth-matched AUC (n), p |
|---|---|---|---|---|---|---|---|---|---|---|
| famgenus | abundance | ding | 0.500 [0.396–0.599] | 0.516 [0.291–0.732] | 0.572 | 1.000 | 1000 | 0.001 | 0.500 / 0.535 / 0.598 / 0.674 | 0.591 (84), 0.295 |
| famgenus | abundance | zou | 0.662 [0.548–0.772] | 0.549 [0.257–0.833] | 0.256 | 1.000 | 1000 | 1.0 | 0.747 / 0.676 / 0.643 / 0.662 | 0.743 (24), 0.182 |
| famgenus | abundance | david | 0.587 [0.518–0.659] | 0.513 [0.417–0.606] | 0.079 | 1.000 | 1000 | 0.001 | 0.587 / 0.547 / 0.525 / 0.524 | 0.548 (96), 0.309 |
| famgenus | abundance | mean | 0.583 | 0.526 [0.402–0.649] | 0.205 | headline | 1000 |  | 0.611 / 0.586 / 0.589 / 0.620 |  |
| famgenus | abundance | mean_ex_zou | 0.544 | 0.515 [0.393–0.634] | 0.343 | 1.000 | 1000 |  | 0.544 / 0.541 / 0.562 / 0.599 |  |
| famgenus | network | ding | 0.407 [0.309–0.508] | 0.500 [0.291–0.699] | 0.790 | 1.000 | 1000 | 0.01 | 0.417 / 0.407 / 0.382 / 0.341 | 0.491 (84), 0.604 |
| famgenus | network | zou | 0.845 [0.759–0.914] † | 0.563 [0.209–0.850] | 0.031 | 1.000 | 1000 | 0.001 | 0.845 / 0.808 / 0.715 / 0.670 | 0.972 (24), 0.015 |
| famgenus | network | david | 0.617 [0.533–0.694] | 0.513 [0.414–0.611] | 0.008 | 0.784 | 1000 | 0.001 | 0.617 / 0.623 / 0.597 / 0.573 | 0.600 (96), 0.089 |
| famgenus | network | mean | 0.623 | 0.526 [0.379–0.655] | 0.091 | 1.000 | 1000 |  | 0.626 / 0.612 / 0.565 / 0.528 |  |
| famgenus | network | mean_ex_zou | 0.512 | 0.507 [0.390–0.615] | 0.465 | 1.000 | 1000 |  | 0.517 / 0.515 / 0.489 / 0.457 |  |
| famgenus | combined | ding | 0.483 [0.381–0.584] | 0.514 [0.291–0.729] | 0.606 | 1.000 | 1000 | 0.001 | 0.483 / 0.529 / 0.602 / 0.684 | 0.587 (84), 0.311 |
| famgenus | combined | zou | 0.614 [0.502–0.727] | 0.550 [0.246–0.837] | 0.360 | 1.000 | 1000 | 1.0 | 0.757 / 0.689 / 0.622 / 0.614 | 0.674 (24), 0.322 |
| famgenus | combined | david | 0.595 [0.522–0.667] | 0.512 [0.419–0.607] | 0.054 | 1.000 | 1000 | 0.001 | 0.595 / 0.554 / 0.522 / 0.525 | 0.558 (96), 0.254 |
| famgenus | combined | mean | 0.564 | 0.525 [0.395–0.649] | 0.290 | 1.000 | 1000 |  | 0.612 / 0.591 / 0.582 / 0.608 |  |
| famgenus | combined | mean_ex_zou | 0.539 | 0.513 [0.383–0.633] | 0.345 | 1.000 | 1000 |  | 0.539 / 0.541 / 0.562 / 0.605 |  |
| famgenus | depth_only | ding | 0.349 [0.249–0.451] | 0.467 [0.349–0.651] | 1.000 | 1.000 | 1000 | 0.001 | 0.349 / 0.349 / 0.349 / 0.349 | 0.490 (84), 1.000 |
| famgenus | depth_only | zou | 0.072 [0.017–0.142] | 0.101 [0.072–0.928] | 1.000 | 1.000 | 1000 | 0.001 | 0.072 / 0.072 / 0.072 / 0.072 | 0.493 (24), 1.000 |
| famgenus | depth_only | david | 0.505 [0.454–0.556] | 0.500 [0.495–0.505] | 0.506 | 1.000 | 1000 | 0.001 | 0.505 / 0.505 / 0.505 / 0.505 | 0.490 (96), 1.000 |
| famgenus | depth_only | mean | 0.308 | 0.356 [0.305–0.594] | 0.763 | 1.000 | 1000 |  | 0.308 / 0.308 / 0.308 / 0.308 |  |
| famgenus | depth_only | mean_ex_zou | 0.427 | 0.483 [0.422–0.578] | 0.763 | 1.000 | 1000 |  | 0.427 / 0.427 / 0.427 / 0.427 |  |
| famgenus | richness_only | ding | 0.690 [0.590–0.782] | 0.516 [0.310–0.690] | 0.543 | 1.000 | 1000 | 0.001 | 0.690 / 0.690 / 0.690 / 0.690 | 0.609 (84), 0.543 |
| famgenus | richness_only | zou | 0.493 [0.377–0.613] | 0.493 [0.493–0.493] | 1.000 | 1.000 | 1000 | 0.001 | 0.493 / 0.493 / 0.493 / 0.493 | 0.708 (24), 0.987 |
| famgenus | richness_only | david | 0.495 [0.404–0.589] | 0.496 [0.495–0.495] | 1.000 | 1.000 | 1000 | 0.001 | 0.495 / 0.495 / 0.495 / 0.495 | 0.525 (96), 0.981 |
| famgenus | richness_only | mean | 0.559 | 0.502 [0.433–0.559] | 0.543 | 1.000 | 1000 |  | 0.559 / 0.559 / 0.559 / 0.559 |  |
| famgenus | richness_only | mean_ex_zou | 0.593 | 0.506 [0.403–0.593] | 0.543 | 1.000 | 1000 |  | 0.593 / 0.593 / 0.593 / 0.593 |  |
| genus | abundance | ding | 0.489 [0.386–0.590] | 0.516 [0.291–0.721] | 0.612 | 1.000 | 200 | 0.001 | 0.489 / 0.480 / 0.523 / 0.595 | 0.579 (84), 0.323 |
| genus | abundance | zou | 0.761 [0.658–0.848] | 0.546 [0.263–0.845] | 0.119 | 1.000 | 200 | 0.001 | 0.761 / 0.673 / 0.641 / 0.621 | 0.833 (24), 0.040 |
| genus | abundance | david | 0.585 [0.511–0.657] | 0.515 [0.414–0.612] | 0.110 | 1.000 | 200 | 0.001 | 0.585 / 0.537 / 0.520 / 0.518 | 0.545 (96), 0.303 |
| genus | abundance | mean | 0.612 | 0.526 [0.406–0.657] | 0.085 | 1.000 | 200 |  | 0.612 / 0.563 / 0.561 / 0.578 |  |
| genus | abundance | mean_ex_zou | 0.537 | 0.515 [0.400–0.627] | 0.393 | 1.000 | 200 |  | 0.537 / 0.508 / 0.521 / 0.556 |  |
| genus | network | ding | 0.455 [0.352–0.559] | 0.485 [0.296–0.683] | 0.592 | 1.000 | 200 | 0.01 | 0.461 / 0.455 / 0.420 / 0.365 | 0.527 (84), 0.368 |
| genus | network | zou | 0.836 [0.746–0.909] | 0.545 [0.284–0.790] | 0.010 | 0.970 | 200 | 0.01 | 0.837 / 0.836 / 0.756 / 0.714 | 0.938 (24), 0.040 |
| genus | network | david | 0.611 [0.531–0.692] | 0.519 [0.414–0.610] | 0.020 | 1.000 | 200 | 0.001 | 0.611 / 0.606 / 0.570 / 0.532 | 0.601 (96), 0.119 |
| genus | network | mean | 0.634 | 0.516 [0.392–0.624] | 0.020 | 1.000 | 200 |  | 0.636 / 0.633 / 0.582 / 0.537 |  |
| genus | network | mean_ex_zou | 0.533 | 0.502 [0.398–0.618] | 0.298 | 1.000 | 200 |  | 0.536 / 0.531 / 0.495 / 0.449 |  |
| genus | combined | ding | 0.482 [0.382–0.583] | 0.514 [0.298–0.713] | 0.622 | 1.000 | 200 | 0.001 | 0.482 / 0.477 / 0.523 / 0.601 | 0.579 (84), 0.303 |
| genus | combined | zou | 0.773 [0.673–0.866] | 0.544 [0.254–0.851] | 0.104 | 1.000 | 200 | 0.001 | 0.773 / 0.683 / 0.627 / 0.608 | 0.833 (24), 0.060 |
| genus | combined | david | 0.589 [0.517–0.662] | 0.513 [0.412–0.611] | 0.100 | 1.000 | 200 | 0.001 | 0.589 / 0.539 / 0.518 / 0.515 | 0.549 (96), 0.303 |
| genus | combined | mean | 0.615 | 0.524 [0.408–0.641] | 0.090 | 1.000 | 200 |  | 0.615 / 0.566 / 0.556 / 0.575 |  |
| genus | combined | mean_ex_zou | 0.535 | 0.514 [0.400–0.624] | 0.388 | 1.000 | 200 |  | 0.535 / 0.508 / 0.520 / 0.558 |  |
| genus | depth_only | ding | 0.349 [0.249–0.452] | 0.462 [0.349–0.651] | 1.000 | 1.000 | 200 | 0.001 | 0.349 / 0.349 / 0.349 / 0.349 | 0.490 (84), 1.000 |
| genus | depth_only | zou | 0.072 [0.021–0.141] | 0.106 [0.072–0.928] | 1.000 | 1.000 | 200 | 0.001 | 0.072 / 0.072 / 0.072 / 0.072 | 0.493 (24), 1.000 |
| genus | depth_only | david | 0.505 [0.453–0.559] | 0.500 [0.495–0.505] | 0.527 | 1.000 | 200 | 0.001 | 0.505 / 0.505 / 0.505 / 0.505 | 0.490 (96), 1.000 |
| genus | depth_only | mean | 0.308 | 0.356 [0.305–0.594] | 0.776 | 1.000 | 200 |  | 0.308 / 0.308 / 0.308 / 0.308 |  |
| genus | depth_only | mean_ex_zou | 0.427 | 0.481 [0.422–0.578] | 0.776 | 1.000 | 200 |  | 0.427 / 0.427 / 0.427 / 0.427 |  |
| genus | richness_only | ding | 0.679 [0.572–0.773] | 0.532 [0.321–0.679] | 0.592 | 1.000 | 200 | 0.001 | 0.679 / 0.679 / 0.679 / 0.679 | 0.594 (84), 0.592 |
| genus | richness_only | zou | 0.504 [0.385–0.620] | 0.504 [0.504–0.504] | 0.990 | 1.000 | 200 | 0.001 | 0.504 / 0.504 / 0.504 / 0.504 | 0.712 (24), 0.990 |
| genus | richness_only | david | 0.499 [0.406–0.598] | 0.499 [0.499–0.499] | 1.000 | 1.000 | 200 | 0.001 | 0.499 / 0.499 / 0.499 / 0.499 | 0.526 (96), 0.995 |
| genus | richness_only | mean | 0.561 | 0.512 [0.442–0.561] | 0.592 | 1.000 | 200 |  | 0.561 / 0.561 / 0.561 / 0.561 |  |
| genus | richness_only | mean_ex_zou | 0.589 | 0.516 [0.410–0.589] | 0.592 | 1.000 | 200 |  | 0.589 / 0.589 / 0.589 / 0.589 |  |
| famgenus_rarefied | abundance | ding | 0.455 [0.353–0.561] | 0.516 [0.337–0.702] | 0.746 | 1.000 | 200 | 0.001 | 0.455 / 0.453 / 0.526 / 0.571 | 0.542 (84), 0.423 |
| famgenus_rarefied | abundance | zou | 0.425 [0.310–0.542] | 0.559 [0.241–0.851] | 0.791 | 1.000 | 200 | 1.0 | 0.714 / 0.599 / 0.517 / 0.425 | 0.660 (24), 0.378 |
| famgenus_rarefied | abundance | david | 0.580 [0.508–0.651] | 0.518 [0.415–0.613] | 0.134 | 1.000 | 200 | 0.001 | 0.580 / 0.527 / 0.484 / 0.468 | 0.535 (96), 0.428 |
| famgenus_rarefied | abundance | mean | 0.487 | 0.531 [0.406–0.649] | 0.781 | 1.000 | 200 |  | 0.583 / 0.527 / 0.509 / 0.488 |  |
| famgenus_rarefied | abundance | mean_ex_zou | 0.517 | 0.517 [0.409–0.616] | 0.537 | 1.000 | 200 |  | 0.517 / 0.490 / 0.505 / 0.520 |  |
| famgenus_rarefied | network | ding | 0.332 [0.240–0.435] | 0.491 [0.320–0.677] | 0.960 | 1.000 | 200 | 0.001 | 0.332 / 0.339 / 0.355 / 0.374 | 0.377 (84), 0.900 |
| famgenus_rarefied | network | zou | 0.770 [0.673–0.865] | 0.500 [0.193–0.777] | 0.040 | 1.000 | 200 | 1.0 | 0.803 / 0.833 / 0.809 / 0.770 | 0.819 (24), 0.080 |
| famgenus_rarefied | network | david | 0.595 [0.517–0.679] | 0.528 [0.425–0.608] | 0.110 | 1.000 | 200 | 0.001 | 0.595 / 0.585 / 0.550 / 0.527 | 0.556 (96), 0.303 |
| famgenus_rarefied | network | mean | 0.566 | 0.507 [0.406–0.600] | 0.149 | 1.000 | 200 |  | 0.577 / 0.586 / 0.572 / 0.557 |  |
| famgenus_rarefied | network | mean_ex_zou | 0.463 | 0.510 [0.431–0.606] | 0.841 | 1.000 | 200 |  | 0.463 / 0.462 / 0.453 / 0.450 |  |
| famgenus_rarefied | combined | ding | 0.419 [0.317–0.522] | 0.515 [0.321–0.698] | 0.841 | 1.000 | 200 | 0.001 | 0.419 / 0.433 / 0.525 / 0.584 | 0.497 (84), 0.597 |
| famgenus_rarefied | combined | zou | 0.405 [0.293–0.521] | 0.553 [0.264–0.843] | 0.821 | 1.000 | 200 | 1.0 | 0.731 / 0.634 / 0.538 / 0.405 | 0.646 (24), 0.378 |
| famgenus_rarefied | combined | david | 0.577 [0.500–0.648] | 0.515 [0.414–0.607] | 0.159 | 1.000 | 200 | 0.001 | 0.577 / 0.529 / 0.483 / 0.459 | 0.529 (96), 0.423 |
| famgenus_rarefied | combined | mean | 0.467 | 0.528 [0.404–0.645] | 0.811 | 1.000 | 200 |  | 0.576 / 0.532 / 0.515 / 0.482 |  |
| famgenus_rarefied | combined | mean_ex_zou | 0.498 | 0.515 [0.407–0.617] | 0.637 | 1.000 | 200 |  | 0.498 / 0.481 / 0.504 / 0.521 |  |
| famgenus_rarefied | richness_only | ding | 0.696 [0.593–0.791] | 0.555 [0.304–0.696] | 0.642 | 1.000 | 200 | 0.001 | 0.696 / 0.696 / 0.696 / 0.696 | 0.641 (84), 0.642 |
| famgenus_rarefied | richness_only | zou | 0.520 [0.404–0.641] | 0.519 [0.520–0.520] | 0.990 | 1.000 | 200 | 0.001 | 0.520 / 0.520 / 0.520 / 0.520 | 0.705 (24), 0.990 |
| famgenus_rarefied | richness_only | david | 0.504 [0.407–0.597] | 0.504 [0.504–0.504] | 0.985 | 1.000 | 200 | 0.001 | 0.504 / 0.504 / 0.504 / 0.504 | 0.537 (96), 0.985 |
| famgenus_rarefied | richness_only | mean | 0.573 | 0.526 [0.443–0.573] | 0.632 | 1.000 | 200 |  | 0.573 / 0.573 / 0.573 / 0.573 |  |
| famgenus_rarefied | richness_only | mean_ex_zou | 0.600 | 0.529 [0.404–0.600] | 0.632 | 1.000 | 200 |  | 0.600 / 0.600 / 0.600 / 0.600 |  |
| genus_rarefied | abundance | ding | 0.460 [0.355–0.564] | 0.520 [0.302–0.717] | 0.692 | 1.000 | 200 | 0.001 | 0.460 / 0.458 / 0.512 / 0.551 | 0.552 (84), 0.448 |
| genus_rarefied | abundance | zou | 0.723 [0.613–0.823] | 0.549 [0.260–0.858] | 0.159 | 1.000 | 200 | 0.001 | 0.723 / 0.587 / 0.510 / 0.425 | 0.771 (24), 0.110 |
| genus_rarefied | abundance | david | 0.579 [0.503–0.653] | 0.521 [0.416–0.617] | 0.174 | 1.000 | 200 | 0.001 | 0.579 / 0.529 / 0.484 / 0.470 | 0.535 (96), 0.403 |
| genus_rarefied | abundance | mean | 0.587 | 0.530 [0.401–0.652] | 0.199 | 1.000 | 200 |  | 0.587 / 0.525 / 0.502 / 0.482 |  |
| genus_rarefied | abundance | mean_ex_zou | 0.519 | 0.521 [0.401–0.644] | 0.542 | 1.000 | 200 |  | 0.519 / 0.493 / 0.498 / 0.510 |  |
| genus_rarefied | network | ding | 0.417 [0.315–0.523] | 0.496 [0.352–0.657] | 0.756 | 1.000 | 200 | 1.0 | 0.355 / 0.366 / 0.395 / 0.417 | 0.487 (84), 0.547 |
| genus_rarefied | network | zou | 0.768 [0.666–0.863] | 0.480 [0.182–0.759] | 0.025 | 1.000 | 200 | 1.0 | 0.772 / 0.808 / 0.790 / 0.768 | 0.833 (24), 0.050 |
| genus_rarefied | network | david | 0.575 [0.493–0.659] | 0.525 [0.423–0.617] | 0.239 | 1.000 | 200 | 0.001 | 0.575 / 0.555 / 0.504 / 0.475 | 0.546 (96), 0.463 |
| genus_rarefied | network | mean | 0.587 | 0.500 [0.402–0.611] | 0.070 | 1.000 | 200 |  | 0.567 / 0.576 / 0.563 / 0.553 |  |
| genus_rarefied | network | mean_ex_zou | 0.496 | 0.510 [0.424–0.601] | 0.597 | 1.000 | 200 |  | 0.465 / 0.460 / 0.450 / 0.446 |  |
| genus_rarefied | combined | ding | 0.431 [0.330–0.529] | 0.520 [0.296–0.715] | 0.751 | 1.000 | 200 | 0.001 | 0.431 / 0.434 / 0.515 / 0.565 | 0.513 (84), 0.542 |
| genus_rarefied | combined | zou | 0.736 [0.633–0.836] | 0.542 [0.245–0.853] | 0.139 | 1.000 | 200 | 0.001 | 0.736 / 0.610 / 0.518 / 0.427 | 0.771 (24), 0.119 |
| genus_rarefied | combined | david | 0.574 [0.499–0.651] | 0.519 [0.414–0.613] | 0.174 | 1.000 | 200 | 0.001 | 0.574 / 0.524 / 0.472 / 0.454 | 0.530 (96), 0.448 |
| genus_rarefied | combined | mean | 0.580 | 0.527 [0.415–0.647] | 0.204 | 1.000 | 200 |  | 0.580 / 0.523 / 0.502 / 0.482 |  |
| genus_rarefied | combined | mean_ex_zou | 0.502 | 0.519 [0.403–0.644] | 0.607 | 1.000 | 200 |  | 0.502 / 0.479 / 0.493 / 0.509 |  |
| genus_rarefied | richness_only | ding | 0.677 [0.576–0.779] | 0.528 [0.323–0.677] | 0.582 | 1.000 | 200 | 0.001 | 0.677 / 0.677 / 0.677 / 0.677 | 0.612 (84), 0.582 |
| genus_rarefied | richness_only | zou | 0.533 [0.412–0.658] | 0.531 [0.531–0.533] | 0.975 | 1.000 | 200 | 0.001 | 0.533 / 0.533 / 0.533 / 0.533 | 0.733 (24), 0.975 |
| genus_rarefied | richness_only | david | 0.512 [0.411–0.609] | 0.511 [0.511–0.512] | 0.975 | 1.000 | 200 | 0.001 | 0.512 / 0.512 / 0.512 / 0.512 | 0.544 (96), 0.975 |
| genus_rarefied | richness_only | mean | 0.574 | 0.524 [0.448–0.574] | 0.577 | 1.000 | 200 |  | 0.574 / 0.574 / 0.574 / 0.574 |  |
| genus_rarefied | richness_only | mean_ex_zou | 0.595 | 0.520 [0.417–0.595] | 0.582 | 1.000 | 200 |  | 0.595 / 0.595 / 0.595 / 0.595 |  |

### Within-cohort CV (StratifiedGroupKFold 5 × 2 repeats, families kept together; inner GroupKFold 3 for C)

| cohort | features | n | AUC | null mean [95% range] | p | Holm | AUC at C = 0.001 / 0.01 / 0.1 / 1 | sibling concordance (families), p | AUC within male / female |
|---|---|---|---|---|---|---|---|---|---|
| ding | abundance | 122 | 0.937 | 0.476 [0.368–0.632] | 0.005 | 0.525 | 0.931 / 0.946 / 0.949 / 0.947 |  |  |
| ding | abundance_rarefied | 122 | 0.909 | 0.472 [0.359–0.603] | 0.005 | 0.525 | 0.906 / 0.929 / 0.935 / 0.925 |  |  |
| ding | depth_only | 122 | 0.563 | 0.407 [0.352–0.461] | 0.005 | 0.525 | 0.563 / 0.611 / 0.625 / 0.623 |  |  |
| ding | richness_only | 122 | 0.571 | 0.405 [0.351–0.458] | 0.005 | 0.525 | 0.571 / 0.659 / 0.670 / 0.671 |  |  |
| zou | abundance | 92 | 0.996 | 0.477 [0.356–0.628] | 0.005 | 0.525 | 0.973 / 0.989 / 0.996 / 0.997 |  |  |
| zou | abundance_rarefied | 92 | 0.988 | 0.477 [0.359–0.607] | 0.005 | 0.525 | 0.970 / 0.986 / 0.992 / 0.991 |  |  |
| zou | depth_only | 92 | 0.873 | 0.394 [0.325–0.454] | 0.005 | 0.525 | 0.873 / 0.922 / 0.924 / 0.923 |  |  |
| zou | richness_only | 92 | 0.436 | 0.392 [0.326–0.453] | 0.104 | 1.000 | 0.436 / 0.414 / 0.393 / 0.390 |  |  |
| david | abundance | 107 | 0.491 | 0.491 [0.396–0.609] | 0.527 | 1.000 | 0.486 / 0.468 / 0.494 / 0.516 | 0.479 (47), 0.669 | 0.473 / 0.579 |
| david | abundance_rarefied | 107 | 0.519 | 0.490 [0.389–0.607] | 0.308 | 1.000 | 0.481 / 0.455 / 0.480 / 0.509 | 0.543 (47), 0.327 | 0.481 / 0.579 |
| david | depth_only | 107 | 0.488 | 0.483 [0.457–0.513] | 0.383 | 1.000 | 0.488 / 0.475 / 0.488 / 0.494 | 0.564 (47), 0.233 | 0.491 / 0.382 |
| david | richness_only | 107 | 0.461 | 0.481 [0.429–0.536] | 0.672 | 1.000 | 0.461 / 0.457 / 0.447 / 0.444 | 0.479 (47), 0.671 | 0.521 / 0.371 |
| david | metadata | 107 | 0.603 | 0.484 [0.399–0.568] | 0.010 | 0.970 | 0.585 / 0.653 / 0.654 / 0.654 | 0.750 (47), 0.000 | 0.551 / 0.402 |
| david | combined | 107 | 0.507 | 0.492 [0.388–0.609] | 0.413 | 1.000 | 0.511 / 0.508 / 0.525 / 0.541 | 0.479 (47), 0.669 | 0.468 / 0.541 |
| david_controlsexswapped | metadata | 107 | 0.521 | 0.479 [0.398–0.561] | 0.169 | 1.000 | 0.515 / 0.542 / 0.542 / 0.541 | 0.553 (47), 0.277 | 0.462 / 0.479 |
| david_controlsexswapped | combined | 107 | 0.506 | 0.495 [0.371–0.616] | 0.403 | 1.000 | 0.490 / 0.475 / 0.510 / 0.534 | 0.479 (47), 0.669 | 0.496 / 0.535 |

† = raw p < 0.05 at chosen C but fixed-C p < 0.05 at ≤ 1 of 4 C values. CIs are sibling-group bootstrap (2,000 resamples).

## 10. Files

- `loco_results.csv`
- `c_sensitivity.csv`
- `oof_scores.csv`
- `harmonisation_log.csv`
- `depth_by_label.csv`
- `within_cohort_results.csv`
- `within_c_sensitivity.csv`
- `within_*_oof_scores.csv`
- `david_delta.csv`
- `zou_diagnostics.csv`
- `multiplicity.csv`
- `multiplicity_summary.txt`
- `run_output_log.txt`

**Reproduce:** `bash code/run.sh <repo>/data <outdir>` (about 25 min on 2 CPUs, seed 20261112).
