# Process

## Rounds
1. The human pastes `PROMPT.md` (with the round number filled in) to Claude, ChatGPT and Perplexity, unchanged.
2. Each agent works only in `rounds/round_NN/<agent>/`. Code-capable agents also commit to their own branch.
3. The human freezes each submission with the tag `freeze/round_NN/<agent>`, then reads all three.
4. The human writes ONE `rounds/round_NN/FEEDBACK.md` for all three: integrity problems found, missing analyses, disputed claims, what to do next. It must be identical for every agent and must contain **no holdout numbers**.
5. Move to the next round with the same prompt text; only the round number and the feedback file change.

## Holdout discipline (the key safeguard)
Repeating rounds against one holdout would turn it into a tuning set. Therefore:
- **Between rounds the holdout is never scored.** Rounds are judged on leave-one-cohort-out results from the training cohorts, on integrity and on evidence quality.
- The holdout is scored **once**, at the end, for the final round (`python scorer/score.py --round NN --final`). The scorer writes `scoring/FINAL_SCORED` and refuses to run again.
- If a better design needs a new holdout, add a new cohort for it; do not reuse the first.

## Choosing the best solution
Per round the human scores `scoring/rubric.md` for each agent and records it in `scoring/leaderboard.md`. The best solution is the one with the highest rubric score on its own track, and it may combine parts from different agents; record which parts and why in `best/DECISIONS.md`. Accuracy alone never decides.

## Stopping
Stop when any one holds:
- two consecutive rounds show no improvement in leave-one-cohort-out results beyond their uncertainty, and no new integrity issues;
- the human judges the answer to the umbrella question to be stable and well supported;
- the round cap (default 4) is reached.
Then run the one final holdout scoring and write the final answer, positive or negative, with its limits.
