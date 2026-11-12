# Method — ChatGPT, round 01

**Scope:** research-only ASD/control classification of public stool 16S rRNA samples. Not a diagnosis or clinically validated tool. No holdout outcomes, data or labels accessed.

## Data and exclusions

Input: `data/train/{ding,zou,david}/{genus_counts.tsv,labels.tsv}` (for convenience the script also supports the six flat uploaded filenames). 331 distinct samples: Ding 122 (76 ASD/46 control), Zou 92 (45/47), David 117 (60/57). Original assignment labels are provisional for Ding/Zou. Sample identifiers are strings. All samples with matching abundance and label tables retained. Zero/negative/nonfinite counts checked (negative/nonfinite rejected). Sequences were preprocessed in the repository's common QIIME2/DADA2/SILVA138 workflow, but original sequencing regions differ.

**Unassigned/above-genus rule:** discard columns without a terminal nonempty `g__<name>` token, including semicolon-`__` unassigned branches; 36 Ding, 22 Zou and 32 David. Also retain named genus-like SILVA placeholders (`g__..._group`) as operational labels. For duplicate final genus strings, sum raw counts *before* transformation. Match genera by their exact terminal genus field (no hand-curated alias mapping). Missing genus in a given cohort means zero counts for its samples. No library-depth renormalization is performed before removing above-genus counts. The zero replacement/CLR below changes denominators and induces a compositional logratio representation; because assignment fractions vary, this is a limitation.

## Cross-cohort design and representation

Three outer folds: one entire cohort is test, other two cohorts fit model. David siblings remain together because the entire David cohort is always in the same outer partition. Nested tuning uses each of the two *training* cohorts as the inner test in turn; this also keeps David sibling groups intact. **No outer test labels used to select settings**, though these three results should not be used to select the final method without new validation.

- **Prevalence**: keep genera with nonzero counts in >=10% of the currently fitting training set, fitted separately for every inner or outer fit.
- **Abundance**: CLR of log(raw genus count + 0.5), subtracting each sample's mean log abundance over the selected feature universe (no cohort-specific adjustment). 0.5 is a fixed pseudo-count; a read-count pseudocount is sensitive to library size.
- **Network-derived**: infer Pearson correlations **between CLR genus features across fitting samples**. For each genus take its 5 strongest absolute-correlation neighbors (or fewer if needed), signed correlation weights normalized to sum of absolute weights 1. Project each *individual sample*'s CLR vector through this fixed training-only neighbor matrix to create a vector of network-smoothed features. These are **not directly inferred per-child microbial interaction networks**, nor do they demonstrate biological interactions. The same fixed graph is applied to held-out samples. Network-derived features differ from abundance features by mixing taxa according to training-set co-variation.
- **Combined**: concatenate abundance and network-derived vectors, then standardize feature-wise.

Classifier for all three: `StandardScaler` fitted only on fitting data, then `LogisticRegression(solver='liblinear', penalty='l2', max_iter=1500)` with `C` chosen from {0.001, 0.01, 0.1, 1} by **mean inner leave-one-source-cohort-out AUROC**; ties use smaller C. No threshold tuning or target cohort correction. All three types share exactly the same outer splits and labels.

## Evaluation

AUROC on each held-out cohort. 95% intervals are 1,200 stratification-*unrestricted* cluster bootstrap resamples of test subjects, with David resampled by `sibling_pair` (all others by sample); bootstrap replicates with only one class discarded. Resampling probabilities are independent of label; intervals are descriptive, not repeated-cohort generalization confidence limits. Source-label-prior/constant-score baseline AUROC=0.5. **Metadata-only cannot honestly be trained cross-cohort:** Ding and Zou have neither age nor sex; David has both, so no outer fold has both identifiable train and target age/sex data. It is explicitly reported not estimable rather than filled or fitted using David test labels.

Permutation negative control: 60 randomizations per outer fold, labels shuffled separately within each training cohort; for David, sibling pairs with one of each class can have their two labels exchanged, and singleton statuses are shuffled. The fixed comparison uses abundance model with C=0.1, to avoid multiplying expensive inner tuning. The reported 95% range is across **permutation null AUROCs, not an uncertainty interval for their mean**. Because the David matched dataset offers few null permutations respecting pair structure, the null distribution for folds including David can be broad and is not a formal significance test. Random seed 20261112.

## Results (point estimates)

| held-out | n | abundance | network | combined | null mean |
|---|---:|---:|---:|---:|---:|
| Ding |122|0.477|0.506|0.483|0.478|
| Zou |92|0.523|0.774|0.730|0.510|
| David |117|0.579|0.591|0.605|0.511|

See `loco_results.csv` for all intervals and `oof_predictions.csv` for test-fold scores. The strongest Zou score does not replicate in Ding; do not claim robust cross-population prediction. Network advantage is a hypothesis for future strictly external assessment, not a selected validated method.

## Reproduction

From a checkout of the public repo, place this submission's `code/` and `requirements.txt` in `rounds/round_01/chatgpt/`, then run:

```bash
python -m pip install -r rounds/round_01/chatgpt/requirements.txt
python rounds/round_01/chatgpt/code/run.py --train-dir data/train --out-dir rounds/round_01/chatgpt
```

From the six provided flat attachments, instead use `--train-dir <directory-containing-the-six-files>`. `run.py` writes `loco_results.csv`, `oof_predictions.csv`, `run_details.json` (C choices, input counts and seed). The optional external holdout features were absent at check time; therefore **no `predictions.csv` is supplied**. No holdout feature transformation or holdout-derived scaling has occurred. Environment: Python 3, NumPy, pandas, scikit-learn; library versions may affect tie-breaking marginally.

## Limitations

Small number of source cohorts; heterogeneity in geography, V-region, family matching, age/sex availability, collection and diet; provisional case labels in two cohorts; CLR with raw-count pseudocount and differing library depth; operational rather than biological graph; nested selection based on just two source cohorts. Not enough evidence for any deployment or patient-level use.
