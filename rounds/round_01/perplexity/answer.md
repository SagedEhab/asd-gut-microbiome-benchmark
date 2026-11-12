# Answer, round 1 (Perplexity)

**Not reliably, on this round's evidence.** This is research-use classification of sampled children, not diagnosis.

**What the evidence supports**
- Leave-one-cohort-out, with siblings grouped and every step fitted on training cohorts only:
  - **Ding:** at chance. Every feature set gives AUC ≈ 0.50, with permutation p ≥ 0.5.
  - **Zou:** AUC 0.71–0.73, but not significant against a refitted label-permutation null (95th percentile ≈ 0.81, p = 0.14–0.19). Sequencing depth alone separates Zou's ASD and control samples (AUC 0.93), which suggests a batch confound.
  - **David** (no depth confound): a weak signal at best. AUC 0.58 (95% CI 0.50–0.67). Network p = 0.025 is uncorrected across 9 tests. Within sibling pairs, the ASD child scores higher 56–58% of the time.
- Network features add nothing over abundance on identical splits.
- In David, sex and age (AUC 0.64) beat the microbiome (0.48).

**How strongly**
- This is a moderately strong negative result, and it matches published frozen-model transfer:
  - median external ASD AUC 0.60 with n−1 cohorts pooled ([Li 2023, DOI 10.1080/19490976.2023.2205386](https://doi.org/10.1080/19490976.2023.2205386));
  - about 0.5 between two cohorts ([Wang & Fu 2023, DOI 10.3390/microorganisms11020291](https://doi.org/10.3390/microorganisms11020291));
  - 0.46 for David even within cohort ([Morton 2023, DOI 10.1038/s41593-023-01361-0](https://doi.org/10.1038/s41593-023-01361-0)).
- Higher published AUCs come from within-cohort or refitted designs. For example, [Peralta-Marzal 2024, DOI 10.1038/s41598-023-50601-7](https://doi.org/10.1038/s41598-023-50601-7) refit inside Ding and Zou.
- Diet and host-variable confounding are documented ([Yap 2021, DOI 10.1016/j.cell.2021.10.015](https://doi.org/10.1016/j.cell.2021.10.015); [Vujkovic-Cvijin 2020, DOI 10.1038/s41586-020-2881-9](https://doi.org/10.1038/s41586-020-2881-9)).
- Of the eight Xu 2019 genera, only *Bifidobacterium* (lower in ASD) is consistent across meta-analyses.
- Caveats: three cohorts give wide intervals, and the Ding/Zou labels are provisional.

**What would change my mind**
- A frozen model reaching AUC ≥ 0.70 (lower CI bound > 0.60) on an unseen, depth-balanced cohort, while beating the depth and sex/age baselines.
- Or within-pair concordance clearly above 0.6 in independent sibling cohorts.

**What the next round should do**
1. Report depth-only and richness-only baselines for every cohort, and re-test on depth-matched or rarefied subsets.
2. Pre-register one primary compositional (CLR) model to limit multiplicity.
3. Resolve David's sex coding (QUESTIONS.md), and make within-pair tests David's primary endpoint.
4. Add cohorts such as Son 2015 (PRJNA282013), Dan 2020 (GSE113701) and Strati 2017 (PRJEB15418). Li 2023 estimates that about 1,600 samples are needed for AUC 0.70.
