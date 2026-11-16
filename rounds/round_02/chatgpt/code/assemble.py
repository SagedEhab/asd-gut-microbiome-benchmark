#!/usr/bin/env python3
"""Combine per-cohort saved work from run.py. Recomputes global Holm across reported comparisons."""
import pathlib,sys,numpy as np,pandas as pd
root=pathlib.Path(sys.argv[1]); sources=[pathlib.Path(s) for s in sys.argv[2:]]
for fn in ['loco_results.csv','regularization_sensitivity.csv','oof_predictions.csv']:
    fs=[p/fn for p in sources]
    dfs=[]
    for f in fs:
        if f.is_file():
            try:
                d=pd.read_csv(f)
                if len(d):dfs.append(d)
            except pd.errors.EmptyDataError:pass
    if dfs:pd.concat(dfs,ignore_index=True).to_csv(root/fn,index=False)
for fn in ['david_grouped_results.csv','david_grouped_scores.csv']:
    src=next((p/fn for p in sources if (p/fn).exists()),None)
    if src:(root/fn).write_bytes(src.read_bytes())
df=pd.read_csv(root/'loco_results.csv')
for mask,col in [((df.key=='family_genus')&(df.setting=='nested_C')&(df.model.isin(['abundance','network','combined'])),'p_holm_nine'),((df.key=='family_genus')&(df.setting=='prespecified_C_0.01'),'p_holm_three_headline'),((df.setting=='nested_C')&(df.model.isin(['abundance','network','combined'])),'p_holm_eighteen')]:
    p=df.loc[mask,'p_raw'].values;order=np.argsort(p);adjust=np.zeros(len(p));maxv=0
    for rank,j in enumerate(order): maxv=max(maxv,(len(p)-rank)*p[j]);adjust[j]=min(1,maxv)
    df.loc[mask,col]=adjust
df.to_csv(root/'loco_results.csv',index=False)
