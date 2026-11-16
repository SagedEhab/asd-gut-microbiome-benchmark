"""Why does Zou separate?  Label-free and technical diagnostics (secondary, descriptive).
python code/zou.py --data <repo>/data --ena <dir with PRJNA578223.tsv, PRJNA589343.tsv> --loco <loco outdir> --out <outdir>
No score is re-signed after seeing its direction: every AUC is reported as computed (ASD = positive class),
and label-free scores (PCs) are reported with |AUC-0.5| alongside because their sign is arbitrary by construction."""
import argparse, os, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr, mannwhitneyu
from sklearn.metrics import roc_auc_score as AUC
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_raw, harmonise, key_of, SEED, PSEUDO, PREV, RAREFY_DEPTH

ap = argparse.ArgumentParser(); ap.add_argument("--data", default="data"); ap.add_argument("--ena", default=".")
ap.add_argument("--loco", default="."); ap.add_argument("--out", default=".")
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
raws, L = load_raw(a.data)
rows = []
def add(check, value, note=""):
    rows.append(dict(check=check, value=value if isinstance(value, str) else round(float(value), 4), note=note))

Lz = L[L.cohort == "zou"]; y = Lz.y.values; ld = np.log10(Lz.depth.values)
Xz = raws["zou"].loc[Lz.index]
add("depth AUC (processed reads, ASD positive)", AUC(y, Lz.depth), "median ASD %d vs control %d" % (Lz.depth[y == 1].median(), Lz.depth[y == 0].median()))
# 1. sequencing / submission metadata from ENA
ena = pd.read_csv(os.path.join(a.ena, "PRJNA578223.tsv"), sep="\t").set_index("run_accession")
j = Lz.join(ena, how="inner"); yj = j.y.values
add("ENA runs matched to labels", len(j), "of %d labelled samples" % len(Lz))
add("ENA instrument/layout", "; ".join(f"{k} x{v}" for k, v in (j.instrument_model + " " + j.library_layout).value_counts().items()),
    "mean bases per spot %.0f -> 2x300 MiSeq, consistent with V3-V4; region itself is not recorded in ENA" % (j.base_count / j.read_count).mean())
add("raw ENA read count AUC", AUC(yj, j.read_count))
add("fraction of raw reads retained after processing AUC", AUC(yj, j.depth / j.read_count),
    "median retained ASD %.3f vs control %.3f" % ((j.depth / j.read_count)[yj == 1].median(), (j.depth / j.read_count)[yj == 0].median()))
acc = j.index.str[3:].astype(int)
add("run accession number AUC (submission order)", AUC(yj, acc), "cases and controls were submitted as near-separate blocks; library names 'case..'/'control..'")
# 2. unassigned reads
un = np.array([key_of(c, "famgenus") is None for c in Xz.columns])
uf = Xz.loc[:, un].sum(1) / Xz.sum(1)
add("unassigned-at-genus read fraction AUC", AUC(y, uf), "median ASD %.3f vs control %.3f" % (uf[y == 1].median(), uf[y == 0].median()))
# 3. overlap with the V4 cohorts: fraction of Zou reads in keys that are >=10% prevalent in Ding and David
for mode in ("famgenus", "genus"):
    R, _ = harmonise(raws, mode)
    prev_other = pd.concat([(R[L.cohort == c] > 0).mean() for c in ("ding", "david")], axis=1).min(1)
    shared = prev_other[prev_other >= PREV].index
    Rz = R.loc[Lz.index]
    sf = Rz[shared].sum(1) / Rz.sum(1)
    add(f"[{mode}] fraction of Zou genus-assigned reads in keys shared with Ding+David AUC", AUC(y, sf),
        "median ASD %.3f vs control %.3f; %d shared keys" % (sf[y == 1].median(), sf[y == 0].median(), len(shared)))
# 4. label-free PCA inside Zou
R, _ = harmonise(raws, "famgenus")
Rz = R.loc[Lz.index]
v = Rz.columns[(Rz > 0).mean() >= PREV]
A = np.log(Rz[v].values + PSEUDO); A = A - A.mean(1, keepdims=True); A = A - A.mean(0)
U, S, Vt = np.linalg.svd(A, full_matrices=False)
ve = S ** 2 / (S ** 2).sum()
for k in range(5):
    pc = U[:, k] * S[k]
    au = AUC(y, pc)
    add(f"Zou PC{k+1} (label-free) AUC; |AUC-0.5|", au, "var expl %.3f; |AUC-0.5|=%.3f; Spearman with log depth %.3f" % (ve[k], abs(au - 0.5), spearmanr(pc, ld).statistic))
