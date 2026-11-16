"""Claude, round 2. One command:  python -I run2.py --data <repo>/data --out .. [--perms 200]
Headline (locked in HEADLINE_LOCKED.md): abundance CLR logistic regression on profiles rarefied to 5,000 reads,
family|genus key, leave-one-cohort-out, full-pipeline permutation null, Holm across the 3 held-out cohorts.
Everything learned is fitted on training cohorts only. No holdout file exists, so no predictions.csv."""
import argparse, os, re
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.metrics import roc_auc_score

CGRID, K, MODULES, PREV, RARE, SEED = [0.001, 0.01, 0.1, 1.0], 10, 10, 0.10, 5000, 0
COHORTS = ["ding", "zou", "david"]


def key(col, mode):
    m = re.search(r"f__([^;]*);\s*g__([^;]*)$", col)
    if not (m and m.group(2).strip()):
        return None
    return f"{m.group(1)}|{m.group(2)}" if mode == "famgen" else m.group(2).strip()


def load(data, name, mode, rarefy):
    X = pd.read_csv(os.path.join(data, "train", name, "genus_counts.tsv"), sep="\t", index_col=0, dtype={0: str})
    L = pd.read_csv(os.path.join(data, "train", name, "labels.tsv"), sep="\t", dtype={"sample_id": str}).set_index("sample_id").loc[X.index]
    depth = X.sum(1).values
    k = {c: key(c, mode) for c in X.columns}
    G = X[[c for c in X.columns if k[c]]].rename(columns=k).T.groupby(level=0).sum().T
    if rarefy:
        rng = np.random.default_rng(SEED)
        V = G.values.astype(np.int64)
        R = np.vstack([rng.multivariate_hypergeometric(v, RARE) if v.sum() >= RARE else v for v in V])
        G = pd.DataFrame(R, index=G.index, columns=G.columns)
    grp = L["sibling_pair"].astype(str).values if "sibling_pair" in L else np.array(X.index)
    grp = np.array([f"{name}_{g}" if g not in ("nan", "") else f"{name}_{i}" for g, i in zip(grp, X.index)])
    return dict(name=name, X=G, y=(L["diagnosis"] == "ASD").astype(int).values, L=L, grp=grp,
                logdepth=np.log10(depth), richness=(G > 0).sum(1).values.astype(float))


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


def choose_c(kind, Ftr, ytr, ctr):
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
    return best


def score(kind, Ftr, ytr, Fte, C):
    return model(C).fit(feats(kind, Ftr, ytr, Ftr, True), ytr).predict_proba(feats(kind, Ftr, ytr, Fte, False))[:, 1]


def cluster_ci(y, s, g, rng, B=2000):
    u = np.unique(g); idx = {k: np.flatnonzero(g == k) for k in u}; b = []
    for _ in range(B):
        i = np.concatenate([idx[k] for k in rng.choice(u, len(u))])
        if len(set(y[i])) == 2:
            b.append(roc_auc_score(y[i], s[i]))
    return np.percentile(b, [2.5, 97.5])


def perm_once(kind, Ftr, ytr, ctr, Fte, yte, seed):
    rng = np.random.default_rng(seed); yp = ytr.copy()
    for k in set(ctr):
        m = ctr == k; yp[m] = rng.permutation(ytr[m])
    return roc_auc_score(yte, score(kind, Ftr, yp, Fte, choose_c(kind, Ftr, yp, ctr)))


def holm(p):
    p = np.asarray(p, float); o = np.argsort(p); adj = np.empty_like(p); run = 0
    for r, i in enumerate(o):
        run = max(run, (len(p) - r) * p[i]); adj[i] = min(1, run)
    return adj


def loco(cohorts, kinds, perms, rng, tag, out_scores=None):
    rows = []
    for held in cohorts:
        train = [c for c in cohorts if c is not held]
        voc = vocab(train)
        Ftr = np.vstack([clr(c["X"], voc) for c in train]); ytr = np.concatenate([c["y"] for c in train])
        ctr = np.concatenate([[c["name"]] * len(c["y"]) for c in train]); Fte, yte = clr(held["X"], voc), held["y"]
        for kind in kinds:
            C = choose_c(kind, Ftr, ytr, ctr); s = score(kind, Ftr, ytr, Fte, C)
            auc = roc_auc_score(yte, s); lo, hi = cluster_ci(yte, s, held["grp"], rng)
            byC = {f"auc_C{c}": round(roc_auc_score(yte, score(kind, Ftr, ytr, Fte, c)), 3) for c in CGRID}
            row = dict(analysis=tag, heldout=held["name"], model=kind, n_test=len(yte), n_features=len(voc), C=C,
                       auc=round(auc, 3), ci95_lo=round(lo, 3), ci95_hi=round(hi, 3), **byC)
            if perms:
                null = np.array(Parallel(n_jobs=-1)(delayed(perm_once)(kind, Ftr, ytr, ctr, Fte, yte, 1000 * i + 7) for i in range(perms)))
                row.update(perm_null_mean=round(null.mean(), 3), perm_null_q975=round(np.quantile(null, .975), 3),
                           perm_p=round((1 + (null >= auc).sum()) / (1 + perms), 4))
            if held["name"] == "david" and out_scores is not None:
                out_scores[(tag, kind)] = s
            rows.append(row); print(row, flush=True)
    return rows


