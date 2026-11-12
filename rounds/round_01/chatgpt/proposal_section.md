# Master's proposal section — ChatGPT, round 01

## Research problem

Studies have reported differences in the stool gut microbiota between children sampled with ASD and children sampled as controls, but their reported taxa differ across cohorts and technical protocols. A meta-analysis of 18 studies (493 ASD and 404 controls) identified some pooled differences, yet showed substantial heterogeneity (Iglesias-Vázquez et al., 2020, DOI: **10.3390/nu12030792**, VERIFIED). Dietary restriction and other ASD-associated behaviors may explain some observed microbiome associations (Yap et al., 2021, DOI: **10.1016/j.cell.2021.10.015**, VERIFIED). Published cross-cohort machine-learning experiments have reported imperfect generalization (Rojas et al., 2024, DOI: **10.1038/s41598-023-50601-7**, VERIFIED). It remains unclear whether reproducible information in genus-level 16S rRNA stool profiles is sufficiently stable to classify ASD/control status in independent cohorts beyond confounding and technical batch effects. The project concerns research-use classification, not clinical diagnosis.

## Overall aim

To estimate the reproducibility and out-of-cohort discrimination of ASD/control labels using leakage-controlled, 16S rRNA stool microbial-genus features, and to evaluate whether microbial co-variation representations add information beyond taxonomic abundance and accessible covariates.

## Research questions

1. What out-of-cohort AUROC is achieved when a classifier trained on other studies is applied without refitting to a completely held-out cohort?
2. Do training-derived genus co-variation features or their combination with abundance features improve that out-of-cohort AUROC on identical partitions?
3. How do family structure, sequencing variation, age, sex, gastrointestinal symptoms and diet affect apparent predictive performance when these data are available?
4. Are genus-level directions of association and fitted model interpretations reproducible across independent studies, or are they study-specific?

## Measurable objectives

1. Curate at least six public 16S ASD/control cohorts with sample-level labels and reproducible sequencing/taxonomic metadata, documenting exclusions and overlaps.
2. Run a common sequence-processing workflow and audit genus assignments, sequencing depth, missingness and assay differences for every sample.
3. Implement outer leave-one-cohort-out evaluation with inner cohort-only hyperparameter tuning and family-group-safe splits; report AUROC, 95% cluster-bootstrap intervals, and calibration where interpretable.
4. Compare predeclared abundance-only, training-derived network and combined models on identical cohorts alongside constant-score, label-permutation and available age/sex baselines.
5. Assess robustness by predeclared depth, taxonomic, covariate and cohort sensitivity analyses; evaluate a single fully frozen final model against a previously untouched independent cohort once.

## Ethical statement

The outcomes represent research-use discrimination of case/control labels in sampled children and must not be presented as a diagnostic, screening or clinically validated test.
