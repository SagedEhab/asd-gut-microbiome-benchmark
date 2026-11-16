# Questions from Perplexity, round 2 (answers are shared with all three agents)

1. **David sex coding: new verbatim evidence.**
   - David et al. 2021 (mSystems, DOI 10.1128/msystems.00193-20; full text) says: "The ASD cohort comprised 72% male participants (n = 43) compared to 55% of the NT cohort (n = 27)". Its Table 1 lists NT "Male 27/49 ... Female 22/49", with "Missing 8 NT gender responses".
   - `labels.tsv` has controls at 22 m / 27 f.
   - The within-David metadata AUC is 0.60 as coded but 0.52 with control sex swapped.
   - Could the referee ask the authors, or check the raw questionnaire field, to establish which is right?
2. **Zou batch structure.**
   - In ENA, Zou library names are "case…" and "control…".
   - Run accession order separates the groups with AUC 0.04, consistent with case and control samples deposited as separate blocks.
   - Should Zou stay a training cohort, be down-weighted, or be reported separately in later rounds?
3. **Holm family.** I applied Holm once across all 105 secondary permutation p-values, LOCO and within-cohort together. Is one family across all analyses the intended scope, or should it be per analysis?
4. **Permutation count for the Holm view.** With 200 permutations, the smallest p is 0.005, which cannot survive Holm across about 100 tests. Should the next round use ≥ 2,000 permutations for every secondary model, or report fewer secondary models?
5. **Next-round headline.** Can an agent replace its headline between rounds, for example by testing the network → David result as the sole new primary? Or must the round-2 headline be carried forward unchanged?
