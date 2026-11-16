"""Leave-one-cohort-out analysis with full-pipeline permutation nulls, per-C sensitivity,
technical baselines, harmonisation and rarefaction variants, depth-matched subsets and the David sibling test."""
import time
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from common import (COHORTS, C_GRID, SEED, RAREFY_DEPTH, Featuriser, harmonise, scalar_feature, fit_score, auc,
                    group_boot_ci, permute_labels, perm_p, sibling_concordance, depth_match)

KINDS = ["abundance", "network", "combined", "depth_only", "richness_only"]


def build_cache(R, L):
    """Label-free features for every outer fold and every inner fold. cache[test][split] = dict(kind->(Xtr,Xte), tr, te)."""
    cache = {}
    logdepth = np.log10(L.depth.values)
    rich = (R.values > 0).sum(1).astype(float)
    for test in COHORTS:
        tr_c = [c for c in COHORTS if c != test]
        splits = {"outer": (np.where((L.cohort != test).values)[0], np.where((L.cohort == test).values)[0])}
        for ic in tr_c:
            splits[ic] = (np.where(L.cohort.isin([c for c in tr_c if c != ic]).values)[0], np.where((L.cohort == ic).values)[0])
        cache[test] = {}
        for name, (tr, te) in splits.items():
            F = Featuriser().fit(R.iloc[tr], L.cohort.iloc[tr])
            ftr, fte = F.transform(R.iloc[tr]), F.transform(R.iloc[te])
            d = {k: (ftr[k], fte[k]) for k in ("abundance", "network", "combined")}
            d["depth_only"] = scalar_feature(logdepth[tr], logdepth[te])
            d["richness_only"] = scalar_feature(rich[tr], rich[te])
            cache[test][name] = dict(feats=d, tr=tr, te=te, n_vocab=len(F.vocab), n_modules=len(F.modules))
    return cache


def run_kind(cache, kind, y):
    """Full pipeline for one feature kind and one label vector. Returns per test cohort: chosen C, scores at
    chosen C, and scores at every C."""
    out = {}
    for test in COHORTS:
        inner = [k for k in cache[test] if k != "outer"]
        means = []
        for C in C_GRID:
            a = []
            for ic in inner:
                s = cache[test][ic]
                Xtr, Xte = s["feats"][kind]
                a.append(auc(y[s["te"]], fit_score(Xtr, y[s["tr"]], Xte, C)))
            means.append(np.nanmean(a))
        best = C_GRID[int(np.nanargmax(np.round(means, 10)))]  # ties -> first (smallest) C
        s = cache[test]["outer"]
        Xtr, Xte = s["feats"][kind]
        perC = {C: fit_score(Xtr, y[s["tr"]], Xte, C) for C in C_GRID}
        out[test] = dict(C=best, score=perC[best], perC=perC, te=s["te"])
    return out


def summarise_null(res, y_true, subsets):
    """AUCs (chosen C and each fixed C) for one permuted run, evaluated against TRUE held-out labels."""
    row = {}
    for test, r in res.items():
        yt = y_true[r["te"]]
        row[(test, "chosen")] = auc(yt, r["score"])
        for C in C_GRID:
            row[(test, C)] = auc(yt, r["perC"][C])
        if test in subsets:
            pos = np.searchsorted(r["te"], subsets[test])
            row[(test, "matched")] = auc(yt[pos], r["score"][pos])
    row[("mean", "chosen")] = np.mean([row[(t, "chosen")] for t in COHORTS])
    row[("mean_ex_zou", "chosen")] = np.mean([row[(t, "chosen")] for t in ("ding", "david")])
    for C in C_GRID:
        row[("mean", C)] = np.mean([row[(t, C)] for t in COHORTS])
        row[("mean_ex_zou", C)] = np.mean([row[(t, C)] for t in ("ding", "david")])
    return row


