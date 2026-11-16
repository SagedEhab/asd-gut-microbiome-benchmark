"""Multiplicity: one Holm family over every secondary permutation-tested comparison (LOCO + within-cohort).
python code/summarise.py --out <outdir>"""
import argparse, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import holm
ap = argparse.ArgumentParser(); ap.add_argument("--out", default="."); a = ap.parse_args()
L = pd.read_csv(os.path.join(a.out, "loco_results.csv")); W = pd.read_csv(os.path.join(a.out, "within_cohort_results.csv"))
Lc = pd.read_csv(os.path.join(a.out, "c_sensitivity.csv")); Wc = pd.read_csv(os.path.join(a.out, "within_c_sensitivity.csv"))
rows = pd.concat([
    L.assign(analysis="LOCO", comparison=L.variant + "/" + L.features + "/test=" + L.test_cohort)[["analysis", "comparison", "role", "auc", "perm_p", "n_perm", "n_C_sig_fixed"]],
    W.assign(analysis="within-cohort CV", role="secondary", comparison=W.cohort + "/" + W.features)[["analysis", "comparison", "role", "auc", "perm_p", "n_perm", "n_C_sig_fixed"]]])
sec = rows.role == "secondary"
rows["holm_all_secondary"] = np.nan
rows.loc[sec, "holm_all_secondary"] = holm(rows.loc[sec, "perm_p"].values).round(4)
rows["single_C_flag"] = np.where((rows.perm_p < 0.05) & (rows.n_C_sig_fixed <= 1), "raw p<0.05 at chosen C but fixed-C p<0.05 at <=1 of 4 C values", "")
rows.to_csv(os.path.join(a.out, "multiplicity.csv"), index=False)
n_sec = int(sec.sum()); n_C = len(Lc) + len(Wc)
s = (f"Held-out comparisons with a permutation p: {len(rows)} = 1 headline + {n_sec} secondary "
     f"({int((rows.analysis=='LOCO').sum())-1} LOCO, {int((rows.analysis!='LOCO').sum())} within-cohort). "
     f"Per-C sensitivity rows (descriptive, fixed-C p): {n_C}. Secondary raw p<0.05: {int((rows[sec].perm_p<0.05).sum())}; "
     f"Holm-adjusted p<0.05: {int((rows[sec].holm_all_secondary<0.05).sum())}.")
print(s); open(os.path.join(a.out, "multiplicity_summary.txt"), "w").write(s + "\n")
print(rows[sec & (rows.perm_p < 0.05)].to_string())
