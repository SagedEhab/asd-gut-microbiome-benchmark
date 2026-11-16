# Evidence audit, round 2 (Perplexity)

Research use only. Nothing here describes a diagnostic test.

## How each item was checked

**What changed since round 1.** In round 1, numbers came from a tool-assisted read with an extraction prompt. This round, every number was checked as follows:
1. I downloaded the primary text myself on 2026-11-12:
   - Europe PMC `fullTextXML` for open-access PMC articles;
   - the PMC article page for three articles without Europe PMC XML (Dan 2020, Vujkovic-Cvijin 2020, Sinha 2017);
   - the Europe PMC or PubMed abstract for everything else.
2. I searched that text for the exact number (`lit/check.py`; output in `lit/grep_results.tsv`).

**Marks:**
- **VERIFIED (full text)**: the number or statement appears verbatim in the article body that I downloaded.
- **VERIFIED (abstract)**: it appears verbatim in the abstract, and I did not have the full text.
- **UNVERIFIED**: I could not find it in any text I opened. This covers numbers that exist only in figures, supplements or paywalled pages, and numbers quoted by a review. Where round 1 marked one of these VERIFIED, the downgrade is stated.

Every DOI–PMID pair below was resolved through the Europe PMC REST API.

---

## 1. Frozen classifiers on an independent cohort, or failed transfer

| # | Paper (DOI; PMID) | Design / assay | Number, with the verbatim anchor | Refit in new cohort? | Mark |
|---|---|---|---|---|---|
| 1.1 | Li M et al. 2023, Gut Microbes (10.1080/19490976.2023.2205386; 37140125) | 20 diseases; six 16S ASD cohorts; single-cohort, LODO and cumulative-cohort external validation | "a total of 1,600 and 2,400 samples would be required for ASD and PD to achieve" a median external AUC of 0.7. Section heading: "...whereas ASD and PD require more samples". | No: trained on source cohorts, applied to the left-out cohort | **VERIFIED (full text)** for 1,600. The round-1 numbers **"median external AUC 0.60"** and **"missing features set to zero" are now UNVERIFIED**: neither string is in the text, so they likely came from Fig. 4 or were inferred. |
| 1.2 | Wang W, Fu P 2023, Microorganisms (10.3390/microorganisms11020291; 36838256) | Two shotgun cohorts (Moscow, Shenzhen); RF | Within cohort: "AUROC value of 0.984" (Shenzhen) and "0.81" (Moscow). Across cohorts: "low AUROC values (around 0.5)" | No: trained on one cohort, tested on the other | **VERIFIED (full text)** |
| 1.3 | Morton JT et al. 2023, Nat Neurosci (10.1038/s41593-023-01361-0; 37365313) | 10 16S + 3 shotgun datasets; "80/20 training and test splits" | Pooled "across all 1,193 samples ... (AUC = 0.78)". Sibling-matched: "Son ... AUC = 0.69; David ... AUC = 0.46; Elliot ... AUC = 0.38". Six of nine age/sex-matched cohorts "AUC > 0.87". Held-out shotgun log-ratios "> 0 in 70% of pairs" (Wang) and "73%" (Dan) | Within-dataset random splits; not leave-one-cohort-out | **VERIFIED (full text)** |
| 1.4 | Peralta-Marzal LN et al. 2024, Sci Rep (10.1038/s41598-023-50601-7; 38191575) | Same three cohorts as this benchmark. Discovery = David; validation = "PRJNA589343 (single reads 250 bp long from V4 region ...)" and "PRJNA578223 (paired-end reads 300 bp V3–V4 regions ...)" | Discovery "average AUC = 0.816". Validation "average AUC=0.748 and average AUC=0.74". Extra Trees "AUC=0.84 for both validation datasets" | **Yes.** The 26 ASVs were transferred, but the models were refit in "a tenfold cross-validation scheme using two independent cohorts". This is not a frozen-model test. | **VERIFIED (full text)**. This paper is also my source for Zou = V3–V4 and Ding = V4. |
| 1.5 | Lou M et al. 2022, Gut (10.1136/gutjnl-2021-325115; 34930815) | 16S; "773 subjects with ASD", "429 neurotypical" | "discovery (AUC=0.86), and validation 1 (AUC=0.78), 2 (AUC=0.82) and 3 (AUC=0.67)" | Unclear: features were used "to re-establish the prediction model". The construction of the validation sets is in the supplement, which I did not open | Numbers **VERIFIED (full text)**; refit status **UNVERIFIED** |
| 1.6 | Su Q et al. 2024, Nat Microbiol (10.1038/s41564-024-01739-1; 38977906) | Shotgun, "1,627 children" | Single-kingdom panels "AUC of 0.68 to 0.87"; 31 markers "AUC of 0.91" | Validation design not in the abstract | **VERIFIED (abstract)**. Validation-cohort AUCs are **UNVERIFIED** (not opened). |
| 1.7 | Wan Y et al. 2022, Gut (10.1136/gutjnl-2020-324015; 34312160) | Shotgun, "146 Chinese children (72 ASD and 74 TD)" | "AUC of 82.6% and 76.2% in the discovery cohort and validation cohort" | Whether validation is independent of the 146 is **UNVERIFIED** | **VERIFIED (abstract)**, via the PubMed page. The Europe PMC abstract is truncated. |
| 1.8 | Ding X et al. 2020, J Psychiatr Res (10.1016/j.jpsychires.2020.06.032; 32912596). Source of the Ding training cohort | 16S | RF "AUC of 0.94"; "validation model ... (AUC = 0.98, 95% CI: 97.9%-100%)" | Internal only | **VERIFIED (abstract)** |
| 1.9 | Dan Z et al. 2020, Gut Microbes (10.1080/19490976.2020.1747329; 32312186) | 16S "V4 region-specific primer ... 515F ... 806"; GEO "GSE113701" | "under the curve (AUC) was 0.931" | No independent cohort. The words "independent" and "validation cohort" do not occur in the text. | **VERIFIED (full text, PMC page)** |
| 1.10 | Scanu M et al. 2024, Biomedicines (10.3390/biomedicines12102350; 39457661) | Nine 16S datasets, including PRJNA578223 (Zou); ConQur | RF on the whole validation dataset: "AUROC = 0.81" with normalisation and "AUROC = 0.61" without | Pooled random split | **VERIFIED (full text)** |

