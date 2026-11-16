# Round 02 method — prospective specification (written before running Round 02 models)

**Prespecified headline:** family+genus-keyed genus abundance, train-fold prevalence >=10%, log(count+0.5) centered within each sample (CLR-like after dropping unassigned lineages), L2 logistic regression with **C=0.01**, training-only standardisation, no class reweighting. Leave one entire cohort out; score direction always increasing fitted ASD probability. This setting is fixed before viewing Round 02 performance and is not to be changed after observing results. Secondary analyses use an inner-source-cohort LOCO search over C=[0.001,0.01,0.1,1] and all grid settings are reported. The primary source of inspiration is the prior ChatGPT Round 1 abundance pipeline, with the more cautious prespecification and family+genus mapping prompted by Round 1 feedback; Perplexity's discovered depth confound and within-David complete-case design are adopted as controls. The apparently promising Zou model is not selected as headline.

**Scope:** public `data/train/` only. No test-label access, no per-held-out-cohort standardisation, and no score flipping. Network-derived projections are fixed from *training-cohort* CLR Pearson correlation, top-five absolute neighbors per genus, row-normalised; combined concatenates original and network projections. Every model is refitted in outer folds. Prevalence, correlation, scaler and labels used in parameter search come from source cohorts only. Compare genus-name and family+genus strategies. Technical baselines use log10 total input reads and genus richness, respectively. For David, sibling-grouped cross-validation excludes missing sex/age before fold assignment. The label-shuffled null reruns inner hyperparameter selection within the two source cohorts, with >=200 permutations per evaluated held-out model and a one-sided p, then Holm correction across nine primary type/cohort comparisons. Sibling grouping retained in within-David CV and bootstrap CIs.

**Scientific limits:** The genus CLR retains only assigned genus reads, because unassigned lineages are dropped before constructing the feature matrix; this renormalises the *log ratio reference*, not the raw counts. Depth baseline, filtering and rarefaction stress tests address this choice. Datasets differ in sequenced region, site, and several missing covariates. These classifiers are research-use discrimination of sampled children, not clinical tools.

## Results

To be appended after computation, without changing the above prespecification.

### Actual fitted models and validation

Data: Ding 122 (76 ASD), Zou 92 (45 ASD), David 117 (60 ASD); 331 samples in total. Distinct genus keys (family+genus) number 392/222/359 in the three respective cohorts. Unassigned columns dropped: 36/22/32, representing 2.69%/2.48%/2.36% of total reads; this fraction is not silently added back to microbial abundances. Individual samples are log(count+0.5) and centered by the mean of retained log-genus counts; as a compositional transformation, that center is influenced by which genera pass the **training-only** prevalence filter. Network features are deterministic top-5 taxon-correlation projections *without class labels*, not sample-specific co-occurrence networks. The same feature transformations are reconstructed for each inner source-cohort fold. Logistic probabilities always increase with the model's fitted ASD class; no post-hoc orientation reversal. Missing taxa are zeros. The main dataset includes sex and age **only for David**; no cross-cohort metadata model is estimable.

