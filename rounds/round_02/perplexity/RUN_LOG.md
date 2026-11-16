# Run log: Perplexity, round 2

## Prompt and instructions
- **Prompt (paste exactly):** the human's round-2 message, which is `rounds/round_02/PROMPT.md` ("Round: 2. The round 1 feedback is copied at the end of this message ..."), followed verbatim by `rounds/round_01/FEEDBACK.md`:
  - "Required changes for round 2 (all agents)", items 1–10;
  - "Answers to agents' questions": both answer.md and proposal_section.md are scored; exclude rows with missing sex; no predictions while the holdout is absent; David sex/age baselines are provisional; the 400-word limit stays.
- **Repo state:** HEAD e1c4754, pulled on 2026-11-12. `data/holdout/` is absent, so there is no `predictions.csv`.

## Tools used
- Code execution in a Linux sandbox with 2 CPUs. Python 3.14.8, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, scikit-learn 1.9.1, networkx 3.7, joblib 1.6.0.
- HTTP downloads:
  - Europe PMC REST: fullTextXML and core abstracts;
  - PMC article pages for Dan 2020, Vujkovic-Cvijin 2020 and Sinha 2017;
  - the PubMed page for Wan 2022, whose Europe PMC abstract is truncated;
  - the ENA portal API (run tables for PRJNA578223 and PRJNA589343).
- **Evidence was checked by regex over downloaded text** (`lit/check.py` → `lit/grep_results.tsv`), not by LLM extraction prompts as in round 1.

## Timing and effort
- **Start / end:** 2026-11-12, about 14:18–15:40 UTC (about 1.5 h wall clock).
- **Preregistration:** `PREREGISTRATION.md` was written at 14:29:55 UTC, before any round-2 model run (sha256 `abc45b07…5815`).
- **Final LOCO run:** 14:42–14:54 UTC.
  - 1,000 permutations × 5 feature kinds for the headline variant;
  - 200 permutations × 4–5 kinds for each of 3 other variants;
  - every permutation is a full pipeline refit with C re-chosen.
- **Within-cohort run:** 14:54–15:08 UTC.
- **Reproduction:** `code/run.sh` was rerun from scratch into a fresh directory, started 15:09 UTC; the result is noted at the bottom.

## Prior knowledge
- My own round-1 submission and all of `rounds/round_01/` (other agents' work and the referee checks) were read before the preregistration was written.
- **The headline is therefore prespecified for round 2 but not blind to round-1 results.**
- I did not seek or infer holdout labels, and I do not know the holdout cohort.

## Ideas taken from others (FEEDBACK allows this)
- **Claude, round 1:**
  - CLR with pseudocount 0.5 instead of log-proportions;
  - the family|genus harmonisation key.
- **ChatGPT, round 1:** permuting David labels within sibling families for the null.
- **Referee (review/verify_chatgpt_zou.py and FEEDBACK):**
  - re-choosing C inside every permutation;
  - per-C reporting;
  - the observation that Zou's null is wide.
- **Mine, round 1, kept:**
  - depth-by-label diagnostics;
  - within-David complete-case metadata baseline;
  - sibling concordance.

## Deviations, judgement calls and self-corrections
1. **Random forest was dropped.** Full-pipeline nulls at ≥ 200 permutations for every model were the priority, and fewer models means fewer comparisons.
2. **Within-cohort CV uses fixed splits.** The splits are drawn from the true labels and reused for every permutation. Features are label-free, so caching is valid.
   - To fit the compute budget: 2 repeats of 5-fold, and an inner 3-fold for C.
   - A 4-permutation smoke test with 5 repeats was run first and discarded.
3. **A first LOCO run crashed after the headline variant** (a bug in log handling in `run_all.py`). It was fixed and the run restarted from scratch with the same seed; only the restarted outputs are delivered.
4. **I edited `run.sh` while a reproduction run was in progress.** I killed that run and restarted it, because bash reads scripts incrementally.
5. **The Holm view is bounded by permutation resolution.** 200 permutations give a floor of p = 0.005, which cannot pass Holm across 105 tests. This is stated in method.md rather than hidden by adding permutations selectively.
6. **Round-1 evidence claims downgraded to UNVERIFIED** because they are not in the text:
   - Li 2023 "median external AUC 0.60" and "missing features set to zero";
   - Xu 2019 Parabacteroides 0.3 vs 0.5;
   - Son 2015 ages;
   - Kang 2013 n and ages;
   - Dan 2020 per-group split.

   **Corrected:** the Scanu 2024 R² values are now quoted verbatim.
7. **No score was re-signed after seeing its direction.** Label-free PCs are reported as computed, together with |AUC − 0.5|.

## Human changes
None.

## Reproduction
`bash code/run.sh ../repo/data /tmp/repro` was run in a fresh directory, starting 15:09 UTC, with seed 20261112.
- `run_all.py` finished, and so did `within.py` for Ding and Zou. The session then ended `within.py` during the David step, so no David delta or summary files were written.
- I reran `within.py`, then `zou.py` and `summarise.py` (the same commands as in `run.sh`), into the same directory at 15:37 UTC. All of them finished.
- **Outcome:** every result file is byte-identical to the delivered results:
  - LOCO and settings: loco_results, c_sensitivity, oof_scores, harmonisation_log, depth_by_label;
  - within-cohort: within_cohort_results, within_c_sensitivity, within_{ding,zou,david}_oof_scores, david_delta;
  - other: zou_diagnostics, multiplicity, multiplicity_summary.
- Only `run_output_log.txt` differs, and only in timestamps and run times.
