# Questions from Perplexity (answers are shared with all three agents)

1. **David sex coding.** `data/train/david/labels.tsv` has controls coded f = 27, m = 22, with 8 missing. David et al. 2021 (mSystems, DOI 10.1128/msystems.00193-20) reports NT 27 male / 22 female, with 8 missing. The ASD counts match (43 m / 17 f). Are control sexes swapped in labels.tsv? The metadata-only baseline depends on this.
2. **Missing sex is label-informative.** All 8 missing-sex rows are controls. I excluded incomplete rows from the metadata baseline. Should agents treat missingness the same way?
3. **Track C deliverable.** PROMPT.md asks for `answer.md`, and TASKS.md asks for `proposal_section.md`. I delivered both. Please confirm which one is scored.
4. **Holdout timing.** `data/holdout/genus_counts.tsv` was absent on 2026-11-12, so I did not produce predictions.csv. The code writes it automatically once the file exists.
