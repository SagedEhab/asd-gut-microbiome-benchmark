#!/usr/bin/env python3
"""Round 2: reproducible training-only ASD 16S benchmark (no external holdout labels)."""
import argparse, json, re, pathlib, time
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from scipy.stats import spearmanr

COHORTS=['ding','zou','david']; GRID=[.001,.01,.1,1.]; SEED=20261112; KINDS=['abundance','network','combined']

def load(root,key='family_genus'):
    tables=[]; labs=[]; stats={}; tech=[]
    for c in COHORTS:
        base=root/c; a=pd.read_csv(base/'genus_counts.tsv',sep='\t',index_col='sample_id');b=pd.read_csv(base/'labels.tsv',sep='\t',index_col='sample_id');a=a.loc[b.index]
        assert a.index.is_unique and b.index.is_unique and (a.values>=0).all() and a.index.equals(b.index)
        depth=a.sum(axis=1).values
        keys={}; unassigned=[]
        for col in a:
            gm=re.search(r'(?:^|;)g__([^;]+)$',col); fm=re.search(r'(?:^|;)f__([^;]+)',col)
            if gm is None or not gm.group(1).strip('_ '): unassigned.append(col);continue
            g=gm.group(1).strip().lower(); f=fm.group(1).strip().lower() if fm else 'unknown'
            label=g if key=='genus' else f+'|'+g
            keys.setdefault(label,[]).append(col)
        z=pd.DataFrame({k:a[v].sum(axis=1) for k,v in keys.items()},index=a.index)
        tables.append(z); b=b.copy();b['cohort']=c;b['depth']=depth;b['richness']=(z>0).sum(axis=1).values;b['pair_id']=np.where(c=='david',c+':'+b.get('sibling_pair',pd.Series(b.index,index=b.index)).astype(str),c+':'+b.index.astype(str));labs.append(b)
        stats[c]={'n':len(b),'asd':int((b.diagnosis=='ASD').sum()),'genera':len(keys),'unassigned_columns':len(unassigned),'unassigned_read_fraction':float(a[unassigned].sum().sum()/a.sum().sum()) if unassigned else 0}
    X=pd.concat(tables).fillna(0); M=pd.concat(labs);assert X.index.equals(M.index)
    return X.to_numpy(float),M,X.columns.tolist(),stats

def feature(A,B,kind):
    prev=(A>0).mean(axis=0)>=.10
    if not prev.any():prev[:]=True
    A=A[:,prev];B=B[:,prev]
    a=np.log(A+.5); b=np.log(B+.5); a-=a.mean(axis=1,keepdims=True);b-=b.mean(axis=1,keepdims=True)
    if kind=='abundance':return a,b
    ac=a-a.mean(axis=0); norms=np.sqrt((ac**2).sum(axis=0)); z=ac/np.maximum(norms,1e-10)
    corr=z.T@z;np.fill_diagonal(corr,0);W=np.zeros_like(corr); k=min(5,len(corr)-1)
    if k>0:
        ix=np.argsort(-np.abs(corr),axis=1)[:,:k]
        W[np.arange(len(corr))[:,None],ix]=corr[np.arange(len(corr))[:,None],ix]
    W/=np.maximum(np.abs(W).sum(axis=1,keepdims=True),1e-10)
    an=a@W.T;bn=b@W.T
    if kind=='network':return an,bn
    if kind=='combined':return np.concatenate((a,an),axis=1),np.concatenate((b,bn),axis=1)
    raise ValueError(kind)

def getfold(X, tr,te,kind):
    a,b=feature(X[tr],X[te],kind) if kind in KINDS else (X[tr],X[te])
    z=StandardScaler().fit(a);return z.transform(a),z.transform(b)

def pred(a,y,b,C):
    mod=LogisticRegression(C=C,max_iter=500,solver='liblinear',random_state=SEED)
    mod.fit(a,y);return mod.predict_proba(b)[:,1]

