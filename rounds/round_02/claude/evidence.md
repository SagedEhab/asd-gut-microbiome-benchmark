# Evidence audit: Claude, round 2

Round 1 items are kept with their original marks. Round 2 additions come from Perplexity's round 1 audit, which reports full-text verification; I have **not** re-opened those sources myself, so they are marked VERIFIED-BY-PERPLEXITY (not re-checked by Claude). The holdout-candidate table from round 1 is omitted to keep the holdout blind.

**VERIFIED** means I (Claude) opened the source myself, as an abstract, a PubMed or PMC record, the publisher page, or the full text through a reader, and confirmed the listed facts. Abstract-only checks are marked as such.
**UNVERIFIED** means the item came from a secondary source (a review, a third-party audit or a search snippet) and I could not open the primary page; several publisher pages blocked automated access. Do not quote an UNVERIFIED number without reading the source.

## 1. Classifiers tested on an independent cohort, or failed transfer

| Paper | Assay | Design and reported number | Refit in new cohort? | Status |
|---|---|---|---|---|
| Li et al. 2023, *Gut Microbes* 15(1). DOI 10.1080/19490976.2023.2205386 | 16S and shotgun, 83 cohorts, 20 diseases | Classifiers did well within cohort (about 0.77 AUC) but poorly across cohorts, except intestinal diseases (about 0.73). | No (cross-cohort testing) | VERIFIED (abstract). The ASD-specific "median external AUC 0.60" is UNVERIFIED. |
| Fouquier et al. 2021, *mSystems* 6(2):e00848-20. DOI 10.1128/mSystems.00848-20 | 16S V4 | Arizona (36 ASD / 38 controls) vs Colorado (13 / 16): composition differs by site. ASD is associated with composition after controlling for site, but not after controlling for GI symptoms. | n/a | VERIFIED (abstract). The Arizona-to-Colorado classifier AUC 0.60 is UNVERIFIED. |
| Peralta-Marzal et al. 2024, *Sci Rep* 14:814. DOI 10.1038/s41598-023-50601-7 | 16S | 26-taxa panel: AUC 0.816 in the discovery cohort (60 ASD / 57 siblings); 0.748 and 0.740 in two other cohorts (223 samples). | Yes: the selected panel was re-fitted and cross-validated within each cohort, so this is panel replication, not frozen transfer | VERIFIED (numbers). Refit design is per a third-party review: UNVERIFIED by me. |
| Su et al. 2024, *Nat Microbiol* 9:2344-2355. DOI 10.1038/s41564-024-01739-1 | Shotgun, multikingdom | 1,627 children; single-kingdom panels AUC 0.68-0.87; 31-marker panel AUC 0.91. | Not established from the abstract | VERIFIED (abstract). Not a 16S benchmark. |
| Wan et al. 2024, *Gut Microbes*. DOI 10.1080/19490976.2024.2418984 | Shotgun | Discovery cohort of 273 applied to an independent cohort of 325: AUROC 0.734 (95% CI 0.682-0.782). | Reportedly no | UNVERIFIED |
| Chen W. et al. 2025, *Cell Rep Med* 7:102516. DOI 10.1016/j.xcrm.2025.102516 | Shotgun | 20-feature microbiome model, median external AUC 0.78 across 9 cohorts (range 0.65-0.99). | Unclear | UNVERIFIED |
| Xu et al. 2022, *Microbiol Spectr*. DOI 10.1128/spectrum.00331-22 | 16S, pooled studies | 70/30 random split of pooled samples (not study-level holdout). | n/a | UNVERIFIED |
| Morton et al. 2023, *Nat Neurosci*. DOI 10.1038/s41593-023-01361-0 | Multi-omic | Random sample-level splits; pooled AUC 0.78. | n/a | UNVERIFIED |

