# Scoring (100 points)

Predictive performance is deliberately a small part. With about 90 holdout children, AUC near 0.5 is the realistic range for every method, so ranking on it alone would mostly reward luck. If two AUC 95% intervals overlap, performance is a tie and both receive the same points.

| Axis | Points | Who scores | What earns points |
|---|---|---|---|
| Methodological integrity | 25 | referee + reviewer checklist below | No leakage; everything fitted on training only; cohort-wise validation; siblings grouped; baselines and permutation null present |
| Reproducibility | 20 | referee | One command reproduces `predictions.csv` and `loco_results.csv`; environment pinned; random seeds fixed |
| Honest reporting | 20 | referee | Results described at their real strength; uncertainty shown; limitations stated; wording follows RULES.md |
| Evidence quality (Track B) | 20 | referee spot-checks 10 random citations per AI | DOI resolves, title and numbers match the source; UNVERIFIED items marked as such |
| Proposal text (Track C) | 5 | referee | Clear, accurate, no overclaim |
| Predictive performance | 10 | `scorer/score.py` | Holdout AUC rank with CI-overlap ties: 10 / 6 / 3 (distinct) or equal split when tied |

## Not like-for-like across AIs
Perplexity cannot run code, so it cannot earn the Track A parts of integrity, reproducibility or performance. Report two things: (1) a winner per track (A classifier, B evidence, C proposal text); (2) an overall percentage = points earned / points available on the tracks that AI attempted. Do not rank an AI that skipped Track A against one that did it on the raw 100-point total.

## Penalties
- Fabricated or non-existent citation: -10 each (cap -30).
- Evidence of using holdout labels or guessing them: disqualified from Track A.
- Using "diagnosis" claims for the model: -5.
- Hand-edited results that the code does not reproduce: -10.

## Reviewer checklist (Track A)
- [ ] Any feature selection or scaling fitted on all cohorts together?
- [ ] Hyperparameters chosen using the held-out training cohort's labels?
- [ ] Same child appears in both train and test (siblings, repeated samples)?
- [ ] Holdout features used only as described in `method.md`?
- [ ] Network features computed for a new child from the training reference only?
- [ ] Baselines (all-genera abundance, metadata-only) reported?
