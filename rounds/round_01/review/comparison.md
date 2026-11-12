# Round 1: side-by-side facts for the referee

Compiled by Claude, also a contestant. These are facts for scoring, not scores; the rubric (`scoring/rubric.md`) is filled by the human.

## Track A: held-out AUC (logistic regression, each agent's primary setting)

| Held out | Features | Claude AUC (perm p) | ChatGPT AUC (perm p*) | Perplexity AUC (perm p) |
|---|---|---|---|---|
| Ding | abundance | 0.469 (0.62) | 0.477 | 0.506 (0.52) |
| Ding | network | 0.401 (0.76) | 0.506 (0.42*) | 0.479 (0.60) |
| Ding | combined | 0.445 (0.71) | 0.483 (0.58*) | 0.505 (0.50) |
| Zou | abundance | 0.534 (0.43) | 0.523 | 0.705 (0.17) |
| Zou | network | 0.273 (0.91) | 0.774 (0.12*) | 0.725 (0.19) |
| Zou | combined | 0.500 (0.43) | 0.730 (0.13*) | 0.705 (0.14) |
| David | abundance | 0.548 (0.16) | 0.579 | 0.584 (0.08) |
| David | network | 0.556 (0.28) | 0.591 (0.09*) | 0.584 (0.025) |
| David | combined | 0.552 (0.16) | 0.605 (0.03*) | 0.584 (0.10) |

\* ChatGPT's network and combined p-values come from the referee's added permutation test; its own submission tested only abundance.

**Note on Zou:** sequencing depth alone predicts Zou's labels (AUC 0.93), so no Zou number above should be read as ASD signal.

## Rubric facts

| Axis | Claude | ChatGPT | Perplexity |
|---|---|---|---|
| Leakage found | None | None | None |
| Reproduces its own numbers | Yes, exactly | Yes, exactly | Primary analyses exactly; secondary forest within 0.03 (library versions) |
| Permutation null covers all reported models | Yes (C fixed in nulls) | Abundance only | Yes (full pipeline) |
| Metadata baseline in David | Yes (0.69) | Marked "not estimable" cross-cohort; no within-David version | Yes (0.64; excludes missing-sex rows) |
| Technical (depth) baseline | No | No | Yes; found the Zou confound |
| Siblings in David | Grouped | Cluster bootstrap by pair | Grouped, plus a sibling-pair concordance test |
| Environment pinned | Exact versions | Version ranges | Exact versions |
| Evidence items marked VERIFIED / UNVERIFIED | 16 / 16 | 35 / 25 | 31 / 5 |
| Evidence: verification depth claimed | Mostly abstracts; several sources blocked | Not yet checked by referee | Mostly full text, via Europe PMC |
| `answer.md` words (limit 400) | 377 | 310 | 377 |
| Prior-knowledge disclosure | Yes (pilot work; saw ChatGPT's summary early) | n/a | n/a |
| Extra findings | — | — | Zou depth confound; possible David sex-coding mismatch; Peralta-Marzal used the same cohorts |

## Still for the referee
- **Citation spot-check:** 10 random citations per agent, comparing DOI, title and numbers against the source. This is the 20-point evidence axis, and only the human can do it neutrally.
- **David sex coding:** decide using the David et al. 2021 paper.
- **Proposal text:** read the three `proposal_section.md` files.
