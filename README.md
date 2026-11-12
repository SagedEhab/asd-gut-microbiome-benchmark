# ASD gut-microbiome benchmark: Claude vs Codex vs Perplexity

One shared repository, one task brief, one scorer. Each AI works only in its own folder under `submissions/`. At the end the scorer and the rubric in `scoring/` decide which did best, on more than one axis.

## The question every AI answers
Can public paediatric 16S gut-microbiome profiles classify ASD versus control **in a cohort the model has never seen**, and do network-derived features add anything beyond taxonomic abundance? The output is research-use classification only. It is not a diagnosis, and no AI may describe it as one.

## Layout
```
data/train/<cohort>/genus_counts.tsv   samples x genera counts (QIIME2/DADA2/SILVA 138, collapsed to genus)
data/train/<cohort>/labels.tsv         sample_id, diagnosis (ASD/Control), plus sex/age/sibling_pair where they exist
data/holdout/genus_counts.tsv          blind test cohort features (NO labels in this repository)
RULES.md                               fairness rules, read first
TASKS.md                               three tracks and exact deliverables
scorer/score.py                        automatic scoring of predictions against private labels
scoring/rubric.md                      manual rubric and weights
submissions/<ai>/                      the only place that AI writes
```

## How each AI takes part
- **Claude** and **Codex** can run code: they work in their folder, commit on their own branch (`ai/claude`, `ai/codex`).
- **Perplexity** cannot run code or commit: it answers the literature track (and may write method text). The human pastes its output into `submissions/perplexity/` unchanged and records the exact prompt in `RUN_LOG.md`.
- The human is the referee: runs `scorer/score.py`, fills the rubric, and records the result in `scoring/leaderboard.md`.

Start with `RULES.md`.
