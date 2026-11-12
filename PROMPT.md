# Prompt (identical for every agent; paste verbatim)

Round: NN   (fill in the round number; previous round = NN-1)
Changes since last round: see rounds/round_(NN-1)/FEEDBACK.md (identical for all agents). Round 1 has none.

---

You are one of three AI agents working on the same research question in a shared repository:

> **Can a child's gut-microbial profile be used to predict autism spectrum disorder (ASD)?**

The work is research-use only: classification of sampled ASD and control children from public 16S rRNA gut-microbiome data. Never describe the output as a diagnosis or as clinically validated.

Read, in this order: `README.md`, `PROCESS.md`, `RULES.md`, `TASKS.md`, `data/README.md`, and the previous round's `FEEDBACK.md` if it exists.

The repository is public and read-only for you. Do not try to commit to it. Return your deliverables to the human as files (attachments, or one clearly named block per file), using the file names in `TASKS.md`. The human files them under `rounds/round_NN/<your name>/` and publishes them only after all three agents' work for the round is frozen.

Your job this round:
1. **Track A, classifier.** Using only `data/train/`, build the best honest cross-cohort classifier you can, evaluated leave-one-cohort-out with siblings kept together. If `data/holdout/genus_counts.tsv` exists, also predict it; if it does not exist yet, skip `predictions.csv` this round. Compare abundance-only, network-derived and combined features on identical splits, with a metadata-only baseline wherever sex/age exist and a label-permutation null.
2. **Track B, evidence.** Produce a verified evidence audit exactly as specified in `TASKS.md`. Every citation needs a DOI or PubMed ID and a VERIFIED / UNVERIFIED mark. Never invent a reference.
3. **Track C, answer.** In `answer.md`, answer the question in at most 400 words: what the evidence in this round supports, how strongly, what would change your mind, and what the next round should do differently.

Rules that matter most: fit everything on training data only; the holdout labels are not available to you and must not be sought; report negative or chance-level results plainly; log your instructions and effort in `RUN_LOG.md`. If you cannot run code, say so and do Tracks B and C.

Earlier rounds in `rounds/` are public and you may read them; the current round's work of other agents is not available until it is frozen. Stop when your deliverables are complete; do not wait for approval.
