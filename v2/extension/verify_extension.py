"""Independent scalar-loop spot checks of new trajectories; no runner import."""
import csv, hashlib, json, math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
cfg=json.loads((ROOT/'config.json').read_text())
out=ROOT/'results'
with (out/'run_metrics.csv').open() as f:rows=list(csv.DictReader(f))
theta_world=np.load((ROOT/cfg['original_results_relative']).resolve()/'world_parameters.npz')['theta']
cases=[('main_extension','sigmoid','endogenous','world_optimum',10,3,3.),
       ('main_extension','sigmoid','ipw_omit_friction','world_optimum',0,0,3.),
       ('main_extension','matched_exponential','ipw_true','world_optimum',11,2,3.),
       ('main_extension','matched_exponential','ipw_half_sensitivity','world_optimum',5,4,3.),
       ('exact_symmetric','sigmoid','endogenous','0.75',0,7,8.),
       ('exact_symmetric','sigmoid','endogenous','0.0',0,9,3.)]

def probs(w,th,c,b,fam):
    ps=[]
    for g in range(3):
        loss=(w-th[g])**2+.2**2/3
        if fam=='sigmoid':v=1/(1+math.exp(-(2-c[g]-b*loss)))
        else:
            intercept=1/(1+math.exp(-(2-c[g])))
            v=intercept*math.exp(-b*(1-intercept)*loss)
        ps.append(.02+.96*v)
    return ps

records=[]
for block,fam,cond,init,wi,seed,b in cases:
    ismain=block=='main_extension';th=theta_world[wi].tolist() if ismain else [-1.,0.,1.]
    c=[1.2,0.,0.] if ismain else [0.,0.,0.]
    w=sum(th)/3 if ismain else float(init)
    trainseed=cfg['main' if ismain else 'symmetric']['training_seed']
    rng=np.random.default_rng(np.random.SeedSequence([trainseed,wi,seed]))
    u=rng.random((1000,96));eps=rng.uniform(-.2,.2,(1000,96))
    acc=np.zeros(7)
    for t in range(1000):
        p=probs(w,th,c,b,fam);q=[a/sum(p) for a in p]
        groups=[0 if v<q[0] else (1 if v<q[0]+q[1] else 2) for v in u[t]]
        ys=[th[g]+float(eps[t,j]) for j,g in enumerate(groups)]
        if cond.startswith('ipw'):
            c_hat=[0.,0.,0.] if cond=='ipw_omit_friction' else c
            b_hat=b/2 if cond=='ipw_half_sensitivity' else b
            phat=probs(w,th,c_hat,b_hat,fam)
            weights=[1/phat[g] for g in groups]
            est=sum(y*a for y,a in zip(ys,weights))/sum(weights)
        else:est=sum(ys)/96
        if t>=950:
            losses=[(w-a)**2+.2**2/3 for a in th]
            pop=sum(losses)/3;monitor=sum(a*d for a,d in zip(losses,q))
            acc+=np.array(losses+[(w-sum(th)/3)**2,w,pop,monitor])/50
        w=.95*w+.05*est
    target=next(r for r in rows if r['block']==block and r['family']==fam and r['condition']==cond and r['init_label']==init and int(r['world'])==wi and int(r['seed'])==seed and float(r['strength_anchor'])==b)
    names=['g0_loss','g1_loss','g2_loss','population_regret','action','population_loss','monitoring_loss']
    errors={k:abs(float(target[k])-float(v)) for k,v in zip(names,acc)};errors['final_action']=abs(float(target['final_action'])-w)
    records.append({'case':list((block,fam,cond,init,wi,seed,b)),'errors':errors,'max_error':max(errors.values())})
maxerr=max(r['max_error'] for r in records)
assert maxerr<1e-9,maxerr
assert len(rows)==4500
quota={}
for r in rows:
    assert 0<float(r['effective_sample_size'])<=96+1e-10
    assert abs(sum(float(r[f'g{g}_realized_share']) for g in range(3))-1)<1e-12
    assert abs(sum(float(r[f'g{g}_expected_share']) for g in range(3))-1)<1e-12
    assert float(r['cumulative_realized_invites'])>=1000*96
    if r['condition']=='quota':
        for g in range(3):assert abs(float(r[f'g{g}_realized_share'])-1/3)<1e-12
        key=(r['world'],r['seed']);state=[float(r[k]) for k in ['final_action','population_regret','g0_loss','g1_loss','g2_loss']]
        if key in quota:assert quota[key]==state
        else:quota[key]=state
record={'status':'passed','method':'Six scalar-loop reruns without importing simulation runner; all-run support/share/ESS/cost-count invariants; exact quota cross-law state equality',
        'selected_trajectories':records,'max_scalar_discrepancy':maxerr,'run_count':len(rows),
        'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope':'Spot checks and invariants, not an independent rerun of every stochastic trajectory or empirical validation'}
(ROOT/'verification.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))
