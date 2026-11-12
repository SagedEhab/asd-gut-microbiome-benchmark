# Evidence audit, round 1 (Perplexity)

Marks:
- **VERIFIED (full text)**: I opened the article's full text (PMC or the publisher page) on 2026-11-12, and the quoted numbers came from that text.
- **VERIFIED (abstract)**: the DOI/PMID resolved and the numbers came from the PubMed/Europe PMC abstract only. The full text was not read.
- **UNVERIFIED**: I could not open the source, or the specific claim was not in the text I read.

All DOI–PMID pairs were resolved through the Europe PMC REST API (`DOI:` query). Numbers were pulled from the article text by a tool-assisted read with a targeted extraction prompt. They were not copied by hand from PDFs, so the referee's spot-check should compare them against the named table or figure. Data accessions in Part 4 were also checked against ENA or GEO directly.

---

## 1. Frozen classifiers on an independent cohort, or failed transfer

| # | Paper | Design / assay | Reported number (source section) | Refit in new cohort? | Mark |
|---|---|---|---|---|---|
| 1.1 | Li M et al. 2023, *Gut Microbes*. "Performance of gut microbiome as an independent diagnostic tool for 20 diseases: cross-cohort validation of machine-learning classifiers." DOI 10.1080/19490976.2023.2205386, PMID 37140125 | Re-analysis of public cohorts for 20 diseases. Six 16S ASD cohorts, genus-level relative abundance. Single-cohort external validation, leave-one-dataset-out (LODO) and cohort cumulation | ASD: even with n−1 cohorts pooled for training, the **median external AUC was 0.60**. The authors estimate that **about 1,600 samples** would be needed for a median external AUC of 0.70 (95% CI 0.62–0.78). They report poor marker consistency across the six 16S ASD cohorts (Results, "CD and CRC achieve high external validation with small sample sizes, whereas ASD and PD require more samples"; Fig. 4b–d; Fig. S5) | **No.** The model was trained on the source cohort(s) and applied to the left-out cohort, and missing features were set to zero | VERIFIED (full text) |
| 1.2 | Wang W, Fu P 2023, *Microorganisms*. DOI 10.3390/microorganisms11020291, PMID 36838256 | Two shotgun cohorts: Moscow (PRJNA516054, 30 ASD / 20 TD) and Shenzhen (PRJEB23052, 43 / 31). Random forest | Within-cohort AUROC 0.984 (Shenzhen) and 0.81 (Moscow). **Cross-cohort AUROC "around 0.5"**; no exact per-direction value is given (Section 3.5) | No (trained on one cohort, tested on the other) | VERIFIED (full text) |
| 1.3 | Morton JT et al. 2023, *Nat Neurosci*. DOI 10.1038/s41593-023-01361-0, PMID 37365313 | 10 fecal 16S and 3 shotgun datasets, age/sex- or sibling-matched. Gradient boosting with an 80/20 random sample split | 6 of 9 age/sex-matched cohorts had AUC > 0.87 within cohort. The pooled classifier had **AUC 0.78** on 1,193 samples (random sample split, **not** leave-one-cohort-out). Sibling-matched cohorts: Son AUC 0.69, **David AUC 0.46**, Elliott 0.38 (Results, "Differential ranking analysis…"; Fig. 2b; Extended Data Fig. 3). A log-ratio score was >0 in 70% (Wang) and 73% (Dan) of held-out shotgun pairs | Within-dataset models. The log-ratio check on held-out shotgun data was not a refit | VERIFIED (full text) |
| 1.4 | Peralta-Marzal LN et al. 2024, *Sci Rep*. DOI 10.1038/s41598-023-50601-7, PMID 38191575 | **Uses the same three cohorts as this benchmark**: discovery = David 2021 (V4); validation = Ding 2020 (PRJNA589343) and Zou 2020 (PRJNA578223). Recursive ensemble feature selection picked 26 ASVs | Discovery mean AUC 0.816 (Table 3). Validation mean AUC **0.748 (Ding)** and **0.740 (Zou)**; best Extra Trees 0.84 (Table 4) | **Yes.** Only the feature list was transferred; classifiers were re-trained with 10-fold CV inside each validation cohort. This is not a frozen-model test | VERIFIED (full text) |
| 1.5 | Lou M et al. 2022, *Gut*. DOI 10.1136/gutjnl-2021-325115, PMID 34930815 | 16S V4, 773 ASD / 429 NT Chinese children, random forest. Validation sets 1–3 | Discovery AUC 0.86. Validation sets **0.78, 0.82 and 0.67** (Abstract; Results) | **Unclear.** The text says the model was "re-established" on the top 20 features, and the validation-set details are in the supplement | VERIFIED (full text); refit status UNVERIFIED |
| 1.6 | Su Q et al. 2024, *Nat Microbiol*. DOI 10.1038/s41564-024-01739-1, PMID 38977906 | Shotgun, 1,627 children, multikingdom 31-marker random forest. Independent hospital cohort (14 ASD / 17 NT), a community cohort, and a public six-study set | Single-kingdom AUC 0.68–0.87 and **31-marker AUC 0.91** (Abstract). Validation-cohort AUCs are in Extended Data Figs. 5–7 and Extended Data Table 2, which I could not read | Not stated in the text I could read | VERIFIED (abstract); validation AUCs UNVERIFIED |
| 1.7 | Wan Y et al. 2022, *Gut*. DOI 10.1136/gutjnl-2020-324015, PMID 34312160 | Shotgun, 72 ASD / 74 TD Chinese children | A five-species panel had AUC **82.6% (discovery)** and **76.2% (validation)** (Abstract). The validation set comes from the same 146 children | Probably an internal split; not established | VERIFIED (abstract); design UNVERIFIED |
| 1.8 | Ding X et al. 2020, *J Psychiatr Res*. DOI 10.1016/j.jpsychires.2020.06.032, PMID 32912596 (**source of the Ding training cohort**) | 16S, 77 ASD / 50 HC | Three-genus random forest AUC 0.94, and a "validation model" AUC 0.98 (Abstract). This is an internal validation, not an independent cohort | n/a (within cohort) | VERIFIED (abstract) |
| 1.9 | Dan Z et al. 2020, *Gut Microbes*. DOI 10.1080/19490976.2020.1747329, PMID 32312186 | 16S V4, 143 ASD / 143 TD | Random forest AUC 0.931 on 24 genera. **No independent validation cohort** (Methods) | n/a | VERIFIED (full text) |
| 1.10 | Scanu M et al. 2024, *Biomedicines*. DOI 10.3390/biomedicines12102350, PMID 39457661 | 16S V3–V4, 9 datasets from Italy, China and Korea (includes **Zou, PRJNA578223**). ConQur batch correction | Whole-validation random forest AUC **0.61 without** batch correction vs 0.81 with it. Random 70/30 or 80/20 splits; **no leave-one-country-out test** | Pooled refit | VERIFIED (full text) |

