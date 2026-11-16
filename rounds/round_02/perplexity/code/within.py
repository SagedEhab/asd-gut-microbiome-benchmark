"""Within-cohort analyses (secondary): technical baselines in every cohort, and the David
metadata / microbiome / combined comparison with sibling families kept together.
python code/within.py --data <repo>/data --out <outdir> [--n_perm 200]"""
import argparse, os, sys, time
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from sklearn.model_selection import StratifiedGroupKFold, GroupKFold
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_raw, harmonise, fit_score, auc, permute_labels, perm_p, sibling_concordance, holm, SEED, RAREFY_DEPTH, PSEUDO, PREV

C_GRID = [0.001, 0.01, 0.1, 1.0]
N_REP = 2


def clr_feats(Rtr, Rte):
    """CLR on genera with >=10% prevalence in the training rows; z-scored on training rows."""
    v = Rtr.columns[(Rtr > 0).mean() >= PREV]
    f = lambda R: (lambda V: V - V.mean(1, keepdims=True))(np.log(R[v].values + PSEUDO))
    A, B = f(Rtr), f(Rte)
    mu, sd = A.mean(0), A.std(0); sd[sd == 0] = 1
    return (A - mu) / sd, (B - mu) / sd


def zcols(Mtr, Mte):
    mu, sd = Mtr.mean(0), Mtr.std(0); sd[sd == 0] = 1
    return (Mtr - mu) / sd, (Mte - mu) / sd


def make_features(kind, R, M, tr, te):
    """Label-free features for rows tr (fit) and te (apply)."""
    if kind in ("abundance", "abundance_rarefied"):
        return clr_feats(R[kind].iloc[tr], R[kind].iloc[te])
    if kind == "depth_only":
        return zcols(M[["logdepth"]].values[tr], M[["logdepth"]].values[te])
    if kind == "richness_only":
        return zcols(M[["richness_rar"]].values[tr], M[["richness_rar"]].values[te])
    if kind == "metadata":
        return zcols(M[["male", "age"]].values[tr], M[["male", "age"]].values[te])
    if kind == "combined":
        a, b = clr_feats(R["abundance"].iloc[tr], R["abundance"].iloc[te])
        c, d = zcols(M[["male", "age"]].values[tr], M[["male", "age"]].values[te])
        return np.hstack([c, a]), np.hstack([d, b])
    raise ValueError(kind)


def build_cache(kinds, R, M, y, groups):
    """Fixed splits (from the observed labels) reused for every permutation; features are label-free."""
    reps = []
    for rep in range(N_REP):
        outer = list(StratifiedGroupKFold(5, shuffle=True, random_state=SEED + rep).split(np.zeros(len(y)), y, groups))
        folds = []
        for tr, te in outer:
            inner = list(GroupKFold(3).split(tr, groups=groups[tr]))
            f = dict(tr=tr, te=te, feats={k: make_features(k, R, M, tr, te) for k in kinds},
                     inner=[(tr[a], tr[b], {k: make_features(k, R, M, tr[a], tr[b]) for k in kinds}) for a, b in inner])
            folds.append(f)
        reps.append(folds)
    return reps


def run(cache, kind, y):
    """Returns per-repeat OOF scores for chosen C and for each fixed C."""
    n = len(y)
    out = {"chosen": np.zeros((N_REP, n)), **{C: np.zeros((N_REP, n)) for C in C_GRID}}
    chosen = []
    for r, folds in enumerate(cache):
        for f in folds:
            inner_auc = []
            for C in C_GRID:
                s = [auc(y[b], fit_score(fa[kind][0], y[a], fa[kind][1], C)) for a, b, fa in f["inner"]]
                inner_auc.append(np.nanmean(s))
            Cb = C_GRID[int(np.argmax(np.round(inner_auc, 10)))]   # argmax returns first = smallest C on ties
            chosen.append(Cb)
            Xtr, Xte = f["feats"][kind]
            for C in C_GRID:
                out[C][r, f["te"]] = fit_score(Xtr, y[f["tr"]], Xte, C)
            out["chosen"][r, f["te"]] = out[Cb][r, f["te"]]
    return out, chosen


def summ(out, y):
    """AUC = mean over repeats of the pooled-OOF AUC (scores are on a common logit scale within a repeat)."""
    return {k: float(np.mean([auc(y, out[k][r]) for r in range(N_REP)])) for k in out}


