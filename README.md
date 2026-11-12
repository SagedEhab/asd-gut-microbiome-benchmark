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
rounds/round_NN/                       FROZEN past rounds only (each agent's files + FEEDBACK.md), added by the human
templates/                             RUN_LOG.md and QUESTIONS.md for agents to fill in
scorer/score.py                        scores the final round once against the private holdout labels
scoring/rubric.md                      how each round is judged
```

## How each agent takes part
- This repository is **public and read-only** for the agents. Nobody commits to it except the human.
- Every agent returns its files to the human, who stores them in a private results repo until all three are frozen, then publishes the round here.
- **Claude** and **ChatGPT** can run code; **Perplexity** cannot, and does the literature and writing tracks.
- The human is the referee. No agent grades itself or another.

Start with `PROCESS.md`, then `PROMPT.md`.
