"""Track A, round 1 (Perplexity). One command:  python code/run_all.py --data <repo>/data
Writes loco_results.csv, harmonisation_log.csv and (if holdout exists) predictions.csv to the current dir."""
import argparse, os, re, json
import numpy as np, pandas as pd, networkx as nx
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from joblib import Parallel, delayed

SEED = 20261112
COHORTS = ["ding", "zou", "david"]
AMBIG = re.compile(r"^(uncultured|unidentified|metagenome|gut_metagenome|human_gut_metagenome|incertae_sedis|.*_bacterium)$")
PSEUDO = 1e-5          # pseudo-proportion for log transform
PREV = 0.10            # min prevalence required in EVERY training cohort
N_PERM = 200
N_BOOT = 2000

def genus_key(col):
    f = col.split(";")
    last = f[-1].strip()
    if not last.startswith("g__") or last == "g__":
        return None                       # unassigned above genus
    g = last[3:].strip().lower().replace(" ", "_")
    g = g.replace("[", "").replace("]", "")
    if AMBIG.match(g):                    # ambiguous name: qualify by family
        fam = [x for x in f if x.strip().startswith("f__")]
        g = (fam[-1].strip()[3:].lower() if fam else "nofam") + "|" + g
    return g

def load(datadir, c, holdout=False):
    p = os.path.join(datadir, "holdout" if holdout else f"train/{c}", "genus_counts.tsv")
    X = pd.read_csv(p, sep="\t", index_col=0, dtype={0: str})
    X.index = X.index.astype(str)
    total = X.sum(axis=1)                 # depth INCLUDING unassigned reads
    keys = [genus_key(k) for k in X.columns]
    keep = [k is not None for k in keys]
    G = X.loc[:, keep].T.groupby([k for k in keys if k is not None]).sum().T
    rel = G.div(total, axis=0)            # proportion of all reads; unassigned kept in denominator, not renormalised
    log = {"cohort": c, "n_samples": len(X), "raw_columns": X.shape[1],
           "unassigned_columns_dropped": int((~np.array(keep)).sum()),
           "unassigned_read_fraction": float(X.loc[:, ~np.array(keep)].values.sum() / X.values.sum()),
           "harmonised_genera": G.shape[1]}
    if holdout:
        return rel, None, log
    L = pd.read_csv(os.path.join(datadir, f"train/{c}/labels.tsv"), sep="\t", dtype={"sample_id": str}).set_index("sample_id")
    L = L.loc[rel.index]
    L["y"] = (L["diagnosis"] == "ASD").astype(int)
    L["cohort"] = c
    L["log_depth"] = np.log10(total.loc[L.index].values)
    if "sibling_pair" not in L: L["sibling_pair"] = np.nan
    L["group"] = [f"{c}_pair{int(p)}" if pd.notna(p) else f"{c}_{i}" for i, p in zip(L.index, L["sibling_pair"])]
    return rel, L, log