def perm_chunk(cache, kinds, ylist):
    return [{k: summ(run(cache, k, yp)[0], yp) for k in kinds} for yp in ylist]


def family_boot_delta(y, s1, s0, groups, rng, n=2000):
    ug = pd.unique(groups); idx = {g: np.where(groups == g)[0] for g in ug}; d = []
    for _ in range(n):
        bi = np.concatenate([idx[g] for g in rng.choice(ug, len(ug))])
        if len(np.unique(y[bi])) == 2:
            d.append(auc(y[bi], s1[bi]) - auc(y[bi], s0[bi]))
    return np.percentile(d, [2.5, 97.5])


def analyse(cohort, L, R, M, kinds, n_perm, rng, log, tag=""):
    y = L.y.values; groups = L.group.values
    t0 = time.time()
    cache = build_cache(kinds, R, M, y, groups)
    obs = {k: run(cache, k, y) for k in kinds}
    osum = {k: summ(obs[k][0], y) for k in kinds}
    perms = [permute_labels(L, rng) for _ in range(n_perm)]
    ch = np.array_split(np.arange(n_perm), 2)
    res = Parallel(n_jobs=2)(delayed(perm_chunk)(cache, kinds, [perms[i] for i in c]) for c in ch)
    nulls = [r for part in res for r in part]
    log(f"within {cohort}{tag}: n={len(y)} {n_perm} perms x {len(kinds)} kinds in {time.time()-t0:.0f}s")
    rows, crow = [], []
    for k in kinds:
        nl = np.array([z[k]["chosen"] for z in nulls])
        sc = obs[k][0]["chosen"].mean(0)
        row = dict(cohort=cohort + tag, features=k, n=len(y), n_asd=int(y.sum()), auc=round(osum[k]["chosen"], 4),
                   null_mean=round(nl.mean(), 4), null_q025=round(np.percentile(nl, 2.5), 4), null_q975=round(np.percentile(nl, 97.5), 4),
                   perm_p=round(perm_p(osum[k]["chosen"], nl), 4), n_perm=n_perm,
                   C_chosen_mode=pd.Series(obs[k][1]).mode()[0])
        if L.sibling_pair.notna().any():
            c, nf, p, ci = sibling_concordance(L, sc)
            row.update(sib_concordance=round(c, 4), sib_families=nf, sib_p=round(p, 4), sib_ci_low=round(ci[0], 4), sib_ci_high=round(ci[1], 4))
        if "male" in M:
            for sx, v in (("male", 1), ("female", 0)):
                m = M.male.values == v
                row[f"auc_within_{sx}"] = round(auc(y[m], sc[m]), 4)
        rows.append(row)
        for C in C_GRID:
            nc = np.array([z[k][C] for z in nulls])
            crow.append(dict(cohort=cohort + tag, features=k, C=C, auc=round(osum[k][C], 4), null_q975=round(np.percentile(nc, 97.5), 4),
                             perm_p_fixedC=round(perm_p(osum[k][C], nc), 4)))
    scores = pd.DataFrame({k: obs[k][0]["chosen"].mean(0) for k in kinds}, index=L.index).assign(y=y, group=groups)
    return rows, crow, scores, cache, obs


