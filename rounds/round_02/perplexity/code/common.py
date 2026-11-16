"""Shared loading, harmonisation, transforms and featurisation (round 2, Perplexity).
Everything that is fitted (vocabulary, CLR reference set, scaling, network) is fitted on the rows passed as
`train` only; nothing here ever sees labels except the explicit model-fitting helpers."""
import os, re, warnings
import numpy as np, pandas as pd, networkx as nx
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
SEED = 20261112
COHORTS = ["ding", "zou", "david"]
C_GRID = [0.001, 0.01, 0.1, 1.0]
PSEUDO = 0.5
PREV = 0.10
NET_THR = 0.3
RAREFY_DEPTH = 5000


# ---------------------------------------------------------------- harmonisation
def key_of(col, mode):
    """mode='famgenus': family|genus ; mode='genus': genus name only. None = unassigned at genus level."""
    f = [x.strip() for x in col.split(";")]
    last = f[-1]
    if not last.startswith("g__") or last == "g__":
        return None
    g = last[3:].lower().replace(" ", "_").replace("[", "").replace("]", "")
    if mode == "genus":
        return g
    fam = [x for x in f if x.startswith("f__")]
    fam = fam[-1][3:].lower().replace(" ", "_") if fam else "nofamily"
    return fam + "|" + g


def load_raw(datadir):
    """Raw count tables (original columns) and labels; no harmonisation yet."""
    raws, labs = {}, []
    for c in COHORTS:
        X = pd.read_csv(os.path.join(datadir, "train", c, "genus_counts.tsv"), sep="\t", index_col=0)
        X.index = X.index.astype(str)
        L = pd.read_csv(os.path.join(datadir, "train", c, "labels.tsv"), sep="\t", dtype={"sample_id": str}).set_index("sample_id")
        L = L.loc[X.index].copy()
        L["y"] = (L["diagnosis"] == "ASD").astype(int)
        L["cohort"] = c
        if "sibling_pair" not in L:
            L["sibling_pair"] = np.nan
        L["group"] = [f"{c}_fam{int(p)}" if pd.notna(p) else f"{c}_{i}" for i, p in zip(L.index, L["sibling_pair"])]
        L["depth"] = X.sum(axis=1).values          # all reads incl. unassigned
        raws[c] = X
        labs.append(L)
    return raws, pd.concat(labs)


def rarefy(X, depth, rng):
    """Subsample every sample to `depth` reads without replacement (label-free, per sample)."""
    V = X.values.astype(np.int64)
    out = np.zeros_like(V)
    for i in range(V.shape[0]):
        out[i] = rng.multivariate_hypergeometric(V[i], depth)
    return pd.DataFrame(out, index=X.index, columns=X.columns)


def harmonise(raws, mode, rarefy_depth=None, seed=SEED):
    """Return a samples x keys count matrix (union of keys, missing = 0) and a log of the harmonisation."""
    rng = np.random.default_rng(seed)
    mats, logs = [], []
    for c in COHORTS:
        X = raws[c]
        if rarefy_depth:
            X = rarefy(X, rarefy_depth, rng)
        keys = [key_of(k, mode) for k in X.columns]
        keep = np.array([k is not None for k in keys])
        G = X.loc[:, keep].T.groupby([k for k in keys if k is not None]).sum().T
        logs.append(dict(cohort=c, key=mode, rarefied=bool(rarefy_depth), raw_columns=X.shape[1],
                         unassigned_columns_dropped=int((~keep).sum()),
                         unassigned_read_fraction=round(float(X.loc[:, ~keep].values.sum() / X.values.sum()), 4),
                         keys=G.shape[1]))
        mats.append(G)
    R = pd.concat(mats).fillna(0.0)
    shared = set.intersection(*[set(m.columns) for m in mats])
    for lg in logs:
        lg["keys_shared_by_all_3"] = len(shared)
    return R, logs