All nine family+genus and nine genus-only LOCO comparisons use **200 within-source-cohort training-label shuffles**, refitting the model and reselecting C by inner LOCO on each shuffle. The 3 prespecified headline cohorts have 200 fixed-C label shuffles independently. All models share identical held-out cohort splits; all 4 C-grid AUROCs are in `regularization_sensitivity.csv`. Raw p=(1+#null AUROCs >= observed)/(201); null 2.5%/97.5% quantiles are not confidence intervals for performance. Holm p-values across the **nine primary family+genus nested-choice** tests, **18 exploratory mapping×model×cohort** tests, and three prespecified headline cohorts are in `loco_results.csv`. Sibling-group bootstrap (400 replicates) forms held-out confidence intervals. Training-label permutation in David flips labels within discordant pairs with probability 0.5 and shuffles singleton labels, respecting pair structures. Strict paired label permutation is not equivalent to free cohort permutation; its conditional null is deliberately conservative about sibling dependence.

The within-David secondary comparisons use one **5-fold StratifiedGroupKFold**, random seed 20261112 and C=0.01, on **107 sex/age complete cases**, with sibling groups never split. Eight missing-sex controls (and any other incomplete observations) are excluded, never flagged by a missingness feature; disputed sex coding makes metadata results provisional. 200 within-David group-constrained shuffled-label runs apply to metadata, abundance, combined network, and abundance+metadata models (`technical_metadata_null.csv`). All six cross-cohort depth/richness models likewise have 200 shuffled-label fits (fixed C=0.01), on identical splits. These technical/permutation baselines are diagnostics rather than added microbiome evidence.

### Prespecified headline: abundance, family+genus, C=0.01

| Held out | AUC (cluster bootstrap 95% CI) | 200-shuffle null mean [95% range] | permutation raw p | Holm across 3 |
|---|---|---|---|---|
| Ding | 0.470 [0.361,0.564] | See `loco_results.csv` | 0.532 | 1.000 |
| Zou | 0.573 [0.450,0.690] | See CSV | 0.517 | 1.000 |
| David | 0.551 [0.460,0.627] | See CSV | 0.184 | 0.552 |

No cohort's prespecified result shows permutation evidence of transfer.

### Nested-choice exploratory models, family+genus (identical outer splits)

| Held out | Abundance | Network | Combined | Technical baselines (depth, richness) |
|---|---:|---:|---:|---:|
| Ding | 0.484 | 0.509 | 0.485 | 0.349, 0.690 |
| Zou | 0.535 | 0.655 | 0.536 | 0.072, 0.493 |
| David | 0.585 | 0.618 | 0.578 | 0.505, 0.495 |

**Best unadjusted exploratory result:** David network 0.618, CI [0.545,0.689], raw permutation p 0.010, **Holm p=0.090 across nine**, **Holm p=0.179 across 18 harmonisation comparisons**. All other nine-family results have raw p >=0.085. The nine primary family+genus comparisons are the primary multiplicity family; the broader 18-hypothesis adjustment is supplementary because harmonisation is a stated sensitivity choice. Each CI is conditional on the fitted score, not a prospective model refitting interval.

### Hyperparameter sensitivity and genus identity choice

The full 4-point grid per family×genus, cohort, and feature set is `regularization_sensitivity.csv` (**72 AUROCs**). Zou network is especially C-sensitive: with family+genus mapping at C 0.001 / 0.01 / 0.1 / 1, AUROC **0.765 / 0.655 / 0.511 / 0.495**; with genus-name-only mapping the nested-choice network reaches **0.774** (C=0.001, p=0.164). The 0.77 appears only under *one* low-regularisation setting and unstable harmonisation, and does not establish ASD association. Family+genus Zou nested-choice C=0.01 has raw p=0.398. David network is comparatively stable across the grid (0.618 / 0.622 / 0.598 / 0.594) but does not survive Holm adjustment. Genus-name-only mapping merges generic labels such as `uncultured` across families; family+genus prevents these collisions. Both analyses use identical samples, scores unflipped, separate full label permutations, and no held-out labels for fitting.

### Technical confounding and robustness

Zou's median all-read depth is **32,168 ASD versus 43,289 controls**; treating *lower* depth as ASD ranks labels at AUROC **0.928**, while the source-trained depth logistic score runs in the **opposite direction** (0.072). AUC less than 0.5 is NOT post-hoc flipped to claim predictive transfer; the direct depth ranking measures Zou's label-depth association only. Ding median depths 42,083/39,839.5, and David 19,028/21,054 (ASD/control); technical details are in `diagnostics.csv`. Richness-only LOCO AUC reaches 0.690 on Ding. Zou's V3–V4 versus Ding's V4 and cohort-specific sequencing depth, plus unstable naming/mapping, are consistent with study-specific structure; the available tables cannot isolate site, 16S region, depth and ASD effects causally.

**Depth-matching diagnostic:** Greedy, one-to-one ASD/control matching on log read depth was performed *using held-out true labels only to define an analysis subset after predictions*; no model fit or score was changed. Matched AUROC values are descriptive, not prospective or a validation of independence. For Zou, matching retained 90/92, but its median pair log-depth gap is **0.290** (about 34% depth ratio), demonstrating poor overlap; network AUC there is 0.675. Ding matched 92 children (network 0.582); David matched 114 (network 0.609). The matching exercise therefore **cannot eliminate Zou's depth confound**.

**Rarefaction:** Independently downsampled genus-assigned reads to min(5,000, current genus-assigned reads) by multinomial draws for each sample, 5 fixed seeds (20261112–20261116), reran training and testing at fixed C=0.01; these are secondary stress experiments, not 200-permutation tests. Mean network AUROC: Ding **0.542**, Zou **0.679**, David **0.569**; mean abundance AUROC: Ding **0.490**, Zou **0.541**, David **0.516**. Sample depth normalisation alone does not remove chemistry/region/batch confounding.

**LOCO sibling concordance in David:** among **53 discordant pairs** with two available scored members, ASD child higher in 28/53 abundance, **33/53 network**, 31/53 combined. This is a within-household discrimination check (unpaired test individuals do not count), not a clinical endpoint. Within David, complete-case grouped AUROCs (metadata / abundance / combined microbiome / abundance+metadata) are **0.652 / 0.439 / 0.453 / 0.486**. The microbiome does **not** improve the sex/age baseline under this protocol. Metadata-only permutation raw p ~0.164 (provisional); other nulls in CSV.

### Verification and reproduction

From the repository root, with the same `data/train/` used here:

```bash
pip install -r rounds/round_02/chatgpt/requirements.txt
bash rounds/round_02/chatgpt/code/run_all.sh data/train rounds/round_02/chatgpt
```

The command writes all AUC, null, sensitivity, rarefaction, paired-sibling and diagnostic CSVs. The `run.py` script uses only training labels and never accesses `data/holdout/`. `run_all.sh` runs `predict_holdout.py` **only if** a feature-only `data/holdout/genus_counts.tsv` exists. In Round 02 it does not exist; **no predictions.csv** is produced. Any future holdout predictions would train the prespecified family+genus abundance C=0.01 model on the entire source training set without using target features for fitting. The evaluator should still verify that future samples use the identical QIIME2/SILVA taxonomy build. All values in `loco_results.csv` and other outputs are results on sampled children, not evidence of clinical generalisation.

### Further cohort structure audit and total inference accounting

A secondary, **cohort-identity** prediction test (distinct from ASD classification) uses five `StratifiedGroupKFold` folds and train-only CLR+standardisation to classify Zou versus Ding/David, keeping sibling pairs together. AUROC is **0.993** under family+genus and **0.994** under genus-name-only mapping (`domain_shift_diagnostics.csv`). This confirms an enormous *joint cohort signature* in stool composition, but because 16S variable region, geography/site, depth, other covariates and processing are confounded with cohort, it **cannot apportion causal contributions or attribute the contrast to ASD**. The family+genus observed taxon-set Jaccard similarity is **0.421** (Ding–Zou) and **0.523** (Zou–David), further illustrating taxon inventory shifts; not fitted classifier AUROCs.

Counting every performed inferential test: **18** nested-selected microbial comparisons (two genus-key choices × three models × three held-out cohorts), **3** prespecified family+genus abundance comparisons, **6** technical baselines (three cohorts × depth/richness), and **4** within-David grouped models = **31** permutation p-values based on 200 replicates apiece. `postprocess.py` reports an additional conservative **Holm-all-31** comparison next to raw p-values across `loco_results.csv` and `technical_metadata_null.csv`, over and above the nominal nine primary, eighteen exploratory, and three headline families. The strongest raw test (David network p=0.00995) has **Holm-all-31 p=0.308**. Rarefaction runs, domain-identity AUCs, taxon Jaccard measures, depth-matched evaluation subsets, C-grid plots, and sibling fractions are labelled descriptive diagnostics and not counted among these 31 formal permutation-hypothesis tests.

**Software tested:** Python 3.13, numpy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0, scipy 1.17.0. The full one-command 200-permutation run is computationally intensive. A complete *one-permutation* pipeline smoke test succeeded, while the reported 200-permutation model×cohort results were computed in isolated batches and assembled with global Holm corrections, then checked for the expected 27 LOCO rows and 72 grid-sensitivity rows. See `RUN_LOG.md` for the exact distinction; no claim of an uninterrupted 200-permutation end-to-end test is made.
