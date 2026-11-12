# Can a child's gut-microbial profile be used to predict autism?

One question, three agents (Claude, ChatGPT, Perplexity), one shared repository. Every agent receives the **same prompt** (`PROMPT.md`), in rounds, until the human decides the best solution has been reached. The answer may legitimately be "not reliably"; that is a valid result if it is shown with evidence.

Research use only. A result here is never a diagnosis.

## Where things are
```
PROMPT.md                              THE prompt. Paste it verbatim to every agent each round.
PROCESS.md                             how rounds work, the holdout rule, stopping rules, choosing the best solution
RULES.md                               fairness and integrity rules
TASKS.md                               exact deliverables per track
data/train/<cohort>/                   genus count tables + labels (Ding, Zou, David)
data/holdout/genus_counts.tsv          blind cohort features only (labels are NOT in this repo)
rounds/round_NN/<agent>/               each agent writes only here, for the current round
rounds/round_NN/FEEDBACK.md            the human's feedback to all agents after the round (identical for all)
best/                                  the current best solution and DECISIONS.md log
scorer/score.py                        scores the final round once against the private holdout labels
scoring/rubric.md, leaderboard.md      rubric and results
```

## How each agent takes part
- **Claude** and **ChatGPT** can run code. They work in their round folder and commit to their own branch (`ai/claude`, `ai/chatgpt`).
- **Perplexity** cannot run code or commit. It receives the identical prompt, answers the literature and writing tracks, and the human pastes its answer unchanged into its round folder with the exact prompt recorded in `RUN_LOG.md`.
- The human is the referee. No agent grades itself or another.

Start with `PROCESS.md`, then `PROMPT.md`.
