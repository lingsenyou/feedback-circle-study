"""Post-hoc exploratory extension; NumPy only; original study is read-only."""
from __future__ import annotations
import argparse, csv, hashlib, json, math, platform, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
METRICS = ['g0_loss','g1_loss','g2_loss','population_regret','population_loss',
           'monitoring_loss','monitoring_gap','action','g0_expected_share',
           'g1_expected_share','g2_expected_share','g0_realized_share','g1_realized_share',
           'g2_realized_share','effective_sample_size','expected_invites_per_accepted',
           'realized_invites_per_accepted']

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p,x): Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def readcsv(p):
    with Path(p).open(newline='',encoding='utf-8') as f: return list(csv.DictReader(f))
def csvout(p,rows):
    if not rows: raise ValueError('Empty result table')
    with Path(p).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def sigmoid(z): return 1/(1+np.exp(-np.clip(z,-700,700)))

def participation(w,theta,c,b,family,cfg,derivative=False):
    loss=(w[...,None]-theta)**2+cfg['noise_halfwidth']**2/3
    a=sigmoid(cfg['participation_intercept']-c)
    if family=='sigmoid':
        s=sigmoid(cfg['participation_intercept']-c-b*loss)
        p=cfg['participation_floor']+cfg['participation_span']*s
        dp=-2*b*cfg['participation_span']*s*(1-s)*(w[...,None]-theta)
    elif family=='matched_exponential':
        k=b*(1-a); e=a*np.exp(-k*loss)
        p=cfg['participation_floor']+cfg['participation_span']*e
        dp=-2*k*cfg['participation_span']*e*(w[...,None]-theta)
    else: raise ValueError(family)
    return (p,dp) if derivative else p

def meanmap(w,theta,c,b,family,cfg):
    p=participation(np.asarray(w),theta,c,b,family,cfg)
    return (p*theta).sum(axis=-1)/p.sum(axis=-1)

def fixedpoints(theta,c,b,family,cfg):
    x=np.linspace(float(min(theta)),float(max(theta)),cfg['root_grid_points'])
    y=meanmap(x,theta,c,b,family,cfg)-x
    roots=[]
    for j in range(len(x)-1):
        if abs(y[j])<1e-12: roots.append(float(x[j]))
        if y[j]*y[j+1]<0:
            lo,hi=float(x[j]),float(x[j+1]);flo=float(y[j])
            for _ in range(65):
                mid=(lo+hi)/2;fm=float(meanmap(mid,theta,c,b,family,cfg)-mid)
                if flo*fm<=0:hi=mid
                else:lo=mid;flo=fm
            roots.append((lo+hi)/2)
    if abs(y[-1])<1e-12:roots.append(float(x[-1]))
    unique=[]
    for r in sorted(roots):
        if not unique or abs(r-unique[-1])>1e-8:unique.append(r)
    result=[]
    for r in unique:
        p,dp=participation(np.asarray(r),theta,c,b,family,cfg,True)
        mp=float(((dp*theta).sum()*p.sum()-(p*theta).sum()*dp.sum())/p.sum()**2)
        slope=1-cfg['learning_rate']+cfg['learning_rate']*mp
        h=1e-6;fd=float((meanmap(r+h,theta,c,b,family,cfg)-meanmap(r-h,theta,c,b,family,cfg))/(2*h))
        result.append({'root':r,'mean_derivative':mp,'update_derivative':slope,
                       'locally_stable':bool(abs(slope)<1),'finite_difference_error':abs(mp-fd)})
    return result

def deterministic(theta,c,b,family,w0,cfg,tag):
    w=float(w0);rows=[];a=cfg['learning_rate'];v=cfg['noise_halfwidth']**2/3
    for t in range(cfg['deterministic_rounds']+1):
        if t%cfg['trajectory_every']==0:
            losses=(w-theta)**2+v;p=participation(np.asarray(w),theta,c,b,family,cfg)
            rows.append({**tag,'completed_updates':t,'action':w,'g0_loss':float(losses[0]),
                         'g1_loss':float(losses[1]),'g2_loss':float(losses[2]),
                         'population_regret':float((w-theta.mean())**2),
                         'g0_expected_share':float(p[0]/p.sum())})
        if t<cfg['deterministic_rounds']:w=(1-a)*w+a*float(meanmap(w,theta,c,b,family,cfg))
    return rows,w

