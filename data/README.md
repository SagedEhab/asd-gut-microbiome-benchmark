# Data notes
- Counts are reads assigned at genus level by one shared pipeline (QIIME2 DADA2, SILVA 138 99%). Column names are SILVA lineages; genus names are the last `g__` field. Spelling and rank prefixes differ slightly between cohorts, so harmonise by genus name and record how.
- Ding and Zou: V4 vs V3-V4 sequencing, labels from sample names, no age or sex.
- David: sibling-matched, has sex, age and `sibling_pair`; keep pairs together.
- Counts are not relative abundance; samples have different depths.
- `holdout/genus_counts.tsv` has features only (added when the holdout cohort is processed). Labels are not in this repository.
