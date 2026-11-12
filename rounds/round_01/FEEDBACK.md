# Round 1 feedback (identical for all three agents)

Drafted by Claude (also a contestant) and approved by the human referee on 2026-11-12. It contains no holdout numbers (no holdout exists yet).

**Status:** all three agents (Claude, ChatGPT, Perplexity) submitted Track A, B and C deliverables, with code.

## New findings from round 1 that every agent must take into account
- **Zou has a strong technical confound.** Sequencing depth alone separates Zou's ASD and control samples: depth-only AUC 0.93, with controls sequenced deeper (median 43,289 vs 32,168 reads). Raw read counts before processing also separate them (AUC 0.77). This was found by one submission and confirmed by the referee. Any Zou result, high or low, may reflect depth or batch rather than ASD.
- **David sex coding is disputed.** `labels.tsv` matches the authors' metadata file (controls 27 female / 22 male; all 8 missing-sex rows are controls). One submission reports that the paper's text gives the reverse for controls. This is unresolved for now. Until it is settled, report sex/age baselines as provisional, and exclude missing-sex rows rather than encoding missingness, which would leak the label.

## What went well
- Both code submissions reproduce their own numbers exactly when rerun on `data/train/`.
- No leakage was found: no held-out cohort labels are used, the vocabulary filter and network weights are fitted on training data, and hyperparameters are chosen on training cohorts only.
- Both submissions report chance-level results plainly and avoid diagnostic claims.

## Required changes for round 2 (all agents)

1. **Permutation null for every reported model, not only abundance.** Rerun the whole pipeline, including hyperparameter choice, on labels shuffled within each training cohort; at least 200 permutations; report the null's mean and 95% range and a one-sided p. In round 1, a held-out AUC of about 0.77 turned out to fall inside the range that shuffled labels also reach, so an AUC without its own null cannot be interpreted.

2. **Hyperparameter sensitivity.** For every model, report held-out AUC at each value of the regularisation grid, not only the chosen value. Flag any result that holds at only one setting.

3. **Count the comparisons.** State how many held-out comparisons you report, and give a multiplicity-adjusted view (for example Holm) of the permutation p-values next to the raw ones.

4. **Explain the Zou cohort.** Network-derived features gave AUC far below 0.5 on Zou in one submission and far above 0.5 in another. Investigate what drives Zou's separation: its 16S region (V3-V4 against V4 elsewhere), sequencing depth, the genus-name harmonisation, or overall composition shift. Say whether the signal is ASD-related or cohort structure. Do not flip a score after seeing its direction.

5. **Genus harmonisation as a stated choice.** Say whether genera are keyed by genus name alone or by family plus genus, and show whether results change between the two.

6. **Metadata baseline in David, from everyone.** Report metadata-only (sex, age), microbiome-only and combined models inside David with sibling pairs kept together, and say whether the microbiome adds anything beyond sex and age.

7. **Evidence audit hygiene.** Keep the VERIFIED / UNVERIFIED marks, and make "verified" mean that you opened the primary source (say whether abstract or full text). Any number you could not see in the source stays UNVERIFIED, even if a review quotes it.

8. **Technical baselines in every cohort.** Report depth-only and richness-only models next to the microbiome models, and test whether results hold on depth-matched or rarefied samples.

9. **Sibling-pair test in David.** Report the fraction of discordant sibling pairs in which the ASD child scores higher. This is a within-family comparison that sidesteps between-cohort and household differences.

10. **One prespecified headline model.** Before running round 2, write down in `method.md` which single model and setting is your headline result, then report everything else as secondary.

## Answers to agents' questions (shared with all)
- *Which Track C file is scored?* Both: `answer.md` is the Track C answer (PROMPT.md), and `proposal_section.md` is scored as proposal text (TASKS.md).
- *Missing sex in David:* exclude incomplete rows from metadata models and say so; never encode missingness as a feature.
- *Holdout:* still absent. Make no predictions until `data/holdout/genus_counts.tsv` exists.

## Unchanged
Same data, same rules, same deliverables, same 400-word limit for `answer.md`. No holdout predictions until the holdout file appears in `data/holdout/`.
