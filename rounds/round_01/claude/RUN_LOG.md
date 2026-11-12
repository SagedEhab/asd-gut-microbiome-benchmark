# Run log: claude

- **Prompt / instructions given:** the round 1 text in `rounds/round_01/PROMPT_SENT.md`, the same words given to ChatGPT and Perplexity, run in the user's Claude Code session (model: Claude Opus 5.5).
- **Tools used:** Python on the user's laptop (code execution); web search and reader agents earlier in the same session for literature; no access to holdout labels.
- **Start / end, effort:** about 40 minutes for this submission on 2026-11-12, plus about 20 minutes of compute.
- **Prior knowledge of these cohorts (fairness disclosure, required by RULES.md item 10):**
  - Before the benchmark existed, I processed all three cohorts from raw reads with the user and ran several pilot classifiers on them (abundance, network, literature-guided taxa, metadata). This submission's design, code and numbers are close to those pilots, and the leave-one-cohort-out abundance and network AUCs are the same numbers I had seen before.
  - While checking progress on 2026-11-12, I saw ChatGPT's round 1 summary table (abundance, network and combined AUCs per cohort) **before** writing this submission. I did not change any setting after seeing it: the code and design copy my earlier pilot, whose settings were fixed before ChatGPT's results existed. Treat my independence in round 1 as compromised accordingly.
  - The holdout cohort's labels are in the user's files and I have seen their group-level counts [redacted: holdout cohort identity]. No holdout file exists in the repository yet, and I made no holdout predictions.
- **Anything the human changed, fixed or re-ran:** nothing in this submission.
