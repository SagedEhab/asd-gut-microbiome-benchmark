"""Round-2 LOCO driver. python code/run_all.py --data <repo>/data --out <outdir>
Headline (preregistered): famgenus, raw counts, abundance, mean of 3 LOCO AUCs, 1000 perms.
All other rows are secondary and Holm-adjusted as one family."""
import argparse, os, sys, time
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_raw, holm, SEED
from loco import analyse_variant, KINDS
from scipy.stats import mannwhitneyu
from sklearn.metrics import roc_auc_score

ap = argparse.ArgumentParser(); ap.add_argument("--data", default="data"); ap.add_argument("--out", default=".")
ap.add_argument("--n_head", type=int, default=1000); ap.add_argument("--n_sec", type=int, default=200)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
logf = open(os.path.join(a.out, "run_output_log.txt"), "a")
def log(m): print(m, flush=True); logf.write(m + "\n"); logf.flush()
log(f"start {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC seed={SEED}")
raws, L = load_raw(a.data)
rng = np.random.default_rng(SEED)
rows, crows, oofs, hlogs = [], [], [], []
for key, rar, n in [("famgenus", False, a.n_head), ("genus", False, a.n_sec), ("famgenus", True, a.n_sec), ("genus", True, a.n_sec)]:
    r, c, o, h = analyse_variant(raws, L, key, rar, n, KINDS, rng, log)
    pd.DataFrame(r).to_csv(os.path.join(a.out, f"partial_{key}_{int(rar)}.csv"), index=False)
    rows += r; crows += c; oofs.append(o); h = pd.DataFrame(h); h["variant"] = f"{key}{'_rarefied' if rar else ''}"; hlogs.append(h)
R = pd.DataFrame(rows); C = pd.DataFrame(crows)
R["role"] = "secondary"
head = (R.variant == "famgenus") & (R.features == "abundance") & (R.test_cohort == "mean")
R.loc[head, "role"] = "HEADLINE"
sec = R.role == "secondary"
R["holm_p_secondary"] = np.nan
R.loc[sec, "holm_p_secondary"] = holm(R.loc[sec, "perm_p"].values).round(4)
# single-setting flag: how many C values give fixed-C p<0.05
nsig = C.assign(sig=C.perm_p_fixedC < 0.05).groupby(["variant", "features", "test_cohort"]).sig.sum().rename("n_C_sig_fixed").reset_index()
R = R.merge(nsig, on=["variant", "features", "test_cohort"], how="left")
R["flag"] = np.where((R.perm_p < 0.05) & (R.n_C_sig_fixed <= 1), "holds_at_<=1_C", "")
C = C.merge(nsig, on=["variant", "features", "test_cohort"], how="left")
R.to_csv(os.path.join(a.out, "loco_results.csv"), index=False)
C.to_csv(os.path.join(a.out, "c_sensitivity.csv"), index=False)
pd.concat(oofs).to_csv(os.path.join(a.out, "oof_scores.csv"), index=False)
pd.concat(hlogs).to_csv(os.path.join(a.out, "harmonisation_log.csv"), index=False)
# multiplicity across all analyses is written by summarise.py
log(f"held-out comparisons in loco_results: headline 1, secondary {int(sec.sum())} (chosen-C); per-C rows {len(C)}")
log(f"secondary raw p<0.05: {int((R.loc[sec,'perm_p']<0.05).sum())}; Holm p<0.05: {int((R.loc[sec,'holm_p_secondary']<0.05).sum())}")
log("HEADLINE: " + R.loc[head].to_string())
# depth / richness by label
d = L.depth; rows = []
for c in ["ding", "zou", "david"]:
    m = L.cohort == c; y = L.y[m]; X = raws[c]
    rich = (X > 0).sum(axis=1).reindex(L.index[m])
    dd = d[m]
    rows.append(dict(cohort=c, n=int(m.sum()), median_depth_ASD=dd[y == 1].median(), median_depth_control=dd[y == 0].median(),
                     auc_depth_for_ASD=round(roc_auc_score(y, dd), 3), mannwhitney_p=mannwhitneyu(dd[y == 1], dd[y == 0]).pvalue,
                     auc_observed_genera_for_ASD=round(roc_auc_score(y, rich), 3)))
pd.DataFrame(rows).to_csv(os.path.join(a.out, "depth_by_label.csv"), index=False)
log(pd.DataFrame(rows).to_string()); log(f"end {time.strftime('%H:%M:%S', time.gmtime())}")