def auc(y,p):return float(roc_auc_score(y,p)) if len(set(y))==2 else np.nan

def ci(y,p,g,seed,n=600):
    rng=np.random.default_rng(seed); un=np.unique(g);lookup={k:np.flatnonzero(g==k) for k in un};values=[]
    for _ in range(n):
        idx=np.concatenate([lookup[k] for k in rng.choice(un,size=len(un),replace=True)])
        if len(set(y[idx]))>1: values.append(auc(y[idx],p[idx]))
    return np.quantile(values,[.025,.975]) if values else [np.nan,np.nan]

def permute_source(y,coh,g,rng):
    yp=y.copy()
    for s in np.unique(coh):
        ix=np.flatnonzero(coh==s)
        if s=='david':
            for group in np.unique(g[ix]):
                j=ix[g[ix]==group]
                if len(j)==2 and yp[j].sum()==1 and rng.random()<.5: yp[j]=yp[j][::-1]
            singles=np.array([j for j in ix if np.count_nonzero(g[ix]==g[j])==1],dtype=int)
            if len(singles)>1:yp[singles]=rng.permutation(yp[singles])
        else: yp[ix]=rng.permutation(yp[ix])
    return yp

def evaluate(root,out,nperm=200,only_cohort=None,only_key=None):
    out.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(SEED)
    allrows=[]; sens=[]; oof=[]; diagnostics={}; family_result={}; comparison=[]
    for key in ([only_key] if only_key else ['family_genus','genus']):
        X,M,names,stats=load(root,key); y=(M.diagnosis=='ASD').to_numpy(dtype=int);coh=M.cohort.to_numpy();g=M.pair_id.to_numpy();ids=M.index.to_numpy();
        family_result[key]=stats
        for held in ([only_cohort] if only_cohort else COHORTS):
            rng=np.random.default_rng(SEED) # independent per-held-cohort permutation stream
            tr=np.flatnonzero(coh!=held);te=np.flatnonzero(coh==held)
            for kind in KINDS:
                outer=getfold(X,tr,te,kind)
                sources=np.unique(coh[tr]);inner=[]
                for source in sources:
                    it=tr[coh[tr]!=source];iv=tr[coh[tr]==source]
                    inner.append((getfold(X,it,iv,kind),it,iv))
                def choose(labels):
                    means=[]
                    for C in GRID:
                        vals=[auc(labels[np.searchsorted(tr,iv)],pred(ab[0],labels[np.searchsorted(tr,it)],ab[1],C)) for ab,it,iv in inner]
                        means.append(np.mean(vals))
                    return int(np.argmax(means))
                # tr sorted so searchsorted works
                selected_idx=choose(y[tr]);selectedC=GRID[selected_idx]
                pp={C:pred(outer[0],y[tr],outer[1],C) for C in GRID}
                for C,p in pp.items():sens.append(dict(key=key,cohort=held,model=kind,C=C,auc=auc(y[te],p),chosen_by_inner=C==selectedC,headline=(key=='family_genus' and kind=='abundance' and C==.01)))
                p=pp[selectedC];value=auc(y[te],p);lo,hi=ci(y[te],p,g[te],SEED+((len(sens)-1)%12+1),400)
                null=[]
                for _ in range(nperm):
                    yy=permute_source(y[tr],coh[tr],g[tr],rng);j=choose(yy);score=pred(outer[0],yy,outer[1],GRID[j]);null.append(auc(y[te],score))
                raw=(1+np.sum(np.asarray(null)>=value))/(len(null)+1) if null else np.nan
                allrows.append(dict(key=key,cohort=held,model=kind,setting='nested_C',C=selectedC,n_test=len(te),auc=value,ci_low=lo,ci_high=hi,null_mean=np.mean(null) if null else np.nan,null_low=np.quantile(null,.025) if null else np.nan,null_high=np.quantile(null,.975) if null else np.nan,p_raw=raw,permutations=len(null)))
                if key=='family_genus':
                    for i,pv in zip(te,p):oof.append(dict(sample_id=ids[i],cohort=held,model=kind,y=int(y[i]),score=float(pv),pair_id=g[i]))
                if kind=='abundance' and key=='family_genus':
                    p0=pp[.01];v0=auc(y[te],p0);l0,h0=ci(y[te],p0,g[te],SEED+((len(sens)-1)%12+1),400)
                    n0=[]
                    for _ in range(nperm):
                        yy=permute_source(y[tr],coh[tr],g[tr],rng);n0.append(auc(y[te],pred(outer[0],yy,outer[1],.01)))
                    allrows.append(dict(key=key,cohort=held,model=kind,setting='prespecified_C_0.01',C=.01,n_test=len(te),auc=v0,ci_low=l0,ci_high=h0,null_mean=np.mean(n0),null_low=np.quantile(n0,.025),null_high=np.quantile(n0,.975),p_raw=(1+np.sum(np.array(n0)>=v0))/(nperm+1),permutations=nperm))
                print(key,held,kind,'AUC',round(value,3),'C',selectedC,'p',round(raw,3),flush=True)
            if key=='family_genus':
                z=np.column_stack([np.log10(M.depth.to_numpy()+1),M.richness.to_numpy()]);
                for k,ix in [('depth_only',0),('richness_only',1)]:
                    A,B=getfold(z[:,ix:ix+1],tr,te,'technical');p=pred(A,y[tr],B,.01)
                    l,h=ci(y[te],p,g[te],SEED+ix,400)
                    allrows.append(dict(key=key,cohort=held,model=k,setting='fixed_C_0.01',C=.01,n_test=len(te),auc=auc(y[te],p),ci_low=l,ci_high=h,null_mean=np.nan,null_low=np.nan,null_high=np.nan,p_raw=np.nan,permutations=0))
                depths=M.depth.to_numpy();asd=depths[te][y[te]==1];ctl=depths[te][y[te]==0]
                diagnostics[held]={'median_depth_ASD':float(np.median(asd)),'median_depth_control':float(np.median(ctl)),'depth_auc_direct':auc(y[te],-depths[te]),'richness_auc_direct':auc(y[te],M.richness.to_numpy()[te])}
    # Holm on the nine nested_C family+genus contrasts (prespecified headline separately identified).
    df=pd.DataFrame(allrows);mask=(df.key=='family_genus')&(df.setting=='nested_C')&(df.model.isin(KINDS)); ps=df.loc[mask,'p_raw'].values;m=len(ps);order=np.argsort(ps);adj=np.empty(m);running=0
    for rank,j in enumerate(order):running=max(running,(m-rank)*ps[j]);adj[j]=min(1.,running)
    df.loc[mask,'p_holm_nine']=adj
    headline=df[(df.key=='family_genus')&(df.setting=='prespecified_C_0.01')];ps2=headline.p_raw.values;order=np.argsort(ps2);adj2=np.empty(len(ps2));running=0
    for rank,j in enumerate(order):running=max(running,(len(ps2)-rank)*ps2[j]);adj2[j]=min(1,running)
    df.loc[headline.index,'p_holm_three_headline']=adj2
    df.to_csv(out/'loco_results.csv',index=False);pd.DataFrame(sens).to_csv(out/'regularization_sensitivity.csv',index=False);pd.DataFrame(oof).to_csv(out/'oof_predictions.csv',index=False)
    # David grouped CV: perform COMPLETE-case comparisons on identical groups and 5 folds, no missing-sex indicator.
    X,M,_,_=load(root,'family_genus');d=M.cohort=='david';good=d&M.sex.isin(['m','f'])&M.age.notna();idx=np.flatnonzero(good.to_numpy());yd=(M.diagnosis=='ASD').to_numpy(dtype=int)[idx];groups=M.pair_id.to_numpy()[idx];sex=(M.sex.to_numpy()[idx]=='m').astype(float);age=M.age.to_numpy(dtype=float)[idx];met=np.column_stack((sex,age));
    splitter=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=SEED);outrows=[];pred_rows=[]
    for kind in ['metadata_only','abundance','combined','microbiome_plus_metadata']:
        scores=np.full(len(idx),np.nan)
        for itr,ite in splitter.split(X[idx],yd,groups):
            Xtr=X[idx][itr];Xte=X[idx][ite];
            if kind=='metadata_only':a,b=met[itr],met[ite]
            elif kind=='microbiome_plus_metadata':a,b=feature(Xtr,Xte,'abundance');a=np.column_stack((a,met[itr]));b=np.column_stack((b,met[ite]))
            else:a,b=feature(Xtr,Xte,kind)
            sc=StandardScaler().fit(a);scores[ite]=pred(sc.transform(a),yd[itr],sc.transform(b),.01)
        val=auc(yd,scores);lo,hi=ci(yd,scores,groups,SEED+8,1000)
        pairs=[]
        for g0 in np.unique(groups):
            pair=np.flatnonzero(groups==g0)
            if len(pair)==2 and yd[pair].sum()==1:
                pairs.append(float(scores[pair[yd[pair]==1][0]]>scores[pair[yd[pair]==0][0]]))
        outrows.append(dict(model=kind,n=len(idx),auc=val,ci_low=lo,ci_high=hi,discordant_pairs=len(pairs),fraction_asd_higher=np.mean(pairs) if pairs else np.nan,folds=5,C=.01))
        for i,pv in enumerate(scores):pred_rows.append(dict(sample_id=M.index[idx[i]],model=kind,score=pv,y=yd[i],pair=groups[i]))
    pd.DataFrame(outrows).to_csv(out/'david_grouped_results.csv',index=False);pd.DataFrame(pred_rows).to_csv(out/'david_grouped_scores.csv',index=False)
    # depth-matched cohort subsets (post-hoc descriptive diagnostic; not training selection).
    ptable=pd.DataFrame(oof); depthmatched=[]
    for held in COHORTS if len(ptable) else []:
        dd=M[M.cohort==held]; y0=(dd.diagnosis=='ASD').astype(int).to_numpy();depth0=dd.depth.to_numpy();
        # paired greedy nearest-depth matching inside held-out dataset, label-used only for evaluation subset definition
        aa=list(np.where(y0==1)[0]);cc=list(np.where(y0==0)[0]); candidates=sorted((abs(np.log(depth0[i])-np.log(depth0[j])),i,j) for i in aa for j in cc)
        usedA=set();usedC=set();kept=[]
        for dist,i,j in candidates:
            if i not in usedA and j not in usedC:
                usedA.add(i);usedC.add(j);kept.extend([i,j])
        samples=set(dd.index.to_numpy()[kept]);
        for kind in KINDS:
            sc=ptable[(ptable.cohort==held)&(ptable.model==kind)&(ptable.sample_id.isin(samples))];depthmatched.append(dict(cohort=held,model=kind,n=len(sc),auc=auc(sc.y.to_numpy(),sc.score.to_numpy()),definition='posthoc depth nearest-neighbor case-control matching, test labels only used for assessment subset'))
    pd.DataFrame(depthmatched).to_csv(out/'depth_match_results.csv',index=False)
    (out/'diagnostics.json').write_text(json.dumps({'harmonization':family_result,'cohort_technical':diagnostics,'permutations':nperm,'seed':SEED,'n_primary_comparisons':9,'n_headline_comparisons':3},indent=2))
    print('DAVID GROUPED',pd.DataFrame(outrows).to_string(index=False),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--train-dir',type=pathlib.Path,required=True);ap.add_argument('--out-dir',type=pathlib.Path,required=True);ap.add_argument('--permutations',type=int,default=200);ap.add_argument('--only-cohort',choices=COHORTS);ap.add_argument('--only-key',choices=['family_genus','genus']);a=ap.parse_args();evaluate(a.train_dir,a.out_dir,a.permutations,a.only_cohort,a.only_key)