**Net:**
- The only frozen cross-cohort ASD numbers I could verify verbatim are "around 0.5" (1.2) and the sibling-cohort AUC of 0.46 for David (1.3).
- Item 1.4 is often read as cross-cohort validation on our exact cohorts, but it refits inside each validation cohort. Its 0.74–0.75 therefore matches our within-cohort fits (0.94–0.99), not our LOCO results.

## 2. Batch, site, sex, age and diet confounding

| # | Paper (DOI; PMID) | Confounder | Verbatim anchor | Mark |
|---|---|---|---|---|
| 2.1 | Yap CX et al. 2021, Cell (10.1016/j.cell.2021.10.015; 34767757) | Diet | "We found negligible direct associations between ASD diagnosis and the gut microbiome" | **VERIFIED (abstract)** |
| 2.2 | Vujkovic-Cvijin I et al. 2020, Nature (10.1038/s41586-020-2881-9; 33149306) | Host variables | "a reduction in microbiota community differences was observed for 13/19 diseases". "Statistically significant microbiota differences were lost ... for several diseases including ... autism spectrum disorder (ASD)". "In the case of migraine and ASD, omitting BMQ [bowel movement quality] from matching variables caused the greatest increase in case-control microbiota differences" | **VERIFIED (full text, PMC page)** |
| 2.3 | Morton 2023 (see 1.3) | Age, sex, household | "age and sex were significant confounders (P < 0.002)". Simulated bias "mean squared error = 589.3" vs "57.8" after sex and age matching | **VERIFIED (full text)** |
| 2.4 | West KA et al. 2022, Sci Rep (10.1038/s41598-022-21327-9; 36220843) | Age, sex, bowel function | Age effect "in four out of nine datasets, but was only significant in two of 10 datasets in the ASD population". "There was no overlap in differentially abundant taxa between only male or only female" comparisons. Taxa "dependent upon age, sex, and bowel function" | **VERIFIED (full text)** |
| 2.5 | Gibbons SM et al. 2018, PLoS Comput Biol (10.1371/journal.pcbi.1006102; 29684016) | Batch | "batch accounts for 6.342% of the total variance". Fraction of p ≤ 0.05 "can be as high as ~70% for the non-normalized data". Proposes percentile normalisation | **VERIFIED (full text)** |
| 2.6 | Sinha R et al. 2017, Nat Biotechnol (10.1038/nbt.3981; 28967885) | Laboratory / pipeline | Effects of bioinformatics pipelines "were typically smaller than those arising from data generation" | **VERIFIED (full text, PMC author manuscript)**. No numeric claim is used. |
| 2.7 | Duvallet C et al. 2017, Nat Commun (10.1038/s41467-017-01973-8; 29209090) | Cross-study consistency | ASD datasets: "Son 2015, ASD H 44 ASD 59" and "Kang 2013, ASD H 20 ASD 19". "we found no association between autism or arthritis and Prevotella" | **VERIFIED (full text)** |
| 2.8 | Scanu 2024 (see 1.10) | Site / project | Whole dataset: "R 2 batch = 0.068" for BioProject vs "R 2 batch = 0.006" for ASD/NC | **VERIFIED (full text)**. Round 1 gave the same numbers; they are now anchored verbatim. |
| 2.9 | McMurdie PJ, Holmes S 2014, PLoS Comput Biol (10.1371/journal.pcbi.1003531; 24699258). New this round | Library size / rarefying | Title: "Why rarefying microbiome data is inadmissible". The abstract calls rarefying and simple proportions "inappropriate for detection of differentially abundant species" | **VERIFIED (abstract)** |
| 2.10 | Weiss S et al. 2017, Microbiome (10.1186/s40168-017-0237-y; 28253908). New this round | Library size | "Alternate normalization measures are potentially vulnerable to artifacts due to library size". "For groups with large (~10×) differences in the average library size, rarefying lowers the false discovery rate" | **VERIFIED (abstract)** |