Takeaway from Part 1: within-cohort AUCs of 0.8–0.98 are common. The only frozen cross-cohort ASD numbers I found are about 0.5 (1.2), a median of 0.60 with n−1 cohorts pooled (1.1), and 0.46 for the David sibling cohort even within cohort (1.3). Item 1.4 is often cited as cross-study validation, but it refits inside each validation cohort.

## 2. Batch, site, sex, age and diet confounding

| # | Paper | Confounder | Finding | Mark |
|---|---|---|---|---|
| 2.1 | Yap CX et al. 2021, *Cell*. DOI 10.1016/j.cell.2021.10.015, PMID 34767757 | Diet | Shotgun, n = 247. "Negligible direct associations between ASD diagnosis and the gut microbiome." ASD-related restricted interests → less diverse diet → lower microbial diversity and looser stools (Abstract) | VERIFIED (abstract) |
| 2.2 | Vujkovic-Cvijin I et al. 2020, *Nature*. DOI 10.1038/s41586-020-2881-9, PMID 33149306 | Age, sex, BMI, geography, alcohol, bowel-movement quality, diet | Matching on host variables reduced case–control microbiota differences for 13 of 19 diseases. The **ASD difference was no longer significant after confounder matching**, and bowel-movement quality was the most influential matching variable for ASD (Fig. 4e) | VERIFIED (full text) |
| 2.3 | Morton JT et al. 2023 (see 1.3) | Age, sex, household, batch | Age and sex were significant confounders (P < 0.002). Household was a significant confounder in sibling cohorts (P < 0.001). Simulated age-confounder bias was about 10-fold lower with age/sex matching (MSE 589.3 vs 57.8). In MBQC data, laboratory drove Bray–Curtis variation | VERIFIED (full text) |
| 2.4 | West KA et al. 2022, *Sci Rep*. DOI 10.1038/s41598-022-21327-9, PMID 36220843 | Age, sex, bowel function | 13 datasets from 10 cohorts. Age affected community variation in 4 of 9 NT and 2 of 10 ASD subsets. Male-only and female-only ASD-vs-NT differential taxa **did not overlap**. Removing children with bowel dysfunction invalidated many ASD findings | VERIFIED (full text) |
| 2.5 | Gibbons SM, Duvallet C, Alm EJ 2018, *PLoS Comput Biol*. DOI 10.1371/journal.pcbi.1006102, PMID 29684016 | Batch | Batch explained 6.34% of variance across CRC 16S studies. Pooling uncorrected controls from two studies gave about 70% of p ≤ 0.05. Proposes control-referenced percentile normalisation | VERIFIED (full text) |
| 2.6 | Sinha R et al. 2017, *Nat Biotechnol* (MBQC). DOI 10.1038/nbt.3981, PMID 28967885 | Batch / laboratory | Variation across laboratories and pipelines in 16S profiling of shared samples (title and abstract level only; I did not read the numbers) | VERIFIED (citation); numbers UNVERIFIED |
| 2.7 | Duvallet C et al. 2017, *Nat Commun*. DOI 10.1038/s41467-017-01973-8, PMID 29209090 | Cross-study consistency | ASD had only 2 datasets (Son 2015, Kang 2013). No consistent ASD associations were found, and the reported autism–*Prevotella* link was not reproduced | VERIFIED (full text) |
| 2.8 | Scanu M et al. 2024 (see 1.10) | Site / geography | BioProject explained more Bray–Curtis variance (R² 0.068) than ASD status (0.006) in the pooled data before correction | VERIFIED (full text) |
| 2.9 | Li M et al. 2023 (see 1.1) | Cohort / site | Accuracy dropped on independent cohorts for non-intestinal diseases including ASD | VERIFIED (full text) |