Reading of this section: the 16S evidence that tests transfer to a new cohort (Li, and Fouquier's site analysis) points to weak portability. The strongest positive numbers come from shotgun studies or within-cohort designs.

## 2. Batch, site, sex, age and diet confounding

| Paper | Finding | Status |
|---|---|---|
| West et al. 2022, *Sci Rep* 12:17034. DOI 10.1038/s41598-022-21327-9 | 690 participants. Taxa differing in ASD depended on age, sex and bowel function; previous signatures were inconsistent. | VERIFIED (abstract) |
| Yap et al. 2021, *Cell* 184(24):5916-5931. DOI 10.1016/j.cell.2021.10.015 | 247 children. Direct ASD-microbiome associations were negligible; ASD-related narrow diet is linked to lower diversity and looser stool. | VERIFIED (abstract). A 2024 erratum (DOI 10.1016/j.cell.2023.12.001) is UNVERIFIED by me. |
| Fouquier et al. 2021 (above) | Study site is a strong source of variation. | VERIFIED (abstract) |
| Benchmark's own data notes | Ding and Zou labels come from sample names; Ding is V4 and Zou is V3-V4; only David has sex and age. In David, sex is imbalanced (ASD 43 m / 17 f; controls 22 m / 27 f in the original metadata). | VERIFIED (repository files) |

## 3. Do the 8 genera have a consistent direction in ASD?

| Source | What it says | Status |
|---|---|---|
| Xu M. et al. 2019, *Front Psychiatry* 10:473. PMID 31404299, DOI 10.3389/fpsyt.2019.00473 | 9 studies, 254 ASD / 167 controls, ages 6-11; methods pooled pyrosequencing, qPCR, FISH and culture. Reported lower in ASD: Akkermansia, Bacteroides, Bifidobacterium, Parabacteroides, Enterococcus, E. coli; higher: Faecalibacterium, Lactobacillus. **But most random-effects intervals include zero:** Bacteroides SMD -0.35 (95% CI -1.2 to 0.51, p 0.43); Bifidobacterium SMD -1.05 (-2.27 to 0.18); Lactobacillus SMD 0.53 (-0.001 to 1.1); Enterococcus -0.14 (-0.47 to 0.20); E. coli -0.33 (-1.18 to 0.52). The text has internal inconsistencies (Bacteroides model type; Faecalibacterium values). | VERIFIED (full page read; part of the page came through a model summary) |
| Iglesias-Vazquez et al. 2020, *Nutrients* 12(3):792. DOI 10.3390/nu12030792 | Reported, per a secondary source, to find Bacteroides and Parabacteroides **higher** in ASD, the opposite of Xu 2019. | UNVERIFIED (publisher page returned 403) |
| Qin et al. 2026, *Front Microbiol* 17. DOI 10.3389/fmicb.2026.1824546 | Self-described narrative review. Lists conflicting directions: Akkermansia, Bifidobacterium, Faecalibacterium and Bacteroides are each reported up in some studies and down in others. Says the associations "cannot establish causality". | VERIFIED in part (about 17% read verbatim) |
| Oliphant & Allen-Vercoe 2019, *Microbiome* 7:91. DOI 10.1186/s40168-019-0704-8 | What the genera produce: Bifidobacterium acetate and lactate; Faecalibacterium butyrate; Bacteroides and Parabacteroides propionate and succinate; Lactobacillus lactate; Akkermansia is a mucin specialist. Not about autism. | VERIFIED in part (about 20% read verbatim) |

Conclusion for this question: **no consistent direction.** The one verified meta-analysis's pooled effects are mostly compatible with no difference, and other syntheses report opposite directions for the same genera.

## 4. Round 2 additions (from Perplexity round 1; not re-checked by Claude)

| Paper | Point | Mark |
|---|---|---|
| Li et al. 2023, Gut Microbes, DOI 10.1080/19490976.2023.2205386, PMID 37140125 | Six 16S ASD cohorts; with n-1 cohorts pooled for training, median external ASD AUC 0.60; about 1,600 samples estimated for 0.70 (an extrapolation) | VERIFIED-BY-PERPLEXITY (full text) |
| Wang & Fu 2023, Microorganisms, DOI 10.3390/microorganisms11020291, PMID 36838256 | Two shotgun cohorts: within-cohort AUROC 0.81-0.98, cross-cohort about 0.5 | VERIFIED-BY-PERPLEXITY (full text) |
| Morton et al. 2023, Nat Neurosci, DOI 10.1038/s41593-023-01361-0 | Random 80/20 sample split, pooled AUC 0.78; David sibling cohort AUC 0.46 even within cohort | VERIFIED-BY-PERPLEXITY (full text) |
| Peralta-Marzal et al. 2024 | Validation cohorts are Ding (PRJNA589343) and Zou (PRJNA578223), the same as this benchmark; classifiers were refit by 10-fold CV inside each | VERIFIED-BY-PERPLEXITY (full text) |
| Vujkovic-Cvijin et al. 2020, Nature, DOI 10.1038/s41586-020-2881-9, PMID 33149306 | ASD case-control difference no longer significant after matching on host variables; bowel-movement quality the most influential | VERIFIED-BY-PERPLEXITY (full text) |
| Iglesias-Vazquez et al. 2020, Nutrients, DOI 10.3390/nu12030792, PMID 32192218 | Bacteroides and Parabacteroides higher in ASD, opposite to Xu 2019 | VERIFIED-BY-PERPLEXITY (full text); was UNVERIFIED in my round 1 |
| Andreo-Martinez et al. 2022, J Autism Dev Disord, DOI 10.1007/s10803-021-05002-y | Bifidobacterium lower in ASD, SMD -0.513 (-0.953 to -0.073) | VERIFIED-BY-PERPLEXITY (abstract) |

Updated conclusion on the 8 genera: only Bifidobacterium (lower in ASD) has a consistent direction across meta-analyses. Bacteroides and Parabacteroides flip direction between meta-analyses.
