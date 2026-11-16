#!/usr/bin/env python3
"""Seeded 5000-count rarefaction sensitivity, independent of scoring selection."""
import argparse,pathlib,numpy as np,pandas as pd
from run import load,getfold,pred,auc,COHORTS,KINDS,SEED
p=argparse.ArgumentParser();p.add_argument('--train-dir',type=pathlib.Path,required=True);p.add_argument('--out-dir',type=pathlib.Path,required=True);a=p.parse_args()
X,M,_,_=load(a.train_dir,'family_genus'); y=(M.diagnosis=='ASD').to_numpy(int);c=M.cohort.to_numpy();out=[]
for rep in range(5):
    rng=np.random.default_rng(SEED+rep);rare=np.zeros_like(X)
    for i,x in enumerate(X):
        total=x.sum();depth=min(5000,int(total));rare[i]=rng.multinomial(depth,x/total) if total else x
    for held in COHORTS:
        tr=np.flatnonzero(c!=held);te=np.flatnonzero(c==held)
        for model in KINDS:
            train,test=getfold(rare,tr,te,model);sc=pred(train,y[tr],test,.01)
            out.append(dict(replicate=rep,cohort=held,model=model,auc=auc(y[te],sc),n_test=len(te),depth_target=5000,C=.01))
pd.DataFrame(out).to_csv(a.out_dir/'rarefaction_sensitivity.csv',index=False)
print(pd.DataFrame(out).groupby(['cohort','model']).auc.agg(['mean','std']).round(3))
