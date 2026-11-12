# Data notes
- Counts are reads assigned at genus level by one shared pipeline (QIIME2 DADA2, SILVA 138 99%). Column names are SILVA lineages; genus names are the last `g__` field. Spelling and rank prefixes differ slightly between cohorts, so harmonise by genus name and record how.
- Ding and Zou: V4 vs V3-V4 sequencing, labels from sample names, no age or sex.
- David: sibling-matched, has sex, age and `sibling_pair`; keep pairs together.
- Counts are not relative abundance; samples have different depths.
- `holdout/genus_counts.tsv` has features only (added when the holdout cohort is processed). Labels are not in this repository.
- Sample ids are strings. David ids are prefixed `david_` (original ids look like numbers, e.g. 103 and 151.6).
- Ding has 122 samples after dropping those under 5,000 reads (76 ASD / 46 control); the raw project lists 127 (77 / 50).
- Columns ending in `;__` or stopping above genus are reads the classifier could not assign to a genus.
- Zou has four runs missing from the repository download (92 of 96 used); labels for Ding and Zou come from sample names and are provisional.