def conditional_microbiome_null(cache_kinds, L, R, M, n_perm, rng, log):
    """Does the microbiome add to sex+age?  Shuffle microbiome rows within sex x age-tertile strata
    (keeps the metadata-microbiome link, breaks any extra microbiome-label link), refit combined."""
    y = L.y.values
    strata = M.male.astype(str) + "_" + pd.qcut(M.age, 3, labels=False, duplicates="drop").astype(str)
    obs_meta = cache_kinds["metadata"]; obs_comb = cache_kinds["combined"]
    d_obs = obs_comb - obs_meta
    def one(seed):
        r = np.random.default_rng(seed)
        perm = np.arange(len(y))
        for s in pd.unique(strata):
            ii = np.where(strata.values == s)[0]; perm[ii] = r.permutation(ii)
        Rp = {"abundance": R["abundance"].iloc[perm].set_axis(R["abundance"].index)}
        cache = build_cache(["combined"], Rp, M, y, L.group.values)
        return summ(run(cache, "combined", y)[0], y)["chosen"] - obs_meta
    seeds = rng.integers(0, 2**31, n_perm)
    null = np.array(Parallel(n_jobs=2)(delayed(one)(s) for s in seeds))
    return d_obs, null


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--data", default="data"); ap.add_argument("--out", default=".")
    ap.add_argument("--n_perm", type=int, default=200); ap.add_argument("--n_cond", type=int, default=100)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    logf = open(os.path.join(a.out, "run_output_log.txt"), "a")
    def log(m): print(m, flush=True); logf.write(m + "\n"); logf.flush()
    rng = np.random.default_rng(SEED + 7)
    raws, Lall = load_raw(a.data)
    Rg, _ = harmonise(raws, "famgenus"); Rr, _ = harmonise(raws, "famgenus", RAREFY_DEPTH)
    rows, crows = [], []
    for c in ["ding", "zou", "david"]:
        m = (Lall.cohort == c).values
        L = Lall[m].copy()
        R = {"abundance": Rg.loc[L.index], "abundance_rarefied": Rr.loc[L.index]}
        M = pd.DataFrame(index=L.index)
        M["logdepth"] = np.log10(L.depth)
        M["richness_rar"] = (Rr.loc[L.index] > 0).sum(1)       # richness after rarefying to 5000 reads
        kinds = ["abundance", "abundance_rarefied", "depth_only", "richness_only"]
        if c == "david":
            keep = L.sex.notna() & L.age.notna()
            log(f"david complete cases: {int(keep.sum())} of {len(L)} (dropped {list(L.index[~keep])})")
            L = L[keep]; M = M[keep]; R = {k: v[keep.values] for k, v in R.items()}
            M["male"] = (L.sex == "m").astype(float); M["age"] = L.age.astype(float)
            kinds += ["metadata", "combined"]
        r, cr, sc, cache, obs = analyse(c, L, R, M, kinds, a.n_perm, rng, log)
        rows += r; crows += cr
        sc.to_csv(os.path.join(a.out, f"within_{c}_oof_scores.csv"))
        if c == "david":
            y = L.y.values; g = L.group.values
            lo, hi = family_boot_delta(y, sc["combined"].values, sc["metadata"].values, g, rng)
            ochosen = {k: next(x["auc"] for x in r if x["features"] == k) for k in ["metadata", "combined"]}
            d_obs, null = conditional_microbiome_null(ochosen, L, R, M, a.n_cond, rng, log)
            delta = dict(delta_auc_combined_minus_metadata=round(d_obs, 4), family_boot_ci_low=round(float(lo), 4), family_boot_ci_high=round(float(hi), 4),
                         cond_null_mean=round(float(null.mean()), 4), cond_null_q975=round(float(np.percentile(null, 97.5)), 4),
                         cond_perm_p=round(float(perm_p(d_obs, null)), 4), n_cond_perm=len(null))
            log(f"david delta: {delta}")
            pd.DataFrame([delta]).to_csv(os.path.join(a.out, "david_delta.csv"), index=False)
            # provisional: sex-coding sensitivity (swap m<->f in controls)
            L2 = L.copy(); M2 = M.copy()
            ctl = L2.y.values == 0
            M2.loc[ctl, "male"] = 1 - M2.loc[ctl, "male"]
            r2, cr2, _, _, _ = analyse("david", L2, R, M2, ["metadata", "combined"], a.n_perm, rng, log, tag="_controlsexswapped")
            rows += r2; crows += cr2
    W = pd.DataFrame(rows)
    W["holm_p_within"] = holm(W.perm_p.values).round(4)
    C = pd.DataFrame(crows)
    nsig = C.assign(s=C.perm_p_fixedC < 0.05).groupby(["cohort", "features"]).s.sum().rename("n_C_sig_fixed").reset_index()
    W = W.merge(nsig, on=["cohort", "features"])
    W["flag"] = np.where((W.perm_p < 0.05) & (W.n_C_sig_fixed <= 1), "holds_at_<=1_C", "")
    W.to_csv(os.path.join(a.out, "within_cohort_results.csv"), index=False)
    C.to_csv(os.path.join(a.out, "within_c_sensitivity.csv"), index=False)
    log(W.drop(columns=[c for c in W.columns if c.startswith("sib_ci")]).to_string())
