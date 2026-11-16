#!/usr/bin/env python3
"""200-permutation controls: technical-only LOCO and grouped within-David metadata/microbiome."""
import argparse,pathlib,numpy as np,pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler
from run import load,feature,pred,auc,ci,permute_source,SEED,COHORTS
ap=argparse.ArgumentParser();ap.add_argument('--train-dir',type=pathlib.Path,required=True);ap.add_argument('--out-dir',type=pathlib.Path,required=True);ap.add_argument('--permutations',type=int,default=200);args=ap.parse_args()
X,M,_,_=load(args.train_dir,'family_genus');Y=(M.diagnosis=='ASD').astype(int).to_numpy();coh=M.cohort.to_numpy();groups=M.pair_id.to_numpy();rows=[]
for held in COHORTS:
    rng=np.random.default_rng(SEED);tr=np.flatnonzero(coh!=held);te=np.flatnonzero(coh==held)
    for model,vec in [('depth_only',np.log10(M.depth.to_numpy()+1)),('richness_only',M.richness.to_numpy(float))]:
        a=vec[tr].reshape(-1,1);b=vec[te].reshape(-1,1);z=StandardScaler().fit(a);a=z.transform(a);b=z.transform(b)
        obs=auc(Y[te],pred(a,Y[tr],b,.01));null=[]
        for k in range(args.permutations):
            yp=permute_source(Y[tr],coh[tr],groups[tr],rng);null.append(auc(Y[te],pred(a,yp,b,.01)))
        rows.append(dict(split='loco',cohort=held,model=model,auc=obs,null_mean=np.mean(null),null_low=np.quantile(null,.025),null_high=np.quantile(null,.975),p_raw=(1+sum(q>=obs for q in null))/(len(null)+1),permutations=len(null)))
# Within-David pair-split seeds and folds are identical to the main grouped comparison.
good=(M.cohort=='david')&M.sex.isin(['m','f'])&M.age.notna();ids=np.flatnonzero(good.to_numpy());Xd=X[ids];y=Y[ids];grp=groups[ids];met=np.column_stack(((M.sex.to_numpy()[ids]=='m').astype(float),M.age.to_numpy(float)[ids]))
models=['metadata_only','abundance','combined','microbiome_plus_metadata'];cv=list(StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=SEED).split(Xd,y,grp)); folds={}
for kind in models:
    folds[kind]=[]
    for itr,ite in cv:
        if kind=='metadata_only':a,b=met[itr],met[ite]
        elif kind=='microbiome_plus_metadata':a,b=feature(Xd[itr],Xd[ite],'abundance');a=np.column_stack((a,met[itr]));b=np.column_stack((b,met[ite]))
        else:a,b=feature(Xd[itr],Xd[ite],kind)
        sc=StandardScaler().fit(a);folds[kind].append((itr,ite,sc.transform(a),sc.transform(b)))
rng=np.random.default_rng(SEED+3)
for kind in models:
    def score(yy):
        v=np.zeros(len(yy))
        for itr,ite,a,b in folds[kind]: v[ite]=pred(a,yy[itr],b,.01)
        return v
    obs=auc(y,score(y));null=[]
    for _ in range(args.permutations):
        yp=permute_source(y,np.array(['david']*len(y)),grp,rng)
        null.append(auc(y,score(yp)))
    rows.append(dict(split='david_grouped_5fold',cohort='david',model=kind,auc=obs,null_mean=np.mean(null),null_low=np.quantile(null,.025),null_high=np.quantile(null,.975),p_raw=(1+sum(q>=obs for q in null))/(len(null)+1),permutations=len(null)))
pd.DataFrame(rows).to_csv(args.out_dir/'technical_metadata_null.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False))
