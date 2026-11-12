"""Referee check of ChatGPT round 1: permutation null and sensitivity for the network model.
Uses ChatGPT's own code unchanged (imported), so any result here is about its pipeline.
Usage: python -I verify_chatgpt_zou.py <path to chatgpt/code/run.py> <train dir> <perms>"""
import sys, importlib.util
import numpy as np
from sklearn.metrics import roc_auc_score

spec = importlib.util.spec_from_file_location("cg", sys.argv[1]); cg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cg)
import pathlib
X, y, coh, groups, meta, names, stats = cg.read(pathlib.Path(sys.argv[2]))
perms = int(sys.argv[3]); rng = np.random.default_rng(1)

for held in ("zou", "david", "ding"):
    tr = coh != held; te = ~tr
    for kind in ("network", "combined"):
        C = cg.choose_c(X[tr], y[tr], coh[tr], kind)
        real = roc_auc_score(y[te], cg.fit_predict(X[tr], y[tr], X[te], kind, C))
        sens = {c: round(roc_auc_score(y[te], cg.fit_predict(X[tr], y[tr], X[te], kind, c)), 3) for c in (0.001, 0.01, 0.1, 1.0)}
        null = []
        for _ in range(perms):
            yp = y[tr].copy()
            for s in np.unique(coh[tr]):
                ix = np.flatnonzero(coh[tr] == s); yp[ix] = rng.permutation(yp[ix])
            Cp = cg.choose_c(X[tr], yp, coh[tr], kind)  # full pipeline, C re-chosen on permuted labels
            null.append(roc_auc_score(y[te], cg.fit_predict(X[tr], yp, X[te], kind, Cp)))
        null = np.array(null)
        p = (1 + (null >= real).sum()) / (1 + len(null))
        print(f"held={held:<6} {kind:<9} C={C:<6} AUC={real:.3f}  null mean {null.mean():.3f} [95% {np.quantile(null,.025):.3f}-{np.quantile(null,.975):.3f}]  perm p={p:.3f}  AUC by C: {sens}", flush=True)
