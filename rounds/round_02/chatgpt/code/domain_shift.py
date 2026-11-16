#!/usr/bin/env python3
"""Technical domain-classification diagnostic, NOT ASD evaluation."""
import argparse,pathlib,numpy as np,pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler
from run import load,feature,pred,auc,SEED
p=argparse.ArgumentParser();p.add_argument('--train-dir',type=pathlib.Path,required=True);p.add_argument('--out-dir',type=pathlib.Path,required=True);a=p.parse_args()
res=[]
for key in ['family_genus','genus']:
 X,M,cols,stats=load(a.train_dir,key); y=(M.cohort=='zou').to_numpy().astype(int);groups=M.pair_id.to_numpy();folds=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=SEED);scores=np.zeros(len(y));
 for tr,te in folds.split(X,y,groups):
  xtr,xte=feature(X[tr],X[te],'abundance');sc=StandardScaler().fit(xtr);scores[te]=pred(sc.transform(xtr),y[tr],sc.transform(xte),.01)
 res.append(dict(mapping=key,target='Zou_vs_Ding_David',auc=auc(y,scores),n=len(y),folds=5,interpretation='technical cohort membership classification; cannot separate 16S region, site, batch or depth'))
 # prevalence-independent fraction of each cohort's observed taxa present across cohorts
 for c in ['ding','zou','david']:
  ix=(M.cohort==c).to_numpy();observed=set(np.array(cols)[(X[ix]>0).any(axis=0)])
  for other in ['ding','zou','david']:
   jx=(M.cohort==other).to_numpy();o=set(np.array(cols)[(X[jx]>0).any(axis=0)])
   res.append(dict(mapping=key,target=f'{c}_vs_{other}_genus_presence_jaccard',auc=len(observed&o)/len(observed|o),n=len(observed|o),folds=np.nan,interpretation='observed taxon-key Jaccard; not predictive AUC'))
pd.DataFrame(res).to_csv(a.out_dir/'domain_shift_diagnostics.csv',index=False)
print(pd.DataFrame(res).to_string(index=False))
