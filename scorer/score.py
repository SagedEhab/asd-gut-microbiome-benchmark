"""Score every rounds/round_NN/<agent>/predictions.csv against the PRIVATE holdout labels.

Private file (never committed): F:\\masters\\ai_benchmark_private\\holdout_labels.tsv  with columns sample_id, diagnosis (ASD/Control)
Usage:  python -I scorer/score.py --round NN --final [--private PATH]
The holdout may be scored ONCE for the whole study: a stamp file blocks repeat scoring so the holdout cannot become a tuning set.
Output: table on screen and scoring/performance_roundNN.md. Performance is only 10 points of the rubric; intervals that overlap are a tie.
"""
import argparse, os, sys
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score, balanced_accuracy_score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(pred, ids):
    errs = []
    if list(pred.columns[:2]) != ["sample_id", "score"]:
        errs.append("columns must start with sample_id,score")
        return errs
    pred["sample_id"] = pred["sample_id"].astype(str)
    if pred.sample_id.duplicated().any(): errs.append("duplicate sample_id")
    if set(pred.sample_id) != set(ids): errs.append(f"sample_id mismatch: missing {len(set(ids)-set(pred.sample_id))}, extra {len(set(pred.sample_id)-set(ids))}")
    if not np.isfinite(pd.to_numeric(pred.score, errors="coerce")).all(): errs.append("non-numeric or non-finite score")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--private", default=r"F:\masters\ai_benchmark_private\holdout_labels.tsv")
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--final", action="store_true", help="confirms this is the single final scoring")
    a = ap.parse_args()
    stamp = os.path.join(ROOT, "scoring", "FINAL_SCORED")
    if not a.final:
        sys.exit("Refusing: pass --final to confirm this is the one and only holdout scoring (see PROCESS.md).")
    if os.path.exists(stamp):
        sys.exit("Refusing: the holdout was already scored once (scoring/FINAL_SCORED exists).")
    lab = pd.read_csv(a.private, sep="\t"); lab["sample_id"] = lab.sample_id.astype(str)
    y = (lab.diagnosis == "ASD").astype(int).values; ids = lab.sample_id.values
    rng = np.random.default_rng(0); rows = []
    sub = os.path.join(ROOT, "rounds", f"round_{a.round:02d}")
    for ai in sorted(os.listdir(sub)):
        if not os.path.isdir(os.path.join(sub, ai)):
            continue
        p = os.path.join(sub, ai, "predictions.csv")
        if not os.path.exists(p):
            rows.append(dict(ai=ai, status="no predictions.csv")); continue
        pred = pd.read_csv(p); errs = check(pred, ids)
        if errs:
            rows.append(dict(ai=ai, status="INVALID: " + "; ".join(errs))); continue
        s = pred.set_index("sample_id").loc[ids, "score"].astype(float).values
        boots = []
        for _ in range(2000):
            i = rng.integers(0, len(y), len(y))
            if len(set(y[i])) == 2: boots.append(roc_auc_score(y[i], s[i]))
        lo, hi = np.percentile(boots, [2.5, 97.5])
        bal = balanced_accuracy_score(y, (s >= 0.5).astype(int)) if ((s >= 0) & (s <= 1)).all() else np.nan
        rows.append(dict(ai=ai, status="ok", n=len(y), auc=round(roc_auc_score(y, s), 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3), balanced_acc_at_0_5=round(bal, 3) if bal == bal else ""))
    df = pd.DataFrame(rows)
    ok = df[df.status == "ok"].copy()
    if len(ok):
        ok = ok.sort_values("auc", ascending=False)
        tied = [r.ai for r in ok.itertuples() if ok.iloc[0].ci_lo <= r.ci_hi and r.ci_lo <= ok.iloc[0].ci_hi]
        note = f"Top AUC interval overlaps with: {', '.join(tied)} -> treat as a tie." if len(tied) > 1 else "Top AUC is separated from the others."
    else:
        note = "No valid submissions."
    out = df.to_string(index=False) + "\n\n" + note + "\n"
    print(out)
    open(stamp, "w").write(f"scored round {a.round}\n")
    with open(os.path.join(ROOT, "scoring", f"performance_round{a.round:02d}.md"), "w") as f:
        f.write("# Holdout performance (10 points of the rubric)\n\n```\n" + out + "```\n")


if __name__ == "__main__":
    sys.exit(main())