## 3. Direction of the 8 Xu 2019 genera in meta-analyses

Sources:
- **X** = Xu M et al. 2019, *Front Psychiatry*. DOI 10.3389/fpsyt.2019.00473, PMID 31404299. 9 studies, 254 ASD / 167 controls. VERIFIED (full text).
- **I** = Iglesias-Vázquez L et al. 2020, *Nutrients*. DOI 10.3390/nu12030792, PMID 32192218. 18 studies, 493 ASD / 404 NT. VERIFIED (full text).
- **A** = Andreo-Martínez P et al. 2022, *J Autism Dev Disord*. DOI 10.1007/s10803-021-05002-y, PMID 33948825. 18 studies. VERIFIED (abstract only).
- **Y** = Yang C et al. 2024, *Biosci Trends*. DOI 10.5582/bst.2024.01123, PMID 38897955. 28 studies, 1,256 ASD / 1,042 NT. VERIFIED (abstract only; direction only).

| Genus | X (2019): estimate (95% CI) | I (2020): ASD vs control pooled RA %, Z | Other | Consistent? |
|---|---|---|---|---|
| Akkermansia | Lower: % 0.1 vs 0.2, Z = 0.44, P = 0.66, NS | Lower: 0.04 vs 0.55, Z = 1.25, P = 0.28, NS | — | Direction lower, **never significant** |
| Bacteroides | % lower (10.2 vs 14.3, P < 0.001). SMD −0.35 (−1.20 to 0.51), NS | **Higher**: 9.04 (7.62–10.47) vs 4.69 (3.67–5.71), between-group I² 95.8% | — | **Conflicting** |
| Bifidobacterium | % lower (2.2 vs 4.2, P = 0.023). SMD −1.05 (−2.27 to 0.18), NS | Lower: 0.46 vs 0.89, I² 93.9% | A: SMD −0.513 (−0.953 to −0.073). Y: lower | **Consistently lower**; the only genus significant by SMD in more than one source |
| Parabacteroides | Lower: % 0.3 vs 0.5, no test reported | **Higher**: 0.32 vs 0.04 | Y: higher | **Conflicting** |
| Enterococcus | SMD −0.14 (−0.47 to 0.20), NS | Not analysed | — | Insufficient |
| Escherichia-Shigella | *E. coli* SMD −0.33 (−1.18 to 0.52), NS. Reported as *E. coli*, not the SILVA genus | Not analysed | — | Insufficient; taxonomic mismatch |
| Faecalibacterium | **Higher**: % 10.2 vs 7.7, P < 0.001 | Higher: 6.84 vs 5.00, P = 0.040 | Y: higher. Ding 2020 (1.8): **lower** in that cohort | Higher in meta-analyses, but cohort-level conflicts exist |
| Lactobacillus | Higher: SMD 0.53 (−0.001 to 1.10), borderline NS | Not analysed | Strati 2017: higher in ASD (LEfSe) | Weak |

