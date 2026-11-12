# Run log: Perplexity

- **Prompt / instructions given (paste exactly):** the round-1 prompt from the human, verbatim. It is PROMPT.md with "Round: 1 (first round; there is no previous feedback)", the repository link, and the line "The training data files are also attached to this message where the interface allows it; they are identical to data/train/ in the repository." The six training TSVs were attached and were not used beyond confirming they match the repo.
- **Tools used:**
  - Code execution in a Linux sandbox: Python 3, scikit-learn 1.9.1, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, networkx 3.7, joblib.
  - Web search and page fetching: Europe PMC REST API, PMC full-text pages, publisher pages, Crossref, ENA portal API and GEO.
  - Tool-assisted extraction prompts for reading article text.
  - README.md says Perplexity "cannot" run code. In this round it could, so Track A was done in full.
- **Start / end time, total effort:** 2026-11-12, about 13:30–15:00 UTC (about 1.5 h wall clock). Most of the compute was 200-permutation nulls × 9 settings, with a full pipeline refit per permutation.
- **Prior knowledge of these cohorts:**
  - General background knowledge of the published literature only: Ding 2020, Zou 2020, David 2021, Peralta-Marzal 2024, Morton 2023 and the meta-analyses.
  - No prior work with the human on this dataset and no access to earlier runs.
  - I found during this round that Peralta-Marzal 2024 used exactly these three cohorts.
  - I did not look for, infer or request holdout labels, and I do not know which cohort the holdout is.
- **Anything the human changed, fixed or re-ran:** nothing.
- **Self-corrections during the run:**
  1. The first draft of the metadata baseline encoded missing sex as "not male". All 8 missing-sex children are controls, so this would have leaked the label. I replaced it with complete-case analysis and re-ran everything from scratch. Only the final run's outputs are delivered.
  2. A smoke test with 5 permutations was run before the final 200-permutation run. Its outputs were discarded.
- **Deviations:** none from RULES.md. Per-cohort standardisation is reported only as a secondary analysis and is disclosed in method.md (it uses the test cohort's features, never its labels).