## 3. Direction of the 8 Xu 2019 genera in meta-analyses

**Sources:**
- **X** = Xu M et al. 2019, Front Psychiatry (10.3389/fpsyt.2019.00473; 31404299). "nine studies, including 254 patients with ASD" and "167 age-matched typically developing controls". **VERIFIED (full text).**
- **I** = Iglesias-Vázquez L et al. 2020, Nutrients (10.3390/nu12030792; 32192218). "18 studies assessing a total of 493 ASD children and 404 controls". **VERIFIED (full text).**
- **A** = Andreo-Martínez P et al. 2022, J Autism Dev Disord (10.1007/s10803-021-05002-y; 33948825). **VERIFIED (abstract).**
- **Y** = Yang C et al. 2024, Biosci Trends (10.5582/bst.2024.01123; 38897955). "28 studies ... 1,256 children with ASD and 1042 neurotypical". **VERIFIED (abstract)**; direction only.

| Genus | X: verbatim estimate | I: verbatim estimate (ASD vs control pooled %) | Other | Consistent? |
|---|---|---|---|---|
| Akkermansia | Lower %. "Z = 0.44, P = 0.658". VERIFIED (full text) | Table 2: "Akkermansia 8 0.04 −0.10–0.18 81 0.55 −0.36–1.46 49 1.25 14.4 0.280", i.e. 0.04 vs 0.55, Z 1.25, P 0.28. VERIFIED (full text) | — | Lower, never significant |
| Bacteroides | "10.2% ... in children with ASD but 14.3% in typically developing children". "SMD −0.35, 95% CI: −1.2 to 0.51". VERIFIED (full text) | "9.04% in children with ASD (95% CI: 7.62, 10.47) and 4.69% in the control group (95% CI: 3.67, 5.71)", subgroup I² "95.8%". VERIFIED (full text) | — | **Conflicting** |
| Bifidobacterium | "ASD group (2.2%) and the control group (4.2%)". "SMD −1.05, 95% CI: −2.27 to 0.18". VERIFIED (full text) | "0.46% in children with ASD (95% CI: 0.33, 0.59) and 0.89% in the control group (95% CI: 0.72, 1.05)", I² "93.9%". VERIFIED (full text) | A: "SMD + = - 0.513; 95% CI - 0.953, - 0.073" (VERIFIED, abstract). Y: listed among genera lower in ASD (VERIFIED, abstract) | **Consistently lower**; the only interval excluding 0 is A's |
| Parabacteroides | Lower % (abstract sentence of X). The round-1 "0.3 vs 0.5" is **UNVERIFIED** (figure only) | "0.32% (95% CI: 0.21, 0.43) in children with ASD and 0.04%". VERIFIED (full text) | Y: "elevated levels of Parabacteroides" (VERIFIED, abstract) | **Conflicting** |
| Enterococcus | "SMD −0.14, 95% CI: −0.47 to 0.20". VERIFIED (full text) | Not analysed | — | Insufficient |
| Escherichia-Shigella | Reported as E. coli: "SMD −0.33, 95% CI: −1.18 to 0.52". VERIFIED (full text) | Not analysed | Zou 2020 abstract: "Escherichia/Shigella ... decreased" (VERIFIED, abstract) | Insufficient; taxonomic mismatch |
| Faecalibacterium | "10.2% (95% CI: 0.039–0.166), clearly higher than ... (7.7%; 95% CI: 0.021–0.133)", "Z = 4.12". VERIFIED (full text) | "6.84% ... (95% CI: 5.34, 8.35) and 5% in the control group (95% CI: 4.15, 5.85)"; Table 2 p "0.040". VERIFIED (full text). The text and Table 2 disagree on the control CI (5.85 vs 8.35) | Y: elevated (VERIFIED, abstract) | Higher in the meta-analyses |
| Lactobacillus | "SMD 0.53, 95% CI: −0.001 to 1.1". VERIFIED (full text) | Not analysed | — | Weak, borderline |

