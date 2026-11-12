"""Claude, round 1: leave-one-cohort-out ASD vs control on the benchmark's training cohorts.

One command reproduces loco_results.csv:
    python -I run.py --data F:/masters/ai_benchmark/data --out ..

Design (all fixed before running):
- Genus key = "family|genus" from the SILVA lineage; columns without a genus name (unassigned at genus) are dropped.
- Frozen vocabulary: genera present in >= 10 % of TRAINING samples. A vocabulary genus absent from the test table = 0 counts.
- CLR per sample on the frozen vocabulary (pseudocount 0.5).
- Logistic regression (L2, class-balanced). C chosen from {0.01, 0.1, 1} by inner leave-one-training-cohort-out AUC.
- Network features use the training reference only (a test child is never added to a graph):
  cosine similarity to the ASD and control centroids (leave-self-out for training samples), their difference,
  class-balanced fraction of ASD among the 10 nearest training samples, and 10 taxon-module scores from
  average-linkage clustering of training-sample taxon correlations (no labels).
- Models: abund | net | comb, identical splits. AUC with 2,000-sample bootstrap 95 % interval.
- Label-permutation null: 100 permutations of training labels within each training cohort, C fixed at the value
  chosen on the real labels (to keep run time reasonable); one-sided p.
- Metadata baseline: only David has sex/age, and no other cohort does, so a cross-cohort metadata model is impossible.
  Reported instead inside David with 5-fold cross-validation that keeps sibling pairs together (5 repeats).
- Random seed 0 throughout. No holdout file exists in round 1, so no predictions.csv.
"""
import argparse, os, re
import numpy as np, pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.metrics import roc_auc_score

CGRID, K, MODULES, PREV = [0.01, 0.1, 1.0], 10, 10, 0.10
COHORTS = ["ding", "zou", "david"]


def key(col):
    m = re.search(r"f__([^;]*);\s*g__([^;]*)$", col)
    return f"{m.group(1)}|{m.group(2)}" if m and m.group(2).strip() else None


def load(data, name):
    X = pd.read_csv(os.path.join(data, "train", name, "genus_counts.tsv"), sep="\t", index_col=0, dtype={0: str})
    L = pd.read_csv(os.path.join(data, "train", name, "labels.tsv"), sep="\t", dtype={"sample_id": str}).set_index("sample_id").loc[X.index]
    k = {c: key(c) for c in X.columns}
    X = X[[c for c in X.columns if k[c]]].rename(columns=k).T.groupby(level=0).sum().T
    return dict(name=name, X=X, y=(L["diagnosis"] == "ASD").astype(int).values, L=L)


def vocab(train):
    allx = pd.concat([c["X"] for c in train]).fillna(0)
    prev = (allx > 0).mean()
    return list(prev[prev >= PREV].index)


def clr(X, voc):
    Z = np.log(X.reindex(columns=voc, fill_value=0).fillna(0).values + 0.5)
    return Z - Z.mean(1, keepdims=True)


def unit(F):
    return F / (np.linalg.norm(F, axis=1, keepdims=True) + 1e-9)


def reference(F, y):
    C = np.nan_to_num(np.corrcoef(F.T)); D = 1 - np.abs(C); np.fill_diagonal(D, 0)
    mod = fcluster(linkage(squareform(D, checks=False), "average"), MODULES, "maxclust")
    return dict(U=unit(F), y=y, mod=mod, mu=F.mean(0), sd=F.std(0) + 1e-6, sA=F[y == 1].sum(0), sC=F[y == 0].sum(0),
                nA=int((y == 1).sum()), nC=int((y == 0).sum()))


def netfeats(r, Fq, train):
    n = len(Fq)
    A, Cc = np.tile(r["sA"], (n, 1)), np.tile(r["sC"], (n, 1))
    nA, nC = np.full(n, r["nA"], float), np.full(n, r["nC"], float)
    if train:
        y = r["y"]; A = A - Fq * (y == 1)[:, None]; Cc = Cc - Fq * (y == 0)[:, None]; nA = nA - (y == 1); nC = nC - (y == 0)
    Uq = unit(Fq)
    sa = np.einsum("ij,ij->i", Uq, unit(A / nA[:, None])); sc = np.einsum("ij,ij->i", Uq, unit(Cc / nC[:, None]))
    S = Uq @ r["U"].T
    if train:
        np.fill_diagonal(S, -np.inf)
    yk = r["y"][np.argpartition(-S, K, axis=1)[:, :K]]
    wa, wc = (yk == 1).sum(1) / max(r["nA"], 1), (yk == 0).sum(1) / max(r["nC"], 1)
    Z = (Fq - r["mu"]) / r["sd"]
    mods = np.column_stack([Z[:, r["mod"] == m].mean(1) for m in sorted(set(r["mod"]))])
    return np.column_stack([sa, sc, sa - sc, wa / (wa + wc + 1e-9), mods])


def feats(kind, Ftr, ytr, Fq, train):
    if kind == "abund":
        return Fq
    N = netfeats(reference(Ftr, ytr), Fq, train)
    return N if kind == "net" else np.hstack([Fq, N])


