"""Technical-confound diagnostic: sequencing depth by label within each training cohort.
python code/diagnostics.py --data <repo>/data  -> depth_by_label.csv"""
import argparse, numpy as np, pandas as pd
from scipy.stats import mannwhitneyu
from sklearn.metrics import roc_auc_score
ap = argparse.ArgumentParser(); ap.add_argument("--data", default="data"); a = ap.parse_args()
rows = []
for c in ["ding", "zou", "david"]:
    X = pd.read_csv(f"{a.data}/train/{c}/genus_counts.tsv", sep="\t", index_col=0); X.index = X.index.astype(str)
    L = pd.read_csv(f"{a.data}/train/{c}/labels.tsv", sep="\t", dtype={"sample_id": str}).set_index("sample_id").loc[X.index]
    d = X.sum(axis=1); y = (L.diagnosis == "ASD").astype(int)
    rich = (X > 0).sum(axis=1)
    rows.append(dict(cohort=c, median_depth_ASD=d[y == 1].median(), median_depth_control=d[y == 0].median(),
                     auc_depth_for_ASD=round(roc_auc_score(y, d), 3), mannwhitney_p=mannwhitneyu(d[y == 1], d[y == 0]).pvalue,
                     auc_observed_genera_for_ASD=round(roc_auc_score(y, rich), 3)))
pd.DataFrame(rows).to_csv("depth_by_label.csv", index=False); print(pd.DataFrame(rows).to_string())
