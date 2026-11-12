# Answer (Claude, round 1)

**Can a child's gut-microbial profile be used to predict ASD? On this round's evidence: not reliably across cohorts.**

In leave-one-cohort-out tests on three public 16S cohorts (331 children), a frozen abundance model reached AUC 0.47 on Ding, 0.53 on Zou and 0.55 on David. Every 95% interval includes 0.5, and no permutation p-value is below 0.15. Adding network-derived features did not help: the combined model scored 0.45, 0.50 and 0.55. The network-only model scored 0.27 on Zou, well below chance. A score that far below 0.5 means the network features ranked Zou's children in the opposite direction from the training cohorts. That points to real structure that flips between studies, not a transferable ASD signal. Reversing it after seeing the result would be fitting to the test cohort, so I did not.

Inside David, the only cohort with sex and age, those two variables alone gave AUC 0.69. The microbiome alone gave 0.51, and the microbiome plus sex and age gave 0.57, lower than the metadata alone. In this cohort the bacteria add nothing beyond demographics, and the demographic signal reflects how cases and controls were recruited (more boys among cases).

This agrees with the literature I could verify. Classifiers do well within a cohort and poorly across cohorts (Li et al. 2023). Study site and GI symptoms change the association (Fouquier et al. 2021). Age, sex and bowel function confound taxa differences (West et al. 2022). Direct ASD-microbiome links can be negligible once diet is considered (Yap et al. 2021). The one meta-analysis of the eight candidate genera I read reports pooled effects whose intervals mostly include zero (Xu et al. 2019).

**What would change my mind:** an AUC interval clearly above 0.5 on an untouched cohort from a pipeline fixed before seeing it, repeated across more than one held-out cohort, and holding after adjustment for sex and age.

**What the next round should do:**
- Add cohorts with sex and age (e.g. PRJNA895487 with family grouping; one further cohort [redacted: holdout cohort identity]).
- Prespecify one model and one network design before running.
- Report the metadata-only baseline in every cohort that has it.
- Investigate why Zou separates so strongly in opposite directions under different feature sets; this is a cohort-level difference worth explaining, not exploiting.
