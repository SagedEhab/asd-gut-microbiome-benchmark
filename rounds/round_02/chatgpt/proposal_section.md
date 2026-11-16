# Master's proposal section — Round 02

## Research Problem

Gut-microbiome differences have been reported between children with autism spectrum disorder (ASD) and sampled control children, but pooled studies show substantial between-study heterogeneity and taxonomic direction reversals. Observational associations may reflect diet, age, sex, household, sequencing region, library depth, and processing site rather than a portable association with ASD status. Dietary mediation was documented in a primary cohort analysis (Yap et al., 2021; DOI **10.1016/j.cell.2021.10.015**; PMID **34767757**; **VERIFIED—primary abstract**). Two original meta-analyses describe variable taxa and cross-study heterogeneity (Xu et al., 2019; DOI **10.3389/fpsyt.2019.00473**, PMID **31404299**, **VERIFIED—primary full text**; Iglesias-Vázquez et al., 2020; DOI **10.3390/nu12030792**, PMID **32192218**, **VERIFIED—primary PubMed abstract; individual Table 2 values UNVERIFIED**). Apparent performance from a within-cohort random split therefore does not show transportability across independent settings. The research problem is to determine whether a frozen 16S genus-derived model carries any reproducible **research-use classification signal** across cohorts after technical and demographic baselines, sibling matching and label-permutation controls.

## Overall Aim

To develop and transparently assess reproducible, research-use statistical models that discriminate ASD-labeled and control-labeled children in public 16S gut-microbiome datasets, with primary emphasis on cross-cohort generalisation and incremental evidence beyond technical and available demographic variables.

## Research Questions

1. What leave-one-cohort-out discrimination, including confidence intervals and label-permutation nulls, can a prespecified genus-abundance classifier achieve across independently processed public 16S cohorts?
2. Do network-derived features improve out-of-cohort discrimination beyond abundance alone after accounting for genus harmonisation and regularisation sensitivity?
3. To what extent do sequencing depth, richness, 16S region, batch/site, age, sex and sibling relationships explain apparent separation between ASD and controls?
4. Do microbiome-derived scores improve on age/sex-only predictions within complete-case, sibling-grouped data, and do ASD children score consistently higher than their discordant siblings?

## Measurable Objectives

1. Harmonise the genus counts in at least three public cohorts using two documented keys (genus versus family+genus), record unassigned reads and audit sample-ID overlap; release code and exact filtering rules.
2. Fit a **prespecified** L2 logistic regression abundance model with all learned preprocessing restricted to training cohorts; report the three independent LOCO AUROCs with sibling-clustered 95% bootstrap intervals.
3. Compare abundance, training-network and combined representations on identical splits; report all four C-grid points and at least **200** within-training-cohort permutation replicates per model/fold, with raw and Holm-adjusted p-values.
4. Quantify depth-only and richness-only discrimination, depth-matched and rarefied robustness, plus complete-case sex/age-only versus abundance versus combined models under five sibling-grouped folds.
5. Assess within-family ranking on all available discordant sibling pairs and specify, before any external test, a locked model, a no-refit evaluation plan, uncertainty targets and an independent holdout audit for sequencing-run duplication and metadata completeness.

## Delimitations

This is a secondary analysis of observational public 16S rRNA samples; no inference of mechanism, no causal attribution, no population screening claims, and no clinical deployment claim. Any unused or unavailable covariate is reported, not imputed from outcome. A positive result requires replication beyond the development cohorts and robust uncertainty-aware performance.
