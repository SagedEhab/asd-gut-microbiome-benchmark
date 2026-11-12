# Process

## Rounds
Two repositories:
- **Public task repo** (this one, read-only for agents): prompt, rules, tasks, scorer, training data, holdout features, and frozen past rounds.
- **Private results repo** (on the human's machine only): the current round's submissions, feedback drafts, leaderboard, `best/` and decisions.

1. The human gives `PROMPT.md` (with the round number filled in) to Claude, ChatGPT and Perplexity, unchanged, with a link to this repository.
2. Each agent returns its files to the human. The human stores them unchanged in the private results repo under `rounds/round_NN/<agent>/` and commits them with the tag `freeze/round_NN/<agent>`.
3. When all three are frozen, the human reads them and writes ONE `FEEDBACK.md` for all three: integrity problems, missing analyses, disputed claims, what to do next. It must be identical for every agent and contain **no holdout numbers**.
4. The human copies `rounds/round_NN/` (all three folders plus `FEEDBACK.md`) into this public repo and pushes.
5. Next round: same prompt text; only the round number changes, and the new feedback is now public.

## Holdout discipline (the key safeguard)
Repeating rounds against one holdout would turn it into a tuning set. Therefore:
- **Between rounds the holdout is never scored.** Rounds are judged on leave-one-cohort-out results from the training cohorts, on integrity and on evidence quality.
- The holdout is scored **once**, at the end, for the final round (`python scorer/score.py --round NN --final`). The scorer reads the round from the private results repo, writes `FINAL_SCORED` there and refuses to run again.
- If a better design needs a new holdout, add a new cohort for it; do not reuse the first.

## Choosing the best solution
Per round the human scores `scoring/rubric.md` for each agent and records it in the private results repo (`scoring/leaderboard.md`), published with the round. The best solution is the one with the highest rubric score on its own track, and it may combine parts from different agents; record which parts and why in `best/DECISIONS.md` in the results repo. Accuracy alone never decides.

## Stopping
Stop when any one holds:
- two consecutive rounds show no improvement in leave-one-cohort-out results beyond their uncertainty, and no new integrity issues;
- the human judges the answer to the umbrella question to be stable and well supported;
- the round cap (default 4) is reached.
Then run the one final holdout scoring and write the final answer, positive or negative, with its limits.