# ---------------------------------------------------------------- featurisation (label-free)
class Featuriser:
    """Fitted on training rows only. Produces abundance (CLR, z-scored), network and combined features."""

    def fit(self, R, cohort):
        prev = pd.concat([(R[cohort == c] > 0).mean() for c in pd.unique(cohort)], axis=1).min(axis=1)
        self.vocab = list(prev[prev >= PREV].index)
        A = self._clr(R)
        self.mu, self.sd = A.mean(0), A.std(0)
        self.sd[self.sd == 0] = 1.0
        Z = (A - self.mu) / self.sd
        # network: mean of within-training-cohort Spearman correlations (avoids batch-driven edges)
        rhos = [np.nan_to_num(spearmanr(Z[(cohort == c).values]).statistic) for c in pd.unique(cohort)]
        rho = np.mean(rhos, axis=0)
        np.fill_diagonal(rho, 0)
        self.rho = rho
        G = nx.Graph()
        G.add_nodes_from(range(len(self.vocab)))
        ii, jj = np.where(np.triu(np.abs(rho) >= NET_THR, 1))
        for i, j in zip(ii, jj):
            G.add_edge(i, j, weight=abs(rho[i, j]))
        comms = nx.community.louvain_communities(G, weight="weight", seed=SEED)
        self.modules = [sorted(m) for m in comms if len(m) >= 3]
        self.signs = []
        for m in self.modules:
            sub = Z[:, m]
            vt = np.linalg.svd(sub - sub.mean(0), full_matrices=False)[2][0]
            self.signs.append(np.where(vt >= 0, 1.0, -1.0))
        self.deg = np.array([G.degree(i, weight="weight") for i in range(len(self.vocab))])
        self.hubs = np.argsort(-self.deg)[:max(5, len(self.vocab) // 10)]
        N = self._net_raw(R, Z)
        self.nmu, self.nsd = N.mean(0), N.std(0)
        self.nsd[self.nsd == 0] = 1.0
        return self

    def _clr(self, R):
        V = np.log(R.reindex(columns=self.vocab, fill_value=0.0).values + PSEUDO)
        return V - V.mean(1, keepdims=True)

    def _net_raw(self, R, Z):
        mod = np.column_stack([(Z[:, m] * s).mean(1) for m, s in zip(self.modules, self.signs)]) if self.modules else np.zeros((len(Z), 0))
        pres = (R.reindex(columns=self.vocab, fill_value=0.0).values > 0).astype(float)
        hub = pres[:, self.hubs].mean(1, keepdims=True)
        wdeg = (pres * self.deg).sum(1, keepdims=True) / (self.deg.sum() + 1e-9)
        coh = np.einsum("ij,jk,ik->i", Z, self.rho, Z)[:, None] / (Z.shape[1] ** 2)
        return np.hstack([mod, hub, wdeg, coh])

    def transform(self, R):
        Z = (self._clr(R) - self.mu) / self.sd
        N = (self._net_raw(R, Z) - self.nmu) / self.nsd
        return {"abundance": Z, "network": N, "combined": np.hstack([Z, N])}


def scalar_feature(v_tr, v_te):
    mu, sd = v_tr.mean(), v_tr.std() or 1.0
    return ((v_tr - mu) / sd)[:, None], ((v_te - mu) / sd)[:, None]


# ---------------------------------------------------------------- models / stats
def lr(C):
    return LogisticRegression(C=C, l1_ratio=0, solver="lbfgs", max_iter=5000)


def fit_score(Xtr, ytr, Xte, C):
    if len(np.unique(ytr)) < 2:
        return np.zeros(len(Xte))
    return lr(C).fit(Xtr, ytr).decision_function(Xte)


def auc(y, s):
    return roc_auc_score(y, s) if len(np.unique(y)) == 2 else np.nan


def group_boot_ci(y, s, groups, rng, n=2000):
    ug = pd.unique(groups)
    idx = {g: np.where(groups == g)[0] for g in ug}
    out = []
    for _ in range(n):
        bi = np.concatenate([idx[g] for g in rng.choice(ug, len(ug))])
        if len(np.unique(y[bi])) == 2:
            out.append(roc_auc_score(y[bi], s[bi]))
    return np.percentile(out, [2.5, 97.5])


def permute_labels(L, rng):
    """Shuffle labels within each cohort; in cohorts with sibling groups, permute within each family
    (singletons are shuffled among themselves). Returns a new label vector aligned to L."""
    y = L.y.values.copy()
    for c in pd.unique(L.cohort):
        m = np.where((L.cohort == c).values)[0]
        sib = L.sibling_pair.values[m]
        if np.all(pd.isna(sib)):
            y[m] = rng.permutation(y[m])
            continue
        grp = L.group.values[m]
        sizes = pd.Series(grp).value_counts()
        singles = [i for i, g in zip(m, grp) if sizes[g] == 1]
        y[singles] = rng.permutation(y[singles])
        for g in sizes[sizes > 1].index:
            ii = m[grp == g]
            y[ii] = rng.permutation(y[ii])
    return y


def perm_p(obs, null):
    null = np.asarray(null)
    return (1 + np.sum(null >= obs - 1e-12)) / (1 + len(null))


def sibling_concordance(L, s):
    """Family-level fraction of ASD-vs-control comparisons in which the ASD child scores higher;
    discordant families only. Returns (mean concordance, n families, sign-flip p one-sided, CI)."""
    d = pd.DataFrame({"g": L.group.values, "y": L.y.values, "s": s})
    fam = []
    for _, g in d.groupby("g"):
        if g.y.nunique() == 2:
            a, b = g.s[g.y == 1].values, g.s[g.y == 0].values
            fam.append(np.mean([(x > z) + 0.5 * (x == z) for x in a for z in b]))
    fam = np.array(fam)
    rng = np.random.default_rng(SEED)
    obs = fam.mean()
    flips = rng.choice([-1, 1], size=(20000, len(fam)))
    null = 0.5 + (flips * (fam - 0.5)).mean(1)
    p = (1 + np.sum(null >= obs - 1e-12)) / (1 + len(null))
    boots = [rng.choice(fam, len(fam)).mean() for _ in range(5000)]
    return obs, len(fam), p, np.percentile(boots, [2.5, 97.5])


def holm(pvals):
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    m = len(p)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj


def depth_match(L, idx, caliper=0.05):
    """1:1 nearest-neighbour matching of ASD to control on log10 depth within a cohort (evaluation subset only;
    uses that cohort's labels to choose which samples to *evaluate*, never to fit anything)."""
    sub = L.iloc[idx]
    ld = np.log10(sub.depth.values)
    asd = list(np.where(sub.y.values == 1)[0])
    ctl = list(np.where(sub.y.values == 0)[0])
    pairs = []
    cand = sorted([(abs(ld[a] - ld[c]), a, c) for a in asd for c in ctl])
    ua, uc = set(), set()
    for d, a, c in cand:
        if d > caliper:
            break
        if a in ua or c in uc:
            continue
        ua.add(a); uc.add(c); pairs.append((a, c))
    keep = sorted([a for a, _ in pairs] + [c for _, c in pairs])
    return np.asarray(idx)[keep]