**Net:**
- Only Bifidobacterium (lower in ASD) has a consistent direction, plus one interval that excludes zero (A).
- Bacteroides and Parabacteroides flip between meta-analyses.
- All pooled estimates carry I² of 78–99%.

## 4. Candidate public 16S ASD cohorts for a final holdout

| Cohort (DOI; PMID) | Accession | n | Ages | Individual age/sex | Overlap / risks | Mark |
|---|---|---|---|---|---|---|
| Son JS et al. 2015, PLoS One (10.1371/journal.pone.0137725; 26427004) | "PRJNA282013" (ENA: 103 runs) | "59 ASD children and 44 NT siblings from 66 families"; pairs "from 37 families" | **UNVERIFIED**: the round-1 "7–14 y" is not found verbatim | Not stated | Sibling design like David; "V1V2 and the V1V3 regions" (VERIFIED, full text), so no V4 overlap; used in Morton and Duvallet | Numbers and accession **VERIFIED (full text)**; ages **UNVERIFIED** |
| Strati F et al. 2017, Microbiome (10.1186/s40168-017-0242-1; 28222761) | "PRJEB15418 and PRJEB15420" | "40 subjects with clinical diagnosis of autism (average age 11.1 ± 6.8; sex, male:female, 31:9)" vs "40 ... (average age 9.2 ± 7.9; sex, male:female, 28:12)" | as stated | "Sample accessions IDs and metadata are available in Additional file" (Table S9) | Italian 454; includes adolescents and adults | **VERIFIED (full text)** |
| Dan Z et al. 2020, Gut Microbes (10.1080/19490976.2020.1747329; 32312186) | GEO "GSE113701" | Abstract: "a cohort of 143 children aged 2-13 years old" (VERIFIED, abstract). The 143 ASD / 143 TD split is **UNVERIFIED** | 2–13 y | Aggregate | V4 (verbatim primer); Chinese like Ding; GSE113690 is reused by Novielli 2024 (10.1016/j.isci.2024.110709; 39286497, VERIFIED full text: "GSE113690") | Accession and V4 **VERIFIED (full text, PMC page)**; group split **UNVERIFIED** |
| Kang DW et al. 2013, PLoS One (10.1371/journal.pone.0068322; 23844187), as backup | "SRA053656" | Duvallet's table: "Kang 2013, ASD H 20 ASD 19" (20 controls, 19 ASD). The round-1 20/20 is **UNVERIFIED** | **UNVERIFIED** | Dataset S1 (round-1 claim, **UNVERIFIED**) | Tiny; pyrosequencing | Accession **VERIFIED (full text)** |

**Exclusion:** Ma B et al. 2019 (10.3389/fcimb.2019.00040; 30895172): "The datasets for this manuscript are not publicly available". **VERIFIED (full text).**

**Training-cohort facts used in Track A:**
- Zou 2020, Autism Res (10.1002/aur.2358; 32830918): "48 children with ASD and 48 healthy children in China". **VERIFIED (abstract).** The 16S region is not in the abstract; V3–V4 comes from 1.4 (full text). ENA lists 92 matched runs, all "Illumina MiSeq PAIRED", about 592 bases per spot.
- David MM et al. 2021, mSystems (10.1128/msystems.00193-20; 33824194): "16S rRNA V4 amplicon sequencing of 117 samples (60 ASD and 57 controls)". **VERIFIED (full text).** Sex, quoted verbatim:
  - "The ASD cohort comprised 72% male participants (n = 43) compared to 55% of the NT cohort (n = 27)."
  - Table 1: "Male 43/60 71.7 27/49 55.1 ... Female 17/60 28.3 22/49 44.9", with "Missing 8 NT gender responses".
  - Our `labels.tsv` controls are 22 m / 27 f, which is the paper's NT counts with m and f swapped. The referee reports that `labels.tsv` matches the authors' metadata file. So paper and metadata disagree, and every David sex result below is **provisional**.
- Ding = PRJNA589343: ENA lists 127 "Illumina HiSeq 4000 SINGLE" runs, about 253 bases per read. Its V4 region is stated in 1.4.

I did not try to identify the human's holdout cohort.
