#!/usr/bin/env python3
"""When (and only when) feature-only holdout exists, apply the frozen headline model."""
import argparse,pathlib,re,numpy as np,pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from run import load,feature,SEED
ap=argparse.ArgumentParser();ap.add_argument('--train-dir',type=pathlib.Path,required=True);ap.add_argument('--feature-file',type=pathlib.Path,required=True);ap.add_argument('--out-dir',type=pathlib.Path,required=True);args=ap.parse_args()
if not args.feature_file.exists():raise SystemExit('No feature-only holdout; skipping; no predictions.csv created.')
X,M,cols,stats=load(args.train_dir,'family_genus');y=(M.diagnosis=='ASD').astype(int).to_numpy()
a=pd.read_csv(args.feature_file,sep='\t',dtype={'sample_id':str}).set_index('sample_id');assert a.index.is_unique
key={}
for col in a.columns:
 gm=re.search(r'(?:^|;)g__([^;]+)$',col);fm=re.search(r'(?:^|;)f__([^;]+)',col)
 if gm is None or not gm.group(1).strip('_ '):continue
 g=gm.group(1).strip().lower();f=fm.group(1).strip().lower() if fm else 'unknown';key.setdefault(f+'|'+g,[]).append(col)
B=pd.DataFrame({k:a[v].sum(axis=1) for k,v in key.items()},index=a.index).reindex(columns=cols,fill_value=0).to_numpy(dtype=float)
train,test=feature(X,B,'abundance');sc=StandardScaler().fit(train)
fit=LogisticRegression(C=.01,max_iter=500,solver='liblinear',random_state=SEED).fit(sc.transform(train),y)
pred=fit.predict_proba(sc.transform(test))[:,1];pd.DataFrame({'sample_id':a.index,'score':pred}).to_csv(args.out_dir/'predictions.csv',index=False)
