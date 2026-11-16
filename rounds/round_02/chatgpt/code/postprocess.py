#!/usr/bin/env python3
"""Derive outcome-blind technical summaries and evaluation-only matching analyses."""
import argparse,pathlib,numpy as np,pandas as pd
from scipy.stats import spearmanr
from run import load,auc,COHORTS,KINDS
p=argparse.ArgumentParser();p.add_argument('--train-dir',type=pathlib.Path,required=True);p.add_argument('--out-dir',type=pathlib.Path,required=True);a=p.parse_args()
X,M,_,stats=load(a.train_dir,'family_genus');P=pd.read_csv(a.out_dir/'oof_predictions.csv');match=[];pairresults=[];corr=[];diagnostics=[]
for held in COHORTS:
 d=M[M.cohort==held];y=(d.diagnosis=='ASD').astype(int).to_numpy();depth=d.depth.to_numpy(); aa=list(np.flatnonzero(y==1));cc=list(np.flatnonzero(y==0));edges=sorted((abs(np.log(depth[i])-np.log(depth[j])),i,j) for i in aa for j in cc); usedA=set();usedC=set(); selected=[];gaps=[]
 for dist,i,j in edges:
  if i not in usedA and j not in usedC: usedA.add(i);usedC.add(j);selected.extend([i,j]);gaps.append(dist)
 samples=set(d.index.to_numpy()[selected])
 for model in KINDS:
  scores=P[(P.cohort==held)&(P.model==model)].set_index('sample_id').loc[d.index]
  subs=scores.loc[list(samples)]
  match.append(dict(cohort=held,model=model,n_test_matched=len(subs),auc_matched=auc(subs.y.to_numpy(),subs.score.to_numpy()),median_abs_log_depth_gap=float(np.median(gaps))))
  if held=='david':
   pairs=[]
   for group,s in scores.groupby('pair_id'):
    if len(s)==2 and s.y.sum()==1:pairs.append(float(s.loc[s.y==1,'score'].iloc[0]>s.loc[s.y==0,'score'].iloc[0]))
   pairresults.append(dict(model=model,discordant_pairs=len(pairs),asd_higher_n=int(sum(pairs)),asd_higher_fraction=np.mean(pairs)))
  c=spearmanr(scores.score.to_numpy(),depth)
  corr.append(dict(cohort=held,model=model,score_depth_spearman=float(c.statistic),p_spearman=float(c.pvalue)))
 diagnostics.append(dict(cohort=held,**stats[held],median_ASD=float(np.median(depth[y==1])),median_control=float(np.median(depth[y==0])),depth_direct_lower_asd_auc=auc(y,-depth)))
pd.DataFrame(match).to_csv(a.out_dir/'depth_match_results.csv',index=False);pd.DataFrame(pairresults).to_csv(a.out_dir/'loco_sibling_concordance.csv',index=False);pd.DataFrame(corr).to_csv(a.out_dir/'score_depth_correlation.csv',index=False);pd.DataFrame(diagnostics).to_csv(a.out_dir/'diagnostics.csv',index=False)
df=pd.read_csv(a.out_dir/'loco_results.csv');mask=(df.setting=='nested_C')&df.model.isin(KINDS);ps=df.loc[mask,'p_raw'].to_numpy();order=np.argsort(ps);adjust=np.zeros(len(ps));maxp=0
for rank,j in enumerate(order):maxp=max(maxp,(len(ps)-rank)*ps[j]);adjust[j]=min(1,maxp)
df.loc[mask,'p_holm_eighteen']=adjust;df.to_csv(a.out_dir/'loco_results.csv',index=False)

# Very conservative family-wise view spanning *all* 31 inferential tests:
# 18 nested microbial (both mappings), 3 headline, 6 technical, 4 David grouped.
controls_file=a.out_dir/'technical_metadata_null.csv'
if controls_file.exists():
    ctrl=pd.read_csv(controls_file)
    tested=df[(df.setting=='nested_C') | (df.setting=='prespecified_C_0.01')]
    vals=np.concatenate([tested.p_raw.to_numpy(),ctrl.p_raw.to_numpy()]);order=np.argsort(vals);adjust=np.zeros(len(vals));m=len(vals);running=0.
    for rank,j in enumerate(order):running=max(running,(m-rank)*vals[j]);adjust[j]=min(1.,running)
    df.loc[tested.index,'p_holm_all_31']=adjust[:len(tested)]
    ctrl['p_holm_all_31']=adjust[len(tested):]
    df.to_csv(a.out_dir/'loco_results.csv',index=False)
    ctrl.to_csv(controls_file,index=False)
