# Method (Claude, round 1)

Reproduce: `python -I code/run.py --data <repo>/data --out .` (Python 3.10; versions in `code/requirements.txt`; seed 0; about 20 minutes with 100 permutations).

**Data.** Only `data/train/` (Ding 122, Zou 92, David 117). No holdout file exists in round 1, so there is no `predictions.csv`.

**Features.** Genera are keyed as `family|genus` from the SILVA lineage. Columns that stop above genus (unassigned reads) are **dropped**, and no renormalisation is done beyond the per-sample CLR. The vocabulary is frozen from the training cohorts of each split: genera present in at least 10% of training samples (127-138 genera). A vocabulary genus missing from the test table counts as 0 reads. CLR is per sample with pseudocount 0.5. Holdout features were never used for scaling; there is no per-cohort standardisation in this submission.

**Network features**, all from the training reference only:
- cosine similarity of a child's CLR profile to the ASD and control centroids, and their difference (leave-self-out for training children);
- class-balanced fraction of ASD among the 10 nearest training children (self excluded for training children);
- 10 taxon-module scores from average-linkage clustering of training-sample taxon correlations (no labels used).

A test child is never added to a graph. The original 0.75 threshold is not used; k = 10 and 10 modules were fixed in advance, not tuned.

**Models.** L2 logistic regression with balanced class weights; C chosen from {0.01, 0.1, 1} by inner leave-one-training-cohort-out AUC, with network features rebuilt inside each inner fold. The abund, net and comb models use identical splits.

**Uncertainty and null.** AUC with a 2,000-sample bootstrap 95% interval. Label-permutation null: 100 permutations within each training cohort, with C fixed at the value chosen on the true labels (a compromise to keep run time down, which makes the null slightly optimistic).

**Metadata.** Only David records sex and age, so no cross-cohort metadata model is possible. Inside David: 5-fold cross-validation keeping sibling pairs together, 5 repeats, C = 0.1, for metadata-only, microbiome-only and both.

**Siblings.** David's sibling pairs never split across inner and outer folds in the within-David analysis. In leave-one-cohort-out, a held-out cohort is whole, so pairs stay together automatically.

**Known limitations.** Three small cohorts, two 16S regions (V4 and V3-V4) harmonised by genus name, Ding/Zou labels taken from sample names, a single seed and a single model family. The network settings were not tuned.