def _perm_chunk(cache, kinds, ylist, y_true, subsets):
    return [{k: summarise_null(run_kind(cache, k, yp), y_true, subsets) for k in kinds} for yp in ylist]


def analyse_variant(raws, L, key, rar, n_perm, kinds, rng, log):
    R, hlog = harmonise(raws, key, RAREFY_DEPTH if rar else None)
    R = R.loc[L.index]
    if rar:
        kinds = [k for k in kinds if k != "depth_only"]   # depth is constant after rarefaction
    t0 = time.time()
    cache = build_cache(R, L)
    y = L.y.values
    subsets = {c: depth_match(L, np.where((L.cohort == c).values)[0]) for c in COHORTS}
    obs = {k: run_kind(cache, k, y) for k in kinds}
    obs_sum = {k: summarise_null(obs[k], y, subsets) for k in kinds}
    perms = [permute_labels(L, rng) for _ in range(n_perm)]
    chunks = np.array_split(np.arange(n_perm), 2)
    res = Parallel(n_jobs=2)(delayed(_perm_chunk)(cache, kinds, [perms[i] for i in ch], y, subsets) for ch in chunks)
    nulls = [r for part in res for r in part]
    log(f"variant key={key} rarefied={rar}: {n_perm} perms x {len(kinds)} kinds in {time.time()-t0:.0f}s")
    rows, crow = [], []
    variant = f"{key}{'_rarefied' if rar else ''}"
    for k in kinds:
        for test in COHORTS + ["mean", "mean_ex_zou"]:
            o = obs_sum[k][(test, "chosen")]
            nl = np.array([n[k][(test, "chosen")] for n in nulls])
            row = dict(variant=variant, features=k, test_cohort=test, auc=round(o, 4),
                       null_mean=round(nl.mean(), 4), null_q025=round(np.percentile(nl, 2.5), 4),
                       null_q975=round(np.percentile(nl, 97.5), 4), perm_p=round(perm_p(o, nl), 4), n_perm=n_perm)
            if test in COHORTS:
                r = obs[k][test]
                yt, s = y[r["te"]], r["score"]
                lo, hi = group_boot_ci(yt, s, L.group.values[r["te"]], rng)
                row.update(n_test=len(yt), n_asd=int(yt.sum()), ci_low=round(lo, 4), ci_high=round(hi, 4), chosen_C=r["C"],
                           n_vocab=cache[test]["outer"]["n_vocab"], n_modules=cache[test]["outer"]["n_modules"])
                # depth-matched evaluation subset
                sub = subsets[test]
                om = obs_sum[k][(test, "matched")]
                nm = np.array([n[k][(test, "matched")] for n in nulls])
                row.update(matched_n=len(sub), matched_auc=round(om, 4), matched_null_q975=round(np.percentile(nm, 97.5), 4),
                           matched_perm_p=round(perm_p(om, nm), 4))
                if test == "david":
                    c, nf, p, ci = sibling_concordance(L.iloc[r["te"]], s)
                    row.update(sib_concordance=round(c, 4), sib_families=nf, sib_p=round(p, 4),
                               sib_ci_low=round(ci[0], 4), sib_ci_high=round(ci[1], 4))
            rows.append(row)
            # per-C sensitivity with fixed-C null
            for C in C_GRID:
                oc = obs_sum[k][(test, C)]
                nc = np.array([n[k][(test, C)] for n in nulls])
                crow.append(dict(variant=variant, features=k, test_cohort=test, C=C, auc=round(oc, 4),
                                 null_q975=round(np.percentile(nc, 97.5), 4), perm_p_fixedC=round(perm_p(oc, nc), 4)))
    # save observed out-of-fold scores
    oof = []
    for k in kinds:
        for test in COHORTS:
            r = obs[k][test]
            oof.append(pd.DataFrame(dict(variant=variant, features=k, sample_id=L.index[r["te"]], cohort=test,
                                         y=y[r["te"]], score=r["score"])))
    return rows, crow, pd.concat(oof), hlog
