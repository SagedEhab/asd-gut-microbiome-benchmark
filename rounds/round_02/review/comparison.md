# Round 2: side-by-side facts for the referee

Compiled by Claude, also a contestant. These are facts for scoring, not scores; the rubric (`scoring/rubric.md`) is filled by the human.

## Each agent's prespecified headline

| | Claude | ChatGPT | Perplexity |
|---|---|---|---|
| Features | abundance, family\|genus | abundance, family\|genus | abundance, family\|genus |
| Reads | rarefied to 5,000 | raw counts | raw counts |
| C | nested from {0.001…1} | fixed 0.01 | nested from {0.001…1} |
| Statistic | each held-out cohort, Holm across 3 | each held-out cohort, Holm across 3 | mean of 3 held-out AUCs, plus a mean without Zou |
| Result | Ding 0.469, Zou 0.360, David 0.561 (best p 0.25) | Ding 0.470, Zou 0.573, David 0.551 (best p 0.18) | mean 0.583 (p 0.20); without Zou 0.544 (p 0.34) |
| Verdict | null | null | null |

All three answers say "no" to cross-cohort prediction on this evidence.

## Track A: held-out AUC, logistic regression, nested C, unrarefied family|genus (closest like-for-like rows)

| Held out | Features | Claude AUC† | ChatGPT AUC (p) | Perplexity AUC (p) |
|---|---|---|---|---|
| Ding | abundance | 0.484 | 0.484 (0.49) | 0.500 (0.57) |
| Ding | network | 0.430 | 0.509 (0.45) | 0.407 (0.79) |
| Ding | combined | 0.463 | 0.485 (0.53) | 0.483 (0.61) |
| Zou | abundance | 0.534 | 0.535 (0.58) | 0.662 (0.26) |
| Zou | network | 0.273 | 0.655 (0.40) | 0.845 (0.03) |
| Zou | combined | 0.500 | 0.536 (0.63) | 0.614 (0.36) |
| David | abundance | 0.582 | 0.585 (0.08) | 0.587 (0.08) |
| David | network | 0.556 | **0.618 (0.010)** | **0.617 (0.008)** |
| David | combined | 0.581 | 0.578 (0.09) | 0.595 (0.05) |

† Claude ran its permutation nulls only on its rarefied headline variant (Ding 0.469 / 0.356 / 0.447, Zou 0.360 / 0.586 / 0.344, David 0.561 / 0.547 / 0.555; all p ≥ 0.25), so its unrarefied rows have no p.

**Points of agreement:**
- Ding is at chance for every agent and feature set.
- Zou numbers swing widely between agents (0.34–0.85). All three agents report the Zou depth confound, and Perplexity also shows Zou's permutation null spans about 0.26–0.83, so none of these Zou values is evidence either way.
- **Network features on David give about 0.62 for both ChatGPT and Perplexity**, built independently with different network definitions. Neither survives its agent's own multiplicity correction (ChatGPT Holm 0.09 across 9 or 0.31 across 31; Perplexity Holm 0.71–0.78 across 89–105). Claude's network gives 0.556 (unrarefied) and 0.547 (rarefied) on David.
- Abundance on David is 0.58–0.59 for all three agents unrarefied, with p around 0.08 where tested.

## Within David: does the microbiome add to sex and age?

| | Claude | ChatGPT (submitted / referee rerun) | Perplexity |
|---|---|---|---|
| | Claude | ChatGPT (submitted / referee rerun) | Perplexity (submitted / referee rerun) |
|---|---|---|---|
| Sex + age only | 0.659 | 0.652 / 0.660 | 0.603 / 0.552 |
| Microbiome only | 0.475 | 0.439 / 0.529 | 0.492 / 0.510 |
| Both | 0.513 | 0.486 / 0.561 | 0.507 / 0.509 |
| Sex coding swapped in controls | not run | not run | metadata 0.521 / 0.506 |

All three, in both runs: the microbiome does not beat sex and age, and adding it does not help. Perplexity's family-bootstrap 95% CI for the change from adding the microbiome is −0.22 to 0.03 (rerun −0.16 to 0.08). The metadata baseline depends on the disputed control sex coding and on fold assignment.

## Rubric facts

| Axis | Claude | ChatGPT | Perplexity |
|---|---|---|---|
| Leakage found | None | None | None (see `perplexity_check.md`) |
| Reproduces its own numbers | Yes, exactly | Cross-cohort exactly; within-David grouped CV differs by up to 0.09 (sklearn fold assignment) | Held-out AUCs exactly; permutation p within 0.08; within-cohort CV differs by up to 0.22 (David metadata 0.60 → 0.55) |
| Headline written before running | Yes (`HEADLINE_LOCKED.md`) | Yes (declared in method) | Yes (`PREREGISTRATION.md`, timestamp self-reported) |
| Permutation null re-chooses C | Yes | Yes | Yes |
| Permutations, headline | 1,000 | 200 | 1,000 |
| Multiplicity correction | Holm across 3 and 9 | Holm across 3, 9, 18, 31 | Holm across all 105 secondary tests |
| Depth / richness baselines | Yes | Yes | Yes, plus depth-matched subsets |
| Rarefaction sensitivity | Yes (headline) | Yes | Yes (two key variants) |
| Sex-coding sensitivity | No | No | Yes |
| Zou diagnostics | Depth | Depth, cohort identity (0.993) | Depth, ENA submission order, label-free distance to other cohorts, depth-residualised scores |
| Environment pinned | Exact versions | Version ranges | Exact versions |
| `answer.md` words (limit 400) | 369 | 351 | 394 |
| Prior-knowledge disclosure | Yes (pilot work, round 1 of all agents) | n/a | Yes (read all of round 1 before preregistering) |
| Evidence method | Abstracts and full text; round 1 items carried forward | Not yet checked by referee | Regex over downloaded full text (`lit/check.py`), with downgrades of round-1 claims stated |

## Matters for the referee

1. **Citation spot-check:** 10 random citations per agent. This is the evidence axis and only the human can do it neutrally.
2. **David control sex coding.** Paper (Table 1) says NT 27 m / 22 f; `labels.tsv`, matching the authors' metadata file, has 22 m / 27 f. Perplexity quotes the paper verbatim. The decision changes the metadata baseline (0.60 vs 0.52 in Perplexity's run).
3. **Questions raised by agents:**
   - ChatGPT: a shared sample-overlap audit before the holdout.
   - Perplexity: whether Zou stays a training cohort; the scope of the Holm family; the permutation count for secondary tests; whether an agent may change its headline (e.g. network → David as a new single primary).
4. **Proposal text:** read the three `proposal_section.md` files.
