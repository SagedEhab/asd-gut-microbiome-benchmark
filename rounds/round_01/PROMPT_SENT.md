Round: 1 (first round; there is no previous feedback)
Repository (public, read-only for you): https://github.com/SagedEhab/asd-gut-microbiome-benchmark

You are one of three AI agents (Claude, ChatGPT and Perplexity) working on the same research question in that shared repository:

"Can a child's gut-microbial profile be used to predict autism spectrum disorder (ASD)?"

The work is research-use only: classification of sampled ASD and control children from public 16S rRNA gut-microbiome data. Never describe the output as a diagnosis or as clinically validated.

Read, in this order: README.md, PROCESS.md, RULES.md, TASKS.md and data/README.md in the repository. The training data files are also attached to this message where the interface allows it; they are identical to data/train/ in the repository.

The repository is public and read-only for you. Do not try to commit to it. Return your deliverables to me as files (attachments, or one clearly named block per file), using the file names in TASKS.md. I file them under rounds/round_01/<your name>/ and publish them only after all three agents' work for the round is frozen.

Your job this round:
1. Track A, classifier. Using only data/train/, build the best honest cross-cohort classifier you can, evaluated leave-one-cohort-out with siblings kept together. If data/holdout/genus_counts.tsv exists, also predict it; if it does not exist yet, skip predictions.csv this round. Compare abundance-only, network-derived and combined features on identical splits, with a metadata-only baseline wherever sex/age exist and a label-permutation null.
2. Track B, evidence. Produce a verified evidence audit exactly as specified in TASKS.md. Every citation needs a DOI or PubMed ID and a VERIFIED / UNVERIFIED mark. Never invent a reference.
3. Track C, answer. In answer.md, answer the question in at most 400 words: what the evidence in this round supports, how strongly, what would change your mind, and what the next round should do differently.

Rules that matter most: fit everything on training data only; the holdout labels are not available to you and must not be sought; report negative or chance-level results plainly; log your instructions and effort in RUN_LOG.md (template in templates/). If you cannot run code, say so and do Tracks B and C.

Earlier rounds in rounds/ are public and you may read them; the current round's work of other agents is not available until it is frozen. Stop when your deliverables are complete; do not wait for approval.

---
Sent 2026-11-12, identical text to each agent, with the six training files attached (ding/zou/david genus_counts.tsv and labels.tsv, renamed with a cohort prefix):
- ChatGPT (Plus, default "Medium" setting): https://chatgpt.com/c/6af5c47d-d794-83e9-b933-2d9f4ef4d360
- Perplexity (Pro, "Computer" mode, Standard): https://www.perplexity.ai/session/915d953a-28a2-4326-a461-57926667277e
- Claude: same text, to be run in this Claude Code session (not yet started).
Whitespace differs slightly between interfaces (paragraph spacing); the words are identical (checked character by character, ignoring whitespace).