def baselines(cohorts, rng):
    rows = []
    for held in cohorts:
        train = [c for c in cohorts if c is not held]
        for name, fld in (("depth_only", "logdepth"), ("richness_only", "richness")):
            xtr = np.concatenate([c[fld] for c in train])[:, None]; ytr = np.concatenate([c["y"] for c in train])
            s = model(1.0).fit(xtr, ytr).predict_proba(held[fld][:, None])[:, 1]
            auc = roc_auc_score(held["y"], s); lo, hi = cluster_ci(held["y"], s, held["grp"], rng)
            within = roc_auc_score(held["y"], held[fld])
            rows.append(dict(analysis="technical_baseline_loco", heldout=held["name"], model=name, n_test=len(held["y"]),
                             auc=round(auc, 3), ci95_lo=round(lo, 3), ci95_hi=round(hi, 3),
                             note=f"label-vs-{fld} AUC inside this cohort {within:.3f} (0.5 = no association)"))
            print(rows[-1], flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=r"F:\masters\ai_benchmark\data")
    ap.add_argument("--out", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--perms", type=int, default=200)
    a = ap.parse_args(); rng = np.random.default_rng(SEED); rows = []; dscores = {}
    main_c = [load(a.data, n, "famgen", True) for n in COHORTS]
    r = loco(main_c, ["abund", "net", "comb"], a.perms, rng, "LOCO_rarefied5000_famgen", dscores)
    adj = holm([x["perm_p"] for x in r if x["model"] == "abund"])
    for x, p in zip([x for x in r if x["model"] == "abund"], adj):
        x["perm_p_holm_3cohorts"] = round(p, 4); x["headline"] = True
    allp = holm([x["perm_p"] for x in r])
    for x, p in zip(r, allp):
        x["perm_p_holm_all9"] = round(p, 4)
    rows += r
    rows += loco([load(a.data, n, "famgen", False) for n in COHORTS], ["abund", "net", "comb"], 0, rng, "LOCO_unrarefied_famgen")
    rows += loco([load(a.data, n, "genus", True) for n in COHORTS], ["abund"], 0, rng, "LOCO_rarefied5000_genusonly")
    rows += baselines([load(a.data, n, "famgen", False) for n in COHORTS], rng)
    d = next(c for c in main_c if c["name"] == "david"); L = d["L"]
    for (tag, kind), s in dscores.items():
        conc = []
        for _, g in pd.DataFrame({"p": L["sibling_pair"].values, "y": d["y"], "s": s}).groupby("p"):
            if g.y.nunique() == 2:
                conc.append(np.mean([u > v for u in g.s[g.y == 1] for v in g.s[g.y == 0]]))
        rows.append(dict(analysis="david_sibling_pair_concordance", heldout="david", model=kind, n_test=len(conc),
                         auc=round(float(np.mean(conc)), 3), note=f"{tag}; fraction of discordant pairs where the ASD child scores higher"))
        print(rows[-1], flush=True)
    sex = L["sex"].astype(str).str.lower(); ok = sex.isin(["m", "f"]).values & pd.to_numeric(L["age"], errors="coerce").notna().values
    M = np.column_stack([(sex == "m").astype(float).values, pd.to_numeric(L["age"], errors="coerce").values])[ok]
    voc = vocab([d]); Z = clr(d["X"], voc)[ok]; y = d["y"][ok]; g = L["sibling_pair"].astype(str).values[ok]
    for name, F in (("metadata_only_sex_age", M), ("microbiome_only", Z), ("microbiome_plus_metadata", np.hstack([Z, M]))):
        aucs = []
        for r_ in range(5):
            u = np.unique(g); mp = dict(zip(u, np.random.default_rng(r_).permutation(len(u)))); gg = np.array([mp[i] for i in g])
            p = cross_val_predict(model(0.1), F, y, groups=gg, cv=GroupKFold(5), method="predict_proba")[:, 1]
            aucs.append(roc_auc_score(y, p))
        rows.append(dict(analysis="within_david_complete_cases_sibling_grouped_5fold_x5", heldout="david", model=name, n_test=int(ok.sum()),
                         auc=round(float(np.mean(aucs)), 3), note=f"sd {np.std(aucs):.3f}; excludes {int((~ok).sum())} rows missing sex or age; sex coding of controls disputed (round 1 feedback)"))
        print(rows[-1], flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(a.out, "loco_results.csv"), index=False)
    print("wrote loco_results.csv")


if __name__ == "__main__":
    main()