def model(C):
    return make_pipeline(StandardScaler(), LogisticRegression(C=C, class_weight="balanced", max_iter=5000))


def fit_score(kind, Ftr, ytr, ctr, Fte, C=None):
    if C is None:
        best, bs = 0.1, -1
        for c in CGRID:
            a = []
            for k in sorted(set(ctr)):
                m = ctr != k
                if len(set(ytr[m])) == 2 and len(set(ytr[~m])) == 2:
                    Xa, Xb = feats(kind, Ftr[m], ytr[m], Ftr[m], True), feats(kind, Ftr[m], ytr[m], Ftr[~m], False)
                    a.append(roc_auc_score(ytr[~m], model(c).fit(Xa, ytr[m]).predict_proba(Xb)[:, 1]))
            if a and np.mean(a) > bs:
                best, bs = c, np.mean(a)
        C = best
    Xa, Xb = feats(kind, Ftr, ytr, Ftr, True), feats(kind, Ftr, ytr, Fte, False)
    return model(C).fit(Xa, ytr).predict_proba(Xb)[:, 1], C


def boot_ci(y, s, rng, B=2000):
    b = []
    for _ in range(B):
        i = rng.integers(0, len(y), len(y))
        if len(set(y[i])) == 2:
            b.append(roc_auc_score(y[i], s[i]))
    return np.percentile(b, [2.5, 97.5])


def grouped_cv(F, y, groups, reps=5):
    a = []
    for r in range(reps):
        u = np.unique(groups); mp = dict(zip(u, np.random.default_rng(r).permutation(len(u))))
        g = np.array([mp[i] for i in groups])
        p = cross_val_predict(make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)), F, y, groups=g,
                              cv=GroupKFold(5), method="predict_proba")[:, 1]
        a.append(roc_auc_score(y, p))
    return float(np.mean(a)), float(np.std(a))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=r"F:\masters\ai_benchmark\data")
    ap.add_argument("--out", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--perms", type=int, default=100)
    a = ap.parse_args()
    rng = np.random.default_rng(0)
    cohorts = [load(a.data, n) for n in COHORTS]
    rows = []
    for held in cohorts:
        train = [c for c in cohorts if c is not held]
        voc = vocab(train)
        Ftr = np.vstack([clr(c["X"], voc) for c in train]); ytr = np.concatenate([c["y"] for c in train])
        ctr = np.concatenate([[c["name"]] * len(c["y"]) for c in train])
        Fte, yte = clr(held["X"], voc), held["y"]
        scores = {}
        for kind in ("abund", "net", "comb"):
            s, C = fit_score(kind, Ftr, ytr, ctr, Fte)
            scores[kind] = s
            auc = roc_auc_score(yte, s); lo, hi = boot_ci(yte, s, rng)
            null = []
            for _ in range(a.perms):
                yp = ytr.copy()
                for k in set(ctr):
                    m = ctr == k; yp[m] = rng.permutation(ytr[m])
                null.append(roc_auc_score(yte, fit_score(kind, Ftr, yp, ctr, Fte, C=C)[0]))
            p = (1 + sum(n >= auc for n in null)) / (1 + len(null))
            rows.append(dict(split="leave-one-cohort-out", heldout=held["name"], model=kind, n_train=len(ytr), n_test=len(yte),
                             n_asd_test=int(yte.sum()), n_features=len(voc), C=C, auc=round(auc, 3), ci95_lo=round(lo, 3),
                             ci95_hi=round(hi, 3), perm_null_mean=round(float(np.mean(null)), 3), perm_p=round(p, 3)))
            print(rows[-1], flush=True)
        pd.DataFrame({"sample_id": held["X"].index, "y": yte, **scores}).to_csv(
            os.path.join(a.out, f"oof_scores_{held['name']}.csv"), index=False)
    d = next(c for c in cohorts if c["name"] == "david")
    voc = vocab([d]); Z = clr(d["X"], voc)
    sex = (d["L"]["sex"].astype(str).str.lower().str[0] == "m").astype(float).values
    age = pd.to_numeric(d["L"]["age"], errors="coerce"); age = age.fillna(age.median()).values
    M = np.column_stack([sex, age]); g = d["L"]["sibling_pair"].astype(str).values
    for name, F in [("metadata_only_sex_age", M), ("microbiome_only", Z), ("microbiome_plus_metadata", np.hstack([Z, M]))]:
        m, s = grouped_cv(F, d["y"], g)
        rows.append(dict(split="within-david 5-fold CV, sibling pairs grouped, 5 repeats", heldout="david(within)", model=name,
                         n_test=len(d["y"]), n_asd_test=int(d["y"].sum()), n_features=F.shape[1], auc=round(m, 3),
                         note=f"sd over repeats {s:.3f}"))
        print(rows[-1], flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(a.out, "loco_results.csv"), index=False)
    print("wrote", os.path.join(a.out, "loco_results.csv"))


if __name__ == "__main__":
    main()