Caveats:
- Xu 2019 and Iglesias-Vázquez 2020 pool group-level relative abundances, and heterogeneity is extreme (within-group I² of 81–99% in I).
- I gives no confidence interval for the between-group difference.
- The text and tables of I disagree for some CIs (for example, the *Faecalibacterium* control CI is 4.15–5.85 in the text and 4.15–8.35 in Table 2).

Net: only *Bifidobacterium* (lower in ASD) has a consistent direction with an interval excluding zero in at least one SMD analysis (A). *Bacteroides* and *Parabacteroides* flip direction between meta-analyses.

## 4. Candidate public 16S ASD cohorts for a final holdout

All accessions below were checked in ENA or GEO on 2026-11-12.

| Cohort | Accession (checked) | n | Ages | Labels | Individual age/sex | Overlap / risks | Mark |
|---|---|---|---|---|---|---|---|
| Son JS et al. 2015, *PLoS One*. DOI 10.1371/journal.pone.0137725, PMID 26427004 | PRJNA282013 (ENA: 103 Illumina amplicon runs) | 59 ASD / 44 NT siblings (37 pairs) | 7–14 y | ASD vs sibling | Not stated as public | US sibling design like David; **V1–V2/V1–V3** (no V4 overlap); used in Morton 2023 and Duvallet 2017 | VERIFIED (full text + ENA) |
| Strati F et al. 2017, *Microbiome*. DOI 10.1186/s40168-017-0242-1, PMID 28222761 | PRJEB15418 (ENA: 142 runs, LS454) and PRJEB15420 (9 runs) | 40 AD / 40 NT | ASD mean 11.1 ± 6.8 y; NT 9.2 ± 7.9 | ASD vs NT | **Yes**: per-sample metadata in Additional file 12, Table S9 | Italian; 454 V3–V5; includes adolescents and adults; one project may be ITS (fungal); I did not check which | VERIFIED (full text + ENA) |
| Dan Z et al. 2020, *Gut Microbes*. DOI 10.1080/19490976.2020.1747329, PMID 32312186 | GEO GSE113701 (SuperSeries, links PMID 32312186) | 143 ASD / 143 TD | 2–13 y | ASD vs TD | Aggregate only | Chinese **V4** (same region as Ding and David); also used in Novielli 2024 (GSE113690) and in Morton 2023 (shotgun part) | VERIFIED (full text + GEO) |
| Kang DW et al. 2013, *PLoS One* (backup). DOI 10.1371/journal.pone.0068322, PMID 23844187 | SRA053656 (ENA: 40 runs, LS454) | 20 / 20 | 3–16 y | ASD vs NT | Dataset S1 has per-subject survey data | Tiny; V2–V3 pyrosequencing; in Duvallet 2017 | VERIFIED (full text + ENA) |

Training-cohort identity check:
- Ding = **PRJNA589343** (ENA: 127 runs, SRR10442269…). This matches data/README's 127 raw samples.
- Zou = **PRJNA578223** (96 runs). This matches 96 raw samples (92 used). Zou is also part of Scanu 2024.
- David 2021 (DOI 10.1128/msystems.00193-20, PMID 33824194; VERIFIED full text) gives no SRA accession; its FASTQs are hosted at Oregon State.
- Do not use Ma B et al. 2019 (DOI 10.3389/fcimb.2019.00040, PMID 30895172): its data are not public. VERIFIED (full text).

I do not know which cohort the human selected as the holdout, and I did not try to find out. If it is one of the above, it should not be reused (PROCESS.md).
