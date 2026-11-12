#!/usr/bin/env python3
"""Reproducible training-only, group-aware leave-one-cohort-out benchmark."""
import argparse, re, pathlib, json
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

COHORTS=('ding','zou','david'); SEED=20261112

def read(root):
    Xs=[];ys=[]; cs=[];groups=[];meta=[];stat={}
    for c in COHORTS:
        base=(root/c if (root/c/'genus_counts.tsv').exists() else root); a=pd.read_csv(base/(f'{c}_genus_counts.tsv' if base==root else 'genus_counts.tsv'),sep='\t').set_index('sample_id'); b=pd.read_csv(base/(f'{c}_labels.tsv' if base==root else 'labels.tsv'),sep='\t').set_index('sample_id')
        assert a.index.is_unique and b.index.is_unique and set(a.index)==set(b.index)
        a=a.loc[b.index];assert np.isfinite(a.to_numpy(dtype=float)).all() and (a.to_numpy(dtype=float)>=0).all()
        genera={}; dropped=0
        for col in a.columns:
            m=re.search(r'(?:^|;)g__([^;]+)$',col)
            if m is None or not m.group(1).strip('_ '):dropped+=1;continue
            genus=m.group(1).strip();genera.setdefault(genus,[]).append(col)
        z=pd.DataFrame({g:a[cols].sum(axis=1) for g,cols in genera.items()},index=a.index)
        Xs.append(z);ys.extend((b.diagnosis=='ASD').astype(int));cs.extend([c]*len(a))
        groups.extend([c+':'+str(v) if c=='david' else c+':'+str(idx) for idx,v in zip(b.index,b.get('sibling_pair',pd.Series(b.index,index=b.index)))])
        meta.append(pd.DataFrame({'age':pd.to_numeric(b['age'],errors='coerce') if 'age' in b else np.nan,'sex':b['sex'].map({'m':1,'f':0}) if 'sex' in b else np.nan},index=b.index))
        stat[c]={'samples':len(a),'genera':len(z.columns),'unassigned_columns_dropped':dropped,'ASD':int((b.diagnosis=='ASD').sum())}
    X=pd.concat(Xs).fillna(0);X.index=pd.Index(sum([list(x.index) for x in Xs],[]))
    return X.to_numpy(float),np.array(ys),np.array(cs),np.array(groups),pd.concat(meta).to_numpy(float),X.columns.tolist(),stat

def transform(A,B,kind):
    # learn prevalence and correlation only from A (fit fold); B never influences learned representation
    prevalent=(A>0).mean(axis=0)>=.10
    if not prevalent.any():prevalent[:]=True
    A=A[:,prevalent];B=B[:,prevalent]
    def clr(Z):
        Z=np.log(Z+0.5);return Z-Z.mean(axis=1,keepdims=True)
    a=clr(A);b=clr(B)
    if kind=='abundance':return a,b
    # network: graph learned on fit set, each genus summarized by its strongest 5 correlated neighbors;
    # each sample is projected onto this TRAIN-derived, fixed graph. This is NOT sample-specific edge inference.
    a_center=a-a.mean(axis=0);sd=np.sqrt(np.sum(a_center*a_center,axis=0));norm=a_center/np.maximum(sd,1e-8)
    corr=norm.T@norm;np.fill_diagonal(corr,0)
    k=min(5,max(0,a.shape[1]-1));W=np.zeros_like(corr)
    if k:
        for i in range(corr.shape[0]):
            ix=np.argsort(-np.abs(corr[i]))[:k];W[i,ix]=corr[i,ix]
    W=W/np.maximum(np.abs(W).sum(axis=1,keepdims=True),1e-8)
    an=a@W.T;bn=b@W.T
    if kind=='network':return an,bn
    if kind=='combined':return np.column_stack([a,an]),np.column_stack([b,bn])
    raise ValueError(kind)

def fit_predict(A,y,B,kind,C=0.1):
    a,b=transform(A,B,kind);sc=StandardScaler();a=sc.fit_transform(a);b=sc.transform(b)
    m=LogisticRegression(C=C,max_iter=1500,solver='liblinear',random_state=SEED)
    m.fit(a,y);return m.predict_proba(b)[:,1]

def choose_c(X,y,coh,kind):
    # Inner validation on the two available source cohorts; no outer cohort labels used.
    candidates=[0.001,0.01,0.1,1.0]
    scores=[]
    for C in candidates:
        fold=[]
        for held in np.unique(coh):
            tr=coh!=held;te=~tr
            if len(np.unique(y[tr]))!=2 or len(np.unique(y[te]))!=2:continue
            p=fit_predict(X[tr],y[tr],X[te],kind,C)
            fold.append(roc_auc_score(y[te],p))
        scores.append(float(np.mean(fold)) if fold else -1)
    return candidates[int(np.argmax(scores))]

