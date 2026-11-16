# Answer, round 2 (Perplexity)

**No. On this round's evidence, a gut-microbial profile does not predict ASD across cohorts.** This is research-use classification of sampled children, not diagnosis.

## What the evidence supports
- **The prespecified headline fails.** Family|genus CLR abundance, L2-LR, leave-one-cohort-out, siblings together.
  - Mean held-out AUC is 0.583 (null 95% range 0.40–0.65, 1,000 full-pipeline permutations), p = 0.21.
  - Without Zou, the mean is 0.544 (p = 0.34).
  - p < 0.05 only at fixed C = 1 (single setting).
- **Secondary results.** 106 permutation-tested comparisons; 15 have raw p < 0.05, none survives Holm. The best is network → David: 0.62, p = 0.008, Holm 0.78.
- **Zou looks like cohort structure, not ASD signal.**
  - Depth separates its groups (AUC 0.93).
  - So does submission order (0.96): cases and controls were deposited as separate blocks.
  - So does label-free distance to the other cohorts (0.92).
  - Its null spans 0.21–0.85, which explains round 1's conflicting Zou numbers.
  - The network direction that scores Zou at 0.84 scores Ding at 0.41.
- **In David, the microbiome adds nothing beyond sex and age.**
  - Metadata 0.60 vs microbiome 0.49. Adding the microbiome changes AUC by −0.10 (95% CI −0.22 to 0.03).
  - Metadata falls to 0.52 under the paper's sex coding, so the metadata result is provisional.
  - ASD children outscore their sibling in 56% of 55 discordant pairs (p = 0.21).
- **Technical baselines.**
  - Within-cohort fits reach 0.94–0.996, so the signal is cohort-specific.
  - Rarefaction lowers transfer (mean 0.49).
  - Genus vs family|genus keys (they differ only in "uncultured") change no conclusion.

## How strongly
Moderately strong negative evidence, matching verbatim-checked frozen-transfer results:
- "around 0.5" ([Wang & Fu 2023](https://doi.org/10.3390/microorganisms11020291));
- 0.46 for David ([Morton 2023](https://doi.org/10.1038/s41593-023-01361-0));
- about 1,600 samples needed for 0.70 ([Li 2023](https://doi.org/10.1080/19490976.2023.2205386)).

Three cohorts give wide nulls; a modest effect (AUC about 0.6) cannot be excluded.

## What would change my mind
- A frozen, prespecified model reaching AUC ≥ 0.70 (p < 0.01) on an unseen, depth-balanced cohort, beating the depth, richness and sex/age baselines.
- Or sibling concordance ≥ 0.65 replicated in a second sibling cohort.

## Next round
1. Add Son 2015, Dan 2020 and Strati 2017 to narrow the nulls.
2. Settle David's sex coding from the authors' raw metadata.
3. Exclude or batch-adjust Zou.
4. Test network → David once, as the sole new headline.