# rarefied PCA
Rr, _ = harmonise(raws, "famgenus", RAREFY_DEPTH)
Rzr = Rr.loc[Lz.index]
B = np.log(Rzr[v].values + PSEUDO); B = B - B.mean(1, keepdims=True); B = B - B.mean(0)
U2, S2, _ = np.linalg.svd(B, full_matrices=False)
au = AUC(y, U2[:, 0]); add("Zou PC1 after rarefying to 5000 reads AUC", au, "|AUC-0.5|=%.3f; Spearman with log raw depth %.3f" % (abs(au - .5), spearmanr(U2[:, 0], ld).statistic))
# 5. per-genus: ASD effect vs depth sensitivity estimated in controls only
C = np.log(Rz[v].values + PSEUDO); C = C - C.mean(1, keepdims=True)
eff = np.array([AUC(y, C[:, i]) - 0.5 for i in range(C.shape[1])])
ctl = y == 0
dsens = np.array([spearmanr(C[ctl, i], ld[ctl]).statistic for i in range(C.shape[1])])
r = spearmanr(eff, dsens, nan_policy="omit").statistic
add("across genera: Spearman(ASD effect, depth correlation within controls)", r,
    "%d genera; if ASD-vs-control differences were a pure depth artefact this would be strongly positive (ASD has lower depth -> expect negative)" % len(v))
# same for prevalence (detection) which depends on depth
eff_p = np.array([(Rz[g][y == 1] > 0).mean() - (Rz[g][y == 0] > 0).mean() for g in v])
add("genera detected more often in controls than ASD (count / total)", "%d / %d" % ((eff_p < 0).sum(), len(v)),
    "lower-depth group (ASD) is expected to detect fewer rare genera")
rich = (Rz > 0).sum(1); richr = (Rzr > 0).sum(1)
add("observed genera AUC (raw)", AUC(y, rich)); add("observed genera AUC (rarefied 5000)", AUC(y, richr))
# 6. distance to the training (Ding+David) centroid: label-free
for mode in ("famgenus", "genus"):
    R, _ = harmonise(raws, mode)
    tr = L.cohort != "zou"
    prev = pd.concat([(R[L.cohort == c] > 0).mean() for c in ("ding", "david")], axis=1).min(1)
    vv = prev[prev >= PREV].index
    Z = np.log(R[vv].values + PSEUDO); Z = Z - Z.mean(1, keepdims=True)
    cen = Z[tr.values].mean(0)
    dist = np.sqrt(((Z[~tr.values] - cen) ** 2).sum(1))
    add(f"[{mode}] Aitchison distance of Zou samples to Ding+David centroid: AUC", AUC(y, dist),
        "label-free 'how unlike training' score; Spearman with log depth %.3f" % spearmanr(dist, ld).statistic)
# 7. LOCO Zou scores vs depth, from the main run
oof = pd.read_csv(os.path.join(a.loco, "oof_scores.csv"), dtype={"sample_id": str})
oz = oof[oof.cohort == "zou"]
for (var, feat), g in oz.groupby(["variant", "features"]):
    if feat in ("depth_only", "richness_only"):
        continue
    g = g.set_index("sample_id").loc[Lz.index]
    s = g.score.values
    # residualise score on log depth (fitted on Zou, label-free) and recompute AUC
    b = np.polyfit(ld, s, 1); res = s - np.polyval(b, ld)
    add(f"LOCO Zou {var}/{feat}: AUC | Spearman(score, log depth) | AUC of depth-residualised score",
        AUC(y, s), "rho=%.3f; residual AUC=%.3f" % (spearmanr(s, ld).statistic, AUC(y, res)))
# 8. null width
lr = pd.read_csv(os.path.join(a.loco, "loco_results.csv"))
for _, r_ in lr[(lr.test_cohort == "zou")].iterrows():
    add(f"LOCO Zou null 95% range {r_.variant}/{r_.features}", r_.auc, "null %.3f-%.3f, p=%.3f" % (r_.null_q025, r_.null_q975, r_.perm_p))
out = pd.DataFrame(rows); out.to_csv(os.path.join(a.out, "zou_diagnostics.csv"), index=False)
pd.set_option("display.max_colwidth", 200); pd.set_option("display.width", 250)
print(out.to_string())