def cluster_auc_ci(y,p,groups,seed,n=1200):
    rng=np.random.default_rng(seed);u=np.unique(groups);lookup={g:np.flatnonzero(groups==g) for g in u};vals=[]
    for _ in range(n):
        samp=rng.choice(u,size=len(u),replace=True);idx=np.concatenate([lookup[g] for g in samp])
        if len(np.unique(y[idx]))==2:vals.append(roc_auc_score(y[idx],p[idx]))
    return tuple(np.quantile(vals,[.025,.975])) if vals else (np.nan,np.nan)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--train-dir',type=pathlib.Path,required=True);parser.add_argument('--out-dir',type=pathlib.Path,required=True)
    args=parser.parse_args();args.out_dir.mkdir(parents=True,exist_ok=True)
    X,y,coh,groups,meta,names,stats=read(args.train_dir)
    results=[]; preds=[]; details={'input':stats,'seed':SEED,'features':len(names),'selected_C':{}}
    rng=np.random.default_rng(SEED)
    for held in COHORTS:
        tr=coh!=held;te=~tr; details['selected_C'][held]={}
        for kind in ('abundance','network','combined'):
            C=choose_c(X[tr],y[tr],coh[tr],kind);details['selected_C'][held][kind]=C
            p=fit_predict(X[tr],y[tr],X[te],kind,C)
            auc=roc_auc_score(y[te],p);lo,hi=cluster_auc_ci(y[te],p,groups[te],SEED+COHORTS.index(held))
            results.append(dict(cohort=held,model=kind,n_test=int(te.sum()),n_asd=int(y[te].sum()),auc=auc,ci95_low=lo,ci95_high=hi,split='leave-one-cohort-out',note='cluster bootstrap by sibling_pair'))
            preds.extend([dict(sample_id=i,cohort=held,model=kind,actual=int(yy),score=float(pp)) for i,yy,pp in zip(np.array(sum([list(pd.read_csv((args.train_dir/c/'labels.tsv') if (args.train_dir/c/'labels.tsv').exists() else (args.train_dir/f'{c}_labels.tsv'),sep='\t').sample_id) for c in COHORTS],[]))[te],y[te],p)])
        # Permutation null: shuffle labels WITHIN source cohort, re-fit; preserve cohort case balance;
        # permute David as entire sibling-pair label vector assignments to retain paired structure.
        null_aucs=[]
        for i in range(60):
            yp=y[tr].copy();co=coh[tr];gr=groups[tr]
            for source in np.unique(co):
                ix=np.flatnonzero(co==source)
                if source=='david':
                    # paired siblings: exchange the ASD/control assignment inside each pair with p=.5
                    for g in np.unique(gr[ix]):
                        j=ix[gr[ix]==g]
                        if len(j)==2 and yp[j].sum()==1 and rng.random()<.5:yp[j]=yp[j][::-1]
                    # residual unpaired child statuses are independently shuffled
                    singleton=np.array([j for j in ix if np.sum(gr[ix]==gr[j])==1]);
                    if len(singleton)>1:yp[singleton]=rng.permutation(yp[singleton])
                else:yp[ix]=rng.permutation(yp[ix])
            if len(np.unique(yp))<2:continue
            p=fit_predict(X[tr],yp,X[te],'abundance',0.1)
            null_aucs.append(roc_auc_score(y[te],p))
        results.append(dict(cohort=held,model='permuted_labels_abundance',n_test=int(te.sum()),n_asd=int(y[te].sum()),auc=float(np.mean(null_aucs)),ci95_low=float(np.quantile(null_aucs,.025)),ci95_high=float(np.quantile(null_aucs,.975)),split='leave-one-cohort-out',note='60 repeats; interval across permutations, not bootstrap CI'))
        if held=='david':
            # Honest metadata-only baseline: training cohorts have NO age or sex. Cannot train cross-cohort.
            results.append(dict(cohort=held,model='metadata_only',n_test=int(te.sum()),n_asd=int(y[te].sum()),auc=np.nan,ci95_low=np.nan,ci95_high=np.nan,split='leave-one-cohort-out',note='not estimable: both source cohorts missing sex and age'))
        else:
            results.append(dict(cohort=held,model='metadata_only',n_test=int(te.sum()),n_asd=int(y[te].sum()),auc=np.nan,ci95_low=np.nan,ci95_high=np.nan,split='leave-one-cohort-out',note='not estimable: target cohort missing sex and age'))
        # label-prior baseline predicts a constant for all target cases: AUC 0.5.
        results.append(dict(cohort=held,model='source_label_prevalence_constant',n_test=int(te.sum()),n_asd=int(y[te].sum()),auc=0.5,ci95_low=0.5,ci95_high=0.5,split='leave-one-cohort-out',note='constant score; trivially chance AUC'))
    pd.DataFrame(results).to_csv(args.out_dir/'loco_results.csv',index=False)
    pd.DataFrame(preds).to_csv(args.out_dir/'oof_predictions.csv',index=False)
    (args.out_dir/'run_details.json').write_text(json.dumps(details,indent=2))
    print(pd.DataFrame(results).to_string(index=False)); print(json.dumps(details,indent=2))
if __name__=='__main__':main()