def draw_arrays(W,S,T,B,seed,h):
    u=np.empty((W*S,T,B));noise=np.empty_like(u)
    for j in range(W*S):
        rng=np.random.default_rng(np.random.SeedSequence([seed,j//S,j%S]))
        u[j]=rng.random((T,B));noise[j]=rng.uniform(-h,h,(T,B))
    return u,noise

def simulate(theta_world,S,c,b,family,condition,w0,draws,noise,cfg,case_id,tag,checks):
    W=len(theta_world);R=W*S;T=cfg['rounds'];B=cfg['batch_size'];a=cfg['learning_rate']
    theta=np.repeat(theta_world,S,axis=0);row=np.arange(R)[:,None]
    initial=np.repeat(np.broadcast_to(w0,(W,)),S).astype(float);w=initial.copy()
    p0=participation(w,theta,c,b,family,cfg);var=cfg['noise_halfwidth']**2/3
    quota=np.broadcast_to(np.repeat(np.arange(3),B//3),(R,B))
    costrng=np.random.default_rng(np.random.SeedSequence([cfg['invitation_seed'],case_id]))
    totals=np.zeros((R,len(METRICS)));cumexp=np.zeros(R);cumactual=np.zeros(R);cumvar=np.zeros(R)
    trajectories=[]
    for t in range(T):
        p=participation(w,theta,c,b,family,cfg)
        if condition=='static':p=p0
        q=p/p.sum(axis=1,keepdims=True)
        checks['probability_max_sum_error']=max(checks['probability_max_sum_error'],float(abs(q.sum(axis=1)-1).max()))
        if not np.all((p>0)&(p<=1)&np.isfinite(p)):raise AssertionError('Invalid propensity')
        if condition=='quota':
            groups=quota;qobs=np.full_like(q,1/3)
            expected=(B/3/p).sum(axis=1);vv=(B/3*(1-p)/p**2).sum(axis=1)
            actual=(B/3+costrng.negative_binomial(B//3,p)).sum(axis=1)
        else:
            groups=(draws[:,t]>=q[:,0,None]).astype(np.int8)+(draws[:,t]>=(q[:,0]+q[:,1])[:,None]).astype(np.int8)
            qobs=q;ps=p.mean(axis=1);expected=B/ps;vv=B*(1-ps)/ps**2
            actual=B+costrng.negative_binomial(B,ps)
        if np.any(actual<B):raise AssertionError('Invitations below successes')
        y=theta[row,groups]+noise[:,t]
        weights=np.ones_like(y)
        if condition.startswith('ipw'):
            chat=np.zeros_like(c) if condition=='ipw_omit_friction' else c
            bhat=b/2 if condition=='ipw_half_sensitivity' else b
            phat=participation(w,theta,chat,bhat,family,cfg)
            weights=1/phat[row,groups]
            estimate=(weights*y).sum(axis=1)/weights.sum(axis=1)
            if condition=='ipw_true':
                target=(q*(1/p)*theta).sum(axis=1)/(q*(1/p)).sum(axis=1)
                checks['true_ipw_moment_max_error']=max(checks['true_ipw_moment_max_error'],float(abs(target-theta.mean(axis=1)).max()))
        else:estimate=y.mean(axis=1)
        losses=(w[:,None]-theta)**2+var;pop=losses.mean(axis=1);regret=(w-theta.mean(axis=1))**2
        oracle=((theta-theta.mean(axis=1,keepdims=True))**2).mean(axis=1)+var
        checks['risk_decomposition_max_error']=max(checks['risk_decomposition_max_error'],float(abs(pop-oracle-regret).max()))
        monitoring=(qobs*losses).sum(axis=1)
        realshares=np.column_stack([(groups==g).mean(axis=1) for g in range(3)])
        ess=weights.sum(axis=1)**2/(weights**2).sum(axis=1)
        values=np.column_stack([losses,regret,pop,monitoring,pop-monitoring,w,qobs,realshares,ess,expected/B,actual/B])
        if t>=T-cfg['endpoint_last_rounds']:totals+=values/cfg['endpoint_last_rounds']
        if t%cfg['trajectory_every']==0:
            wm=values.reshape(W,S,-1).mean(axis=1)
            for world in range(W):trajectories.append({**tag,'world':world,'completed_updates':t,**dict(zip(METRICS,wm[world].tolist()))})
        cumexp+=expected;cumactual+=actual;cumvar+=vv
        w=(1-a)*w+a*estimate
    runrows=[];worldrows=[]
    for j in range(R):
        runrows.append({**tag,'world':j//S,'seed':j%S,**dict(zip(METRICS,totals[j].tolist())),
                        'initial_action':float(initial[j]),'final_action':float(w[j]),
                        'cumulative_expected_invites':float(cumexp[j]),'cumulative_realized_invites':int(cumactual[j]),
                        'cumulative_invite_variance':float(cumvar[j])})
    wm=totals.reshape(W,S,-1).mean(axis=1)
    for world in range(W):worldrows.append({**tag,'world':world,**dict(zip(METRICS,wm[world].tolist()))})
    costz=float((cumactual.sum()-cumexp.sum())/np.sqrt(cumvar.sum()))
    cost={'case_id':case_id,**tag,'expected_total_invites':float(cumexp.sum()),'actual_total_invites':int(cumactual.sum()),
          'conditional_variance_total':float(cumvar.sum()),'standardized_difference':costz,
          'ratio_actual_to_expected':float(cumactual.sum()/cumexp.sum())}
    return runrows,worldrows,trajectories,wm,cost

def boot(x,idx):
    low,high=np.quantile(x[idx].mean(axis=1),[.025,.975]);return float(x.mean()),float(low),float(high)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'results');args=parser.parse_args()
    cfg=json.loads((ROOT/'config.json').read_text());out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    if (out/'summary.json').exists() or (out/'execution_start.json').exists():raise SystemExit('Refusing to overwrite execution record')
    old=(ROOT/cfg['original_results_relative']).resolve()
    inputs=[old/n for n in ['run_metrics.csv','world_metrics.csv','trajectories_world.csv','world_parameters.npz','summary.json']]
    frozen={'protocol':sha(ROOT/'PROTOCOL.md'),'config':sha(ROOT/'config.json'),'code':sha(__file__)}
    oldhash={p.name:sha(p) for p in inputs};start=time.perf_counter()
    js(out/'execution_start.json',{'utc':datetime.now(timezone.utc).isoformat(),'status':cfg['status'],
       'frozen_sha256':frozen,'original_input_sha256':oldhash,'python':platform.python_version(),'numpy':np.__version__,'config':cfg})
    checks={'probability_max_sum_error':0.,'true_ipw_moment_max_error':0.,'risk_decomposition_max_error':0.}
    theta=np.load(old/'world_parameters.npz')['theta'];c=np.array(cfg['main']['friction'])
    original=[r for r in readcsv(old/'run_metrics.csv') if r['scenario']=='main' and float(r['beta'])==3 and r['condition'] in ['endogenous','static']]
    keyed={(int(r['world']),int(r['seed']),r['condition']):r for r in original}
    origrun=[];geometry=[];rootrows=[];detrows=[]
    for wi,th in enumerate(theta):
        pair=[]
        for s in range(10):
            e=keyed[(wi,s,'endogenous')];st=keyed[(wi,s,'static')]
            rr={'world':wi,'seed':s}
            for name in ['g0_risk','g1_risk','g2_risk','population_regret','action']:
                rr[name+'_endogenous']=float(e[name]);rr[name+'_static']=float(st[name]);rr[name+'_contrast']=float(e[name])-float(st[name])
            pair.append(rr);origrun.append(rr)
        wstar=float(th.mean());p=participation(np.asarray(wstar),th,c,3,'sigmoid',cfg)
        dtraj,wend=deterministic(th,c,3,'sigmoid',wstar,cfg,{'block':'original_main','world':wi,'beta':3.,'initial_action':wstar})
        detrows.extend(dtraj)
        for root in fixedpoints(th,c,3,'sigmoid',cfg):rootrows.append({'block':'original_main','world':wi,'beta':3.,**root})
        r={'world':wi,**{f'theta{g}':float(th[g]) for g in range(3)},'left_spacing':float(th[1]-th[0]),'right_spacing':float(th[2]-th[1]),
           'oracle_action':wstar,'initial_mixture_mean':float(meanmap(wstar,th,c,3,'sigmoid',cfg)),
           'initial_drift':float(meanmap(wstar,th,c,3,'sigmoid',cfg)-wstar),'deterministic_action_5000':wend,
           **{f'g{g}_initial_share':float(p[g]/p.sum()) for g in range(3)},
           'g0_contrast_world':float(np.mean([z['g0_risk_contrast'] for z in pair])),
           'negative_seed_contrasts':sum(z['g0_risk_contrast']<0 for z in pair)}
        for g in range(3):
            r[f'g{g}_endogenous_loss']=float(np.mean([z[f'g{g}_risk_endogenous'] for z in pair]));r[f'g{g}_static_loss']=float(np.mean([z[f'g{g}_risk_static'] for z in pair]))
        geometry.append(r)
    csvout(out/'original_primary_run_contrasts.csv',origrun);csvout(out/'original_world_geometry.csv',geometry)
    ot=[r for r in readcsv(old/'trajectories_world.csv') if r['scenario']=='main' and float(r['beta'])==3 and r['condition'] in ['endogenous','static']]
    csvout(out/'original_primary_trajectories.csv',ot)
    origcontrast=np.array([r['g0_contrast_world'] for r in geometry]);oidx=np.random.default_rng(2026092203).integers(0,20,(10000,20))
    original_summary={'mean_ci95':boot(origcontrast,oidx),'positive_worlds':int((origcontrast>0).sum()),
                      'negative_world_ids':[r['world'] for r in geometry if r['g0_contrast_world']<0]}
    # Fresh paired stochastic streams; no new study outcomes have been examined before this recorded execution.
    allruns=[];allworlds=[];alltr=[];costrows=[];main_arrays={};case=0
    T=cfg['rounds'];B=cfg['batch_size'];S=cfg['main']['seeds_per_world']
    draws,noise=draw_arrays(len(theta),S,T,B,cfg['main']['training_seed'],cfg['noise_halfwidth'])
    for fam in cfg['main']['families']:
        for b in cfg['main']['strength_anchors']:
            for cond in cfg['main']['conditions']:
                tag={'block':'main_extension','family':fam,'strength_anchor':b,'condition':cond,'init_label':'world_optimum'}
                result=simulate(theta,S,c,b,fam,cond,theta.mean(axis=1),draws,noise,cfg,case,tag,checks)
                rr,ww,tt,arr,cost=result;allruns+=rr;allworlds+=ww;alltr+=tt;costrows.append(cost);main_arrays[(fam,cond)]=arr
                case+=1;print('Completed main',case,fam,cond,flush=True)
    del draws,noise
    scfg=cfg['symmetric'];th=np.array(scfg['theta']);cs=np.array(scfg['friction']);S=scfg['seeds']
    draws,noise=draw_arrays(1,S,T,B,scfg['training_seed'],cfg['noise_halfwidth']);sym_summary=[]
    for b in scfg['betas']:
        for root in fixedpoints(th,cs,b,'sigmoid',cfg):rootrows.append({'block':'exact_symmetric','world':0,'beta':b,**root})
        for initial in scfg['initial_actions']:
            dtraj,end=deterministic(th,cs,b,'sigmoid',initial,cfg,{'block':'exact_symmetric','world':0,'beta':b,'initial_action':initial});detrows+=dtraj
            mirror_end=deterministic(th,cs,b,'sigmoid',-initial,cfg,{'block':'check','world':0,'beta':b,'initial_action':-initial})[1]
            checks['deterministic_mirror_max_error']=max(checks.get('deterministic_mirror_max_error',0.),abs(end+mirror_end))
            if initial==0 and abs(end)>1e-12:raise AssertionError('Exact zero should be deterministic fixed point')
            for cond in scfg['conditions']:
                tag={'block':'exact_symmetric','family':'sigmoid','strength_anchor':b,'condition':cond,'init_label':str(initial)}
                rr,ww,tt,arr,cost=simulate(th[None,:],S,cs,b,'sigmoid',cond,initial,draws,noise,cfg,case,tag,checks)
                allruns+=rr;allworlds+=ww;alltr+=tt;costrows.append(cost)
                final=np.array([r['final_action'] for r in rr]);d={'beta':b,'initial_action':initial,'condition':cond,
                    'seeds':S,'final_action_mean':float(final.mean()),'final_action_min':float(final.min()),'final_action_max':float(final.max()),
                    'n_left_below_minus_point2':int((final<-.2).sum()),'n_center_between_point2':int((abs(final)<=.2).sum()),
                    'n_right_above_point2':int((final>.2).sum()),'deterministic_endogenous_action_5000':end,
                    **dict(zip(METRICS,arr[0].tolist()))};sym_summary.append(d)
                case+=1
        print('Completed exact symmetric beta',b,flush=True)
    del draws,noise
    csvout(out/'run_metrics.csv',allruns);csvout(out/'world_metrics.csv',allworlds);csvout(out/'trajectories_world.csv',alltr)
    csvout(out/'fixed_points.csv',rootrows);csvout(out/'deterministic_trajectories.csv',detrows)
    csvout(out/'symmetric_seed_summaries.csv',sym_summary);csvout(out/'invitation_cost_checks.csv',costrows)
    idx=np.random.default_rng(cfg['bootstrap_seed']).integers(0,20,(cfg['bootstrap_resamples'],20));summaries=[];contrasts=[]
    for (fam,cond),arr in main_arrays.items():
        for j,m in enumerate(METRICS):
            mean,lo,hi=boot(arr[:,j],idx);summaries.append({'family':fam,'condition':cond,'metric':m,'mean':mean,'ci95_low':lo,'ci95_high':hi,'n_worlds':20})
    for fam in cfg['main']['families']:
        for lhs,rhs in [('endogenous','static'),('endogenous','quota'),('ipw_true','endogenous'),('ipw_omit_friction','ipw_true'),('ipw_half_sensitivity','ipw_true')]:
            for j,m in enumerate(METRICS):
                values=main_arrays[(fam,lhs)][:,j]-main_arrays[(fam,rhs)][:,j];mean,lo,hi=boot(values,idx)
                contrasts.append({'family':fam,'contrast':lhs+' minus '+rhs,'metric':m,'mean':mean,'ci95_low':lo,'ci95_high':hi,'positive_worlds':int((values>0).sum()),'negative_worlds':int((values<0).sum()),'n_worlds':20})
    csvout(out/'condition_estimates.csv',summaries);csvout(out/'contrasts.csv',contrasts)
    checks['fixedpoint_derivative_max_error']=max(r['finite_difference_error'] for r in rootrows)
    checks['actual_runs']=len(allruns);checks['planned_runs_match']=len(allruns)==cfg['planned_new_stochastic_runs']
    checks['max_cost_standardized_difference']=max(abs(r['standardized_difference']) for r in costrows)
    checks['original_input_hashes_unchanged']=all(sha(p)==oldhash[p.name] for p in inputs)
    # Law-matching identity evaluated directly at zero loss, not by imposing an impossible negative noise variance.
    aa=sigmoid(cfg['participation_intercept']-c);kk=3*(1-aa)
    checks['law_zero_loss_probability_match_error']=float(np.max(abs((.02+.96*aa)-(.02+.96*aa*np.exp(-kk*0)))))
    checks['law_zero_loss_slope_match_error']=float(np.max(abs(-.96*3*aa*(1-aa)-(-.96*aa*kk))))
    if not checks['planned_runs_match'] or not checks['original_input_hashes_unchanged']:raise AssertionError('Count/provenance failure')
    for name in ['probability_max_sum_error','true_ipw_moment_max_error','risk_decomposition_max_error','deterministic_mirror_max_error','law_zero_loss_probability_match_error','law_zero_loss_slope_match_error']:
        if checks[name]>1e-10:raise AssertionError(name)
    if checks['fixedpoint_derivative_max_error']>1e-7:raise AssertionError('Derivative disagreement')
    js(out/'checks.json',checks)
    summary={'status':cfg['status'],'complete_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-start,
             'frozen_sha256':frozen,'actual_new_runs':len(allruns),'condition_cells':case,'original_primary_recomputed':original_summary,
             'checks':checks,'limitations':['Exploratory extension after seeing the original results.','No human or learned-knowledge validation.',
               'Matched law slope is at L=0 only; strength parameters are not globally equivalent.','Propensity errors are specified misspecification, not data-fitted estimates.',
               'Equal accepted samples are not equal invitations.','Roots from sign-changing grids do not prove completeness at tangencies.',
               'Conditional mean-map local stability is not global stochastic convergence.'],
             'output_hashes':{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()}}
    js(out/'summary.json',summary);print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
