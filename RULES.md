# Rules (identical for every AI)

1. **Same inputs.** Use only files in `data/` plus public sources you cite. Do not ask the human for extra hints about the data; if you need something, send the question to the human; every answer is given to all three agents.
2. **Blind holdout.** `data/holdout/` has features only. Labels are held outside the repository by the human. Do not try to infer or request them. Predictions are the only thing handed back.
3. **Everything learned from training data only.** Prevalence filters, feature selection, scaling, network construction, hyperparameter tuning, thresholds and any per-cohort adjustment must be fitted without the holdout labels. If a step uses the holdout *features* (for example per-cohort standardisation), say so in `method.md`.
4. **Cohort-wise validation.** Report leave-one-cohort-out results across the three training cohorts. Random sample splits are not accepted as evidence of generalisation. Keep siblings (`sibling_pair`) together.
5. **No fabricated evidence.** Every reference needs a working DOI or PubMed ID, and every numeric claim must be traceable to the cited text. Mark anything you could not open as UNVERIFIED. A made-up citation is a disqualifying error for that item.
6. **Honest wording.** Describe results as research-use classification of sampled children. Do not use "diagnosis", "detects autism" or "clinically validated". Report AUC with uncertainty and compare with trivial baselines.
7. **Report negative results.** A chance-level result reported honestly scores higher than an inflated one.
8. **Log everything.** Each submission has `RUN_LOG.md`: prompts or instructions given, tools used, time spent, anything the human changed or fixed.
9. **No peeking at other submissions** until all three are frozen. The human freezes them by tagging `freeze/round_NN/<agent>`.
10. **Caveat for fairness.** The human's earlier work with Claude on this dataset is outside this repository. Claude must say in its `RUN_LOG.md` what prior knowledge of these cohorts it brings.
11. **Neutral referee.** The human scores the rubric. No contestant, including Claude, grades its own work or another AI's. Contestants may help run `scorer/score.py` but not interpret rubric items.
12. **Unassigned reads.** Some columns are lineages that stop above genus (they end in `;__`). Decide whether to drop or keep them, and say which in `method.md`. Do not silently renormalise.
