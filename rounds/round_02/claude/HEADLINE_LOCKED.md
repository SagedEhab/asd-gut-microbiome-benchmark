# Claude round 2: headline model, locked before any round 2 analysis was run (2026-11-12)

**Headline:** abundance-only L2 logistic regression on CLR genus profiles, **rarefied to 5,000 reads per sample** (seed 0) to remove depth differences. Genera keyed `family|genus`; vocabulary of genera present in at least 10% of training samples; C chosen from {0.001, 0.01, 0.1, 1} by inner leave-one-training-cohort-out AUC. Evaluated leave-one-cohort-out on Ding, Zou and David.

**Headline statistic:** held-out AUC per cohort, with a 2,000-sample cluster bootstrap 95% interval (clusters = sibling pairs in David) and a full-pipeline permutation p (200 permutations within training cohorts, C re-chosen each time). Holm adjustment across the three held-out cohorts.

**Secondary (reported, not headline):**
- network and combined features;
- unrarefied data;
- genus-name-only key;
- AUC at every C;
- depth-only and richness-only baselines;
- within-David metadata models (complete cases);
- within-David sibling-pair concordance.

Choice made before seeing any round 2 output. Rationale: round 1 showed depth predicts Zou's labels (AUC 0.93), so a depth-equalised abundance model is the least confounded primary analysis available.
