# Proposal section (Track C, Perplexity, round 2)

Only references whose cited content I found verbatim in the primary source are used. Each one carries its mark from evidence.md.

## Research Problem

Gut-microbiome profiles often separate children with autism spectrum disorder (ASD) from controls within a single cohort. Reported values include:
- an AUC of 0.94 in a 16S study of Chinese children (Ding et al., 2020; DOI 10.1016/j.jpsychires.2020.06.032; VERIFIED, abstract);
- an AUC of 0.931 in another (Dan et al., 2020; DOI 10.1080/19490976.2020.1747329; VERIFIED, full text).

Such estimates rarely survive transfer to a new cohort:
- A model trained on one cohort and tested on another gave AUROC "around 0.5" (Wang & Fu, 2023; DOI 10.3390/microorganisms11020291; VERIFIED, full text).
- A sibling-matched cohort reached an AUC of only 0.46 (Morton et al., 2023; DOI 10.1038/s41593-023-01361-0; VERIFIED, full text).
- An analysis of 20 diseases estimated that about 1,600 training samples would be needed for a median external AUC of 0.70 in ASD (Li et al., 2023; DOI 10.1080/19490976.2023.2205386; VERIFIED, full text).

Host and technical variables compete with diagnosis as explanations:
- ASD-related microbiota differences were no longer significant after matching on host confounders (Vujkovic-Cvijin et al., 2020; DOI 10.1038/s41586-020-2881-9; VERIFIED, full text).
- Diet related to restricted interests may mediate the associations (Yap et al., 2021; DOI 10.1016/j.cell.2021.10.015; VERIFIED, abstract).
- Batch effects can inflate the proportion of significant results when studies are pooled (Gibbons et al., 2018; DOI 10.1371/journal.pcbi.1006102; VERIFIED, full text).

In this benchmark, a leave-one-cohort-out classifier with a prespecified design did not beat a full-pipeline permutation null (mean AUC 0.58, p = 0.21). In one public cohort, sequencing depth and submission order are aligned with diagnosis. It therefore remains open whether any gut-microbial signal for ASD generalises across cohorts once batch, sex, age and household are controlled.

## Overall Aim

To estimate, with leakage-free cohort-wise validation and prespecified analyses, whether, how well and how consistently 16S rRNA gut-microbiome profiles classify sampled ASD and control children in independent cohorts. The project will also quantify how much of any apparent signal is reproduced by technical variables (depth, richness, batch) and by host variables (sex, age, household). This is research-use classification, not diagnosis.

## Research Questions

1. Does a single prespecified compositional classifier, evaluated leave-one-cohort-out, exceed a full-pipeline label-permutation null in public 16S ASD cohorts?
2. How much of any held-out performance is reproduced by depth-only, richness-only and batch-indicator models, and does it persist on rarefied or depth-matched samples?
3. In sibling-matched cohorts, does a frozen model rank the ASD child above the neurotypical sibling more often than chance, and does the microbiome add to sex and age?
4. Do genus-level associations agree in direction across cohorts and with published meta-analyses? Bifidobacterium, for example, is reported lower in ASD with SMD −0.513 (95% CI −0.953 to −0.073) (Andreo-Martínez et al., 2022; DOI 10.1007/s10803-021-05002-y; VERIFIED, abstract). Bacteroides direction conflicts between Xu et al., 2019 (DOI 10.3389/fpsyt.2019.00473) and Iglesias-Vázquez et al., 2020 (DOI 10.3390/nu12030792), both VERIFIED, full text.

## Measurable Objectives

1. Assemble at least five public 16S ASD cohorts, including at least one sibling cohort and one never-reused holdout, and reprocess them with one pipeline.
   - Candidates: Son et al., 2015, PRJNA282013, DOI 10.1371/journal.pone.0137725; Strati et al., 2017, PRJEB15418, DOI 10.1186/s40168-017-0242-1; both VERIFIED, full text.
   - Document the harmonisation key and every unassigned-read decision.
2. Register one headline model and its decision rule before any analysis. Report its leave-one-cohort-out AUC with sibling-grouped 95% CIs and a ≥ 1,000-permutation full-pipeline null (one-sided p).
3. For every secondary model, report AUC at every regularisation value, the total number of comparisons and Holm-adjusted p-values.
4. Report depth-only, richness-only and sex/age baselines in every cohort, plus results on rarefied and depth-matched subsets. Declare signal technical when a baseline matches or exceeds the microbiome model.
5. In each sibling cohort, report the fraction of discordant pairs in which the ASD child scores higher, with a sign-flip p-value and a family-bootstrap CI, and the AUC change from adding the microbiome to sex and age.
