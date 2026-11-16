# Proposal section (Claude, round 1, draft)

## Research Problem
Gut-microbiome differences between children with and without autism spectrum disorder (ASD) have been reported, and several machine-learning studies report moderate-to-high classification accuracy. Most of those estimates come from cross-validation inside one cohort, or from re-fitting a selected feature panel within each new cohort. When a fitted model is moved to a different study population, reported performance falls sharply (Li et al., 2023, DOI 10.1080/19490976.2023.2205386). Study site, sex, age, bowel function and diet each change which taxa appear to differ (Fouquier et al., 2021, DOI 10.1128/mSystems.00848-20; West et al., 2022, DOI 10.1038/s41598-022-21327-9; Yap et al., 2021, DOI 10.1016/j.cell.2021.10.015). It is therefore unresolved whether public 16S gut profiles carry an ASD-associated signal that survives a change of cohort, and whether sample-network features add to taxonomic abundance under such evaluation.

## Overall Aim
To estimate, under leakage-controlled leave-one-cohort-out evaluation, how well public paediatric 16S gut-microbiome profiles classify ASD versus control children in cohorts unseen during training, and whether network-derived features improve this beyond abundance alone. The output is research-use classification of sampled children, not a diagnosis.

## Research Questions
1. In cohorts held out entirely from training, how well does a frozen abundance-based classifier separate ASD from control children (AUC with 95% interval, compared with a label-permutation null)?
2. Do network-derived features (similarity to class reference profiles, nearest-neighbour composition, taxon-module scores) change held-out AUC relative to abundance alone, measured as a paired difference with uncertainty?
3. Where sex and age are recorded, how much of the apparent discrimination do they explain, and does the microbiome add to them?
4. Are the taxa that drive classification consistent in direction across cohorts?

## Measurable Objectives
1. Assemble at least four public 16S ASD cohorts with a documented manifest (accession, labels and their source, assay region, n after quality control, age/sex availability, overlap check).
2. Implement one reproducible pipeline that fits every learned step on training cohorts only, and report held-out AUC with bootstrap intervals and permutation p-values for each held-out cohort.
3. Compare abundance-only, network-only and combined models on identical splits, reporting the paired AUC difference and its 95% interval.
4. Report metadata-only, microbiome-only and combined models in every cohort that records sex and age, keeping related children in the same fold.
5. Evaluate the final, frozen pipeline once on an independent holdout cohort and publish the code, manifests and results.
