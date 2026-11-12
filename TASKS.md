# Tasks and deliverables

Each AI does every track it technically can. Perplexity is expected to do Track B and may attempt A only by describing the method.

## Track A: classifier on the blind holdout (code)
Deliver to the human (who files them under `rounds/round_NN/<agent>/`):
- `predictions.csv` (only once `data/holdout/genus_counts.tsv` exists): columns `sample_id,score`. One row per holdout sample (all of them, once). `score` is a number where higher means more ASD-like.
- `method.md`: features, models, how each step is fitted on training data only, hyperparameter choices, anything that touched holdout features.
- `loco_results.csv`: leave-one-cohort-out AUC (with 95% interval) for each training cohort.
- `code/`: everything needed to reproduce both files from `data/` with one command, plus `requirements.txt`.
Required comparisons inside `loco_results.csv` or `method.md`: abundance-only, network-derived features, and abundance + network, on identical splits; a metadata-only baseline (sex, age) wherever those exist; a label-permutation null.

## Track B: evidence audit (literature)
Deliver `rounds/round_NN/<agent>/evidence.md`:
1. Papers that evaluate a **frozen** gut-microbiome ASD classifier on an independent cohort, or report failed transfer. For each: design, assay (16S vs shotgun), the reported number, its source section, and whether refitting happened in the new cohort.
2. Papers on batch, site, sex, age and diet confounding in ASD microbiome studies.
3. Whether these 8 genera (taken from the Xu 2019 meta-analysis; Akkermansia, Bacteroides, Bifidobacterium, Parabacteroides, Enterococcus, Escherichia-Shigella, Faecalibacterium, Lactobacillus) have a consistent direction in ASD according to meta-analyses, with effect sizes and intervals.
4. A list of 3 more public 16S ASD cohorts usable as final holdouts: accession, n, ages, labels, individual age/sex availability, overlap risks.
Every item carries a DOI/PMID and a VERIFIED / UNVERIFIED mark.

## Track C: proposal text
Deliver `rounds/round_NN/<agent>/proposal_section.md`: Research Problem, Overall Aim, 4 research questions and 5 measurable objectives for a master's proposal on this question, in clear academic English, with no clinical-diagnosis claims and only verified references.

## Freeze
When done: the human tags `freeze/round_NN/<agent>`. The rubric is filled for every round. The holdout is scored only once, for the final round: `python -I scorer/score.py --round NN --final`.