# ---------------- feature construction (fitted on training rows only) ----------------
class Featuriser:
    def __init__(self, cohort_std=False, net_thr=0.3):
        self.cohort_std, self.net_thr = cohort_std, net_thr
    def _logab(self, R):
        return np.log10(R.reindex(columns=self.genera, fill_value=0.0) + PSEUDO)
    def fit(self, R, L):
        prev = [(R[L.cohort == c] > 0).mean() for c in L.cohort.unique()]
        prev = pd.concat(prev, axis=1).fillna(0).min(axis=1)
        self.genera = list(prev[prev >= PREV].index)
        A = self._logab(R)
        A = self._std(A, L.cohort, fit=True)
        # co-occurrence network on TRAINING samples: mean within-cohort Spearman (avoids batch-driven edges)
        rhos = []
        for c in L.cohort.unique():
            r = spearmanr(A[L.cohort == c].values).statistic
            rhos.append(np.nan_to_num(r))
        rho = np.mean(rhos, axis=0); np.fill_diagonal(rho, 0)
        self.rho = rho
        Gx = nx.Graph(); Gx.add_nodes_from(range(len(self.genera)))
        ii, jj = np.where(np.triu(np.abs(rho) >= self.net_thr, 1))
        for i, j in zip(ii, jj): Gx.add_edge(i, j, weight=abs(rho[i, j]))
        comms = nx.community.louvain_communities(Gx, weight="weight", seed=SEED)
        self.modules = [sorted(m) for m in comms if len(m) >= 3]
        self.deg = np.array([Gx.degree(i, weight="weight") for i in range(len(self.genera))])
        self.hubs = np.argsort(-self.deg)[:max(5, len(self.genera) // 10)]
        # module sign: align members to the module's first principal direction (training only)
        self.signs = []
        for m in self.modules:
            sub = A.values[:, m]
            u, s, vt = np.linalg.svd(sub - sub.mean(0), full_matrices=False)
            self.signs.append(np.sign(vt[0]) + (vt[0] == 0))
        return self
    def _std(self, A, cohort, fit=False):
        if self.cohort_std:   # unsupervised per-cohort centering/scaling (uses test-cohort FEATURES, never labels)
            out = A.copy()
            for c in pd.unique(cohort):
                m = (cohort == c).values
                mu, sd = A[m].mean(), A[m].std().replace(0, 1).fillna(1)
                out[m] = (A[m] - mu) / sd
            return out
        if fit:
            self.mu, self.sd = A.mean(), A.std().replace(0, 1).fillna(1)
        return (A - self.mu) / self.sd
    def transform(self, R, cohort, kind):
        A = self._std(self._logab(R), cohort)
        if kind == "abundance": return A.values
        V = A.values
        mod = np.column_stack([(V[:, m] * s).mean(1) for m, s in zip(self.modules, self.signs)]) if self.modules else np.zeros((len(V), 0))
        # per-sample network summaries vs the TRAINING reference network
        pres = (R.reindex(columns=self.genera, fill_value=0).values > 0).astype(float)
        hub_pres = pres[:, self.hubs].mean(1, keepdims=True)
        wdeg = (pres * self.deg).sum(1, keepdims=True) / (self.deg.sum() + 1e-9)
        # coherence: how well the sample's profile agrees with the training correlation structure
        coh = np.einsum("ij,jk,ik->i", V, self.rho, V)[:, None] / (V.shape[1] ** 2)
        N = np.hstack([mod, hub_pres, wdeg, coh])
        if kind == "network": return N
        return np.hstack([V, N])

def make_model(name, C=None):
    if name == "logreg":  # L2-penalised
        return LogisticRegression(C=C, l1_ratio=0, solver="lbfgs", max_iter=5000)
    return RandomForestClassifier(n_estimators=500, min_samples_leaf=3, max_features="sqrt",
                                  class_weight="balanced", random_state=SEED, n_jobs=1)

C_GRID = [0.001, 0.01, 0.1, 1.0]

def fit_predict(R, L, tr, te, kind, model, cohort_std, y=None):
    y = L.y.values if y is None else y
    if kind == "depth_only":   # trivial batch/technical baseline: log10 total reads
        d = L.log_depth.values[:, None]; mu, sd = d[tr].mean(), d[tr].std()
        m = make_model("logreg", 1.0).fit((d[tr] - mu) / sd, y[tr])
        return m.predict_proba((d[te] - mu) / sd)[:, 1], 1.0
    Ltr = L[tr]
    F = Featuriser(cohort_std).fit(R[tr], Ltr)
    Xtr = F.transform(R[tr], Ltr.cohort, kind); Xte = F.transform(R[te], L[te].cohort, kind)
    C = None
    if model == "logreg":
        # inner leave-one-training-cohort-out to pick C (uses training labels only)
        best = (-1, C_GRID[0])
        tcs = Ltr.cohort.unique()
        for Cc in C_GRID:
            aucs = []
            for ic in tcs:
                itr = (Ltr.cohort != ic).values
                Fi = Featuriser(cohort_std).fit(R[tr][itr], Ltr[itr])
                a = Fi.transform(R[tr][itr], Ltr[itr].cohort, kind); b = Fi.transform(R[tr][~itr], Ltr[~itr].cohort, kind)
                m = make_model("logreg", Cc).fit(a, y[tr][itr])
                aucs.append(roc_auc_score(y[tr][~itr], m.predict_proba(b)[:, 1]))
            if np.mean(aucs) > best[0]: best = (np.mean(aucs), Cc)
        C = best[1]
    m = make_model(model, C).fit(Xtr, y[tr])
    return m.predict_proba(Xte)[:, 1], C

def _perm_one(R, L, tr, te, kind, yp):
    s, _ = fit_predict(R, L, tr, te, kind, "logreg", False, y=yp)
    return roc_auc_score(L.y.values[te], s)

def boot_ci(y, s, groups, rng):
    ug = pd.unique(groups); idx = {g: np.where(groups == g)[0] for g in ug}; out = []
    for _ in range(N_BOOT):
        bi = np.concatenate([idx[g] for g in rng.choice(ug, len(ug))])
        if len(set(y[bi])) < 2: continue
        out.append(roc_auc_score(y[bi], s[bi]))
    return np.percentile(out, [2.5, 97.5])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", default="data"); ap.add_argument("--perm", type=int, default=N_PERM)
    a = ap.parse_args(); rng = np.random.default_rng(SEED)
    Rs, Ls, logs = [], [], []
    for c in COHORTS:
        r, l, lg = load(a.data, c); Rs.append(r); Ls.append(l); logs.append(lg)
    R = pd.concat(Rs).fillna(0.0); L = pd.concat(Ls)
    shared = set.intersection(*[set(r.columns) for r in Rs])
    for lg in logs: lg["genera_shared_by_all_3"] = len(shared)
    pd.DataFrame(logs).to_csv("harmonisation_log.csv", index=False)
    y = L.y.values; groups = L.group.values
    rows = []
    configs = [("depth_only", "logreg", False)] + [(k, m, cs) for cs in (False, True) for m in ("logreg", "rf") for k in ("abundance", "network", "combined")]
    for kind, model, cs in configs:
        for c in COHORTS:
            te = (L.cohort == c).values; tr = ~te
            s, C = fit_predict(R, L, tr, te, kind, model, cs)
            auc = roc_auc_score(y[te], s); lo, hi = boot_ci(y[te], s, groups[te], rng)
            rows.append(dict(analysis="LOCO", test_cohort=c, features=kind, model=model,
                             per_cohort_std=cs, n_test=int(te.sum()), n_asd=int(y[te].sum()),
                             auc=round(auc, 3), ci_low=round(lo, 3), ci_high=round(hi, 3),
                             chosen_C=C, perm_p=None, perm_null_mean=None, perm_null_95=None, sibling_pair_concordance=None))
            if c == "david":   # within discordant sibling pairs: fraction where the ASD child scores higher
                D = L[te].assign(s=s); conc = []
                for _, g in D.groupby("sibling_pair"):
                    if g.y.nunique() == 2:
                        conc.append(np.mean([a > b for a in g.s[g.y == 1] for b in g.s[g.y == 0]]))
                rows[-1]["sibling_pair_concordance"] = round(float(np.mean(conc)), 3)
                rows[-1]["n_discordant_pairs"] = len(conc)
            print(rows[-1], flush=True)
    # label-permutation null for the pre-specified primary configuration and combined (logreg, global std)
    for kind in ("abundance", "network", "combined"):
        for c in COHORTS:
            te = (L.cohort == c).values; tr = ~te
            obs = [r for r in rows if r["test_cohort"] == c and r["features"] == kind and r["model"] == "logreg" and not r["per_cohort_std"]][0]
            perms = []
            for p in range(a.perm):
                yp = y.copy()
                for cc in COHORTS:   # permute training labels within each cohort (keeps cohort prevalence)
                    m = (L.cohort == cc).values; yp[m] = rng.permutation(yp[m])
                perms.append(yp)
            # full pipeline (feature filter, network, inner C selection) refitted on permuted TRAINING labels,
            # scored against the TRUE labels of the held-out cohort
            null = np.array(Parallel(n_jobs=-1)(delayed(_perm_one)(R, L, tr, te, kind, yp) for yp in perms))
            obs["perm_p"] = round((1 + (null >= obs["auc"]).sum()) / (1 + len(null)), 3)
            obs["perm_null_mean"] = round(null.mean(), 3); obs["perm_null_95"] = round(np.percentile(null, 95), 3)
            print(c, kind, obs["auc"], obs["perm_p"], flush=True)
    # metadata-only baseline: only David has sex/age -> within-David sibling-grouped CV (NOT cross-cohort)
    # complete cases only: in labels.tsv sex is missing for 8 controls (and age for some children); encoding
    # missingness would leak the label (missing sex occurs only in controls), so those children are excluded here.
    D = L[L.cohort == "david"].copy()
    D = D[D.sex.astype(str).str.lower().isin(["m", "f"]) & D.age.notna()]
    RD = R.loc[D.index]
    meta = np.column_stack([(D.sex.str.lower() == "m").astype(float), D.age.astype(float)])
    gkf = GroupKFold(n_splits=5)
    for name in ("metadata_only", "abundance", "abundance+metadata"):
        s = np.zeros(len(D))
        for tri, tei in gkf.split(D, D.y, D.group):
            Ltr = D.iloc[tri]
            F = Featuriser(False).fit(RD.iloc[tri], Ltr)
            ab_tr = F.transform(RD.iloc[tri], Ltr.cohort, "abundance"); ab_te = F.transform(RD.iloc[tei], D.iloc[tei].cohort, "abundance")
            mu, sd = meta[tri].mean(0), meta[tri].std(0) + 1e-9
            mtr, mte = (meta[tri] - mu) / sd, (meta[tei] - mu) / sd
            Xtr, Xte = {"metadata_only": (mtr, mte), "abundance": (ab_tr, ab_te),
                        "abundance+metadata": (np.hstack([ab_tr, mtr]), np.hstack([ab_te, mte]))}[name]
            m = make_model("logreg", 0.1).fit(Xtr, D.y.values[tri]); s[tei] = m.predict_proba(Xte)[:, 1]
        auc = roc_auc_score(D.y, s); lo, hi = boot_ci(D.y.values, s, D.group.values, rng)
        rows.append(dict(analysis="within_david_5fold_sibling_grouped_complete_cases", test_cohort="david", features=name, model="logreg(C=0.1)",
                         per_cohort_std=False, n_test=len(D), n_asd=int(D.y.sum()), auc=round(auc, 3),
                         ci_low=round(lo, 3), ci_high=round(hi, 3), chosen_C=0.1, perm_p=None, perm_null_mean=None, perm_null_95=None, sibling_pair_concordance=None))
        print(rows[-1], flush=True)
    out = pd.DataFrame(rows)
    # summary rows: mean LOCO AUC across the 3 test cohorts
    for (k, m, cs), g in out[out.analysis == "LOCO"].groupby(["features", "model", "per_cohort_std"]):
        rows.append(dict(analysis="LOCO_mean_of_3", test_cohort="all", features=k, model=m, per_cohort_std=cs,
                         n_test=int(g.n_test.sum()), n_asd=int(g.n_asd.sum()), auc=round(g.auc.mean(), 3),
                         ci_low=None, ci_high=None, chosen_C=None, perm_p=None, perm_null_mean=None, perm_null_95=None))
    pd.DataFrame(rows).to_csv("loco_results.csv", index=False)
    hp = os.path.join(a.data, "holdout", "genus_counts.tsv")
    if os.path.exists(hp):
        RH, _, _ = load(a.data, "holdout", holdout=True)
        allR = pd.concat([R, RH]).fillna(0.0); RH = allR.loc[RH.index]; R2 = allR.loc[R.index]
        tr = np.ones(len(L), bool); F = Featuriser(False).fit(R2, L)
        C = 0.01
        m = make_model("logreg", C).fit(F.transform(R2, L.cohort, "abundance"), y)
        s = m.predict_proba(F.transform(RH, pd.Series("holdout", index=RH.index), "abundance"))[:, 1]
        pd.DataFrame({"sample_id": RH.index, "score": s}).to_csv("predictions.csv", index=False)
    else:
        print("no holdout file: predictions.csv skipped")

if __name__ == "__main__":
    main()
