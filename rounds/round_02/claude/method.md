# Method (Claude, round 2)

**Reproduce:** `python -I code/run2.py --data <repo>/data --out .`. Python 3.10; versions in `code/requirements.txt`; seed 0; about 40 minutes on 20 cores with 200 permutations.

**Headline, locked before running** (`HEADLINE_LOCKED.md`, committed first):
- abundance-only L2 logistic regression on CLR genus profiles;
- every sample **rarefied to 5,000 reads** (multivariate hypergeometric draw, seed 0), to remove the depth differences found in round 1;
- genera keyed `family|genus`;
- vocabulary = genera in at least 10% of training samples;
- C from {0.001, 0.01, 0.1, 1} by inner leave-one-training-cohort-out AUC;
- leave-one-cohort-out on Ding, Zou and David.

**Statistics:**
- **Interval:** cluster bootstrap 95% interval (2,000 resamples; clusters are sibling pairs in David, single children elsewhere).
- **Permutation null:** full pipeline with C re-chosen each time, 200 permutations of labels within each training cohort, one-sided p.
- **Multiplicity:** Holm adjustment across the 3 held-out cohorts for the headline, and across all 9 abundance/network/combined tests as a secondary view.

**Secondary analyses**, all reported, none chosen after seeing results:
1. network-derived and combined models (round 1 design: centroid similarities, class-balanced 10-nearest-neighbour fraction, 10 taxon modules, all from the training reference only);
2. the same models on unrarefied data;
3. the headline with a genus-name-only key;
4. AUC at every C value;
5. depth-only (log10 reads) and richness-only (observed genera) logistic models, leave-one-cohort-out, plus each variable's own label association inside each cohort;
6. sibling-pair concordance in David;
7. within-David metadata models on complete cases (10 rows missing sex or age excluded; missingness never encoded), 5-fold, sibling pairs grouped, 5 repeats.

**Ideas taken from other agents' round 1 work:**
- depth and richness baselines, and the sibling-pair concordance test (Perplexity);
- cluster bootstrap by sibling pair (ChatGPT, Perplexity);
- excluding missing-sex rows (Perplexity).

**Limitations:**
- Richness in the technical baseline is counted on unrarefied tables, so it partly reflects depth.
- Rarefying discards reads.
- There are three cohorts, and Ding/Zou labels come from sample names.
- David's control sex coding is disputed.
