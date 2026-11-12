# Proposal section (Track C, Perplexity, round 1)

## Research Problem

Many studies report that gut-microbiome profiles separate children with autism spectrum disorder (ASD) from controls with high within-cohort accuracy. For example:
- AUC 0.94 in one 16S cohort (Ding et al., 2020; DOI 10.1016/j.jpsychires.2020.06.032; VERIFIED, abstract);
- AUC 0.931 in another (Dan et al., 2020; DOI 10.1080/19490976.2020.1747329; VERIFIED).

These estimates rarely survive transfer to new cohorts:
- A frozen-model analysis of six 16S ASD cohorts found a median external AUC of only 0.60, even when n−1 cohorts were pooled for training (Li et al., 2023; DOI 10.1080/19490976.2023.2205386; VERIFIED).
- Matching on host variables removed the apparent ASD–microbiota difference in a large population sample (Vujkovic-Cvijin et al., 2020; DOI 10.1038/s41586-020-2881-9; VERIFIED).
- Diet related to restricted interests may mediate the reported associations (Yap et al., 2021; DOI 10.1016/j.cell.2021.10.015; VERIFIED, abstract).

Technical batch effects also threaten validity. In the public Zou cohort, sequencing depth alone separates ASD and control samples (AUC 0.93; this benchmark, round 1). It remains unclear whether any gut-microbial signal for ASD generalises across cohorts once batch, sex, age and household are controlled.

## Overall Aim

To estimate, under leakage-free cohort-wise validation, how well and how consistently 16S rRNA gut-microbiome profiles classify sampled ASD and control children in independent cohorts, and to quantify how much of any apparent signal is explained by technical and host confounders. This is research-use classification, not diagnosis.

## Research Questions

1. What is the leave-one-cohort-out AUC of abundance-based, network-based and combined classifiers across public 16S ASD cohorts, relative to a label-permutation null?
2. How much of the cross-cohort performance can be reproduced by technical variables (sequencing depth, richness, 16S region) and by host variables (sex, age) alone?
3. In sibling-matched cohorts, does a frozen classifier rank the ASD child above their neurotypical sibling more often than chance?
4. Which genera, if any, show a consistent direction of association across cohorts and across published meta-analyses (Xu et al., 2019, DOI 10.3389/fpsyt.2019.00473; Iglesias-Vázquez et al., 2020, DOI 10.3390/nu12030792; both VERIFIED)?

## Measurable Objectives

1. Harmonise at least five public 16S ASD cohorts (at least three for training, plus one never-reused holdout) into a single genus table processed with DADA2 and SILVA 138, documenting every harmonisation and unassigned-read decision.
2. Report leave-one-cohort-out AUC with sibling-grouped bootstrap 95% CIs and 200-permutation refitted nulls for three feature sets on identical splits, against one pre-registered primary model.
3. Report depth-only, richness-only and (where available) sex/age-only baselines per cohort. Declare a model informative only if its lower CI bound exceeds both the best baseline and 0.5.
4. Report within-sibling-pair concordance with a 95% CI for every sibling-matched cohort.
5. Score a frozen, pre-registered model once on the blind holdout and report the AUC with its 95% CI, whether positive or null.
