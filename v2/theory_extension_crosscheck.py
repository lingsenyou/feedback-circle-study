"""Independent aggregation/formula audit of the exploratory extension.
Does not import the extension implementation or change any original output.
"""
from pathlib import Path
from collections import defaultdict, Counter
import csv,json,hashlib,math
import numpy as np

HERE=Path(__file__).resolve().parent; EX=HERE/'extension'; OUT=EX/'results'
def csvread(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cfg=json.loads((EX/'config.json').read_text());summary=json.loads((OUT/'summary.json').read_text())
rows=csvread(OUT/'run_metrics.csv');worlds=csvread(OUT/'world_metrics.csv');est=csvread(OUT/'condition_estimates.csv');contrasts=csvread(OUT/'contrasts.csv')
costs=csvread(OUT/'invitation_cost_checks.csv');sym=csvread(OUT/'symmetric_seed_summaries.csv')
theta=np.load(HERE.parent/'study/results/world_parameters.npz')['theta'];var=.2**2/3
metadata=['block','family','strength_anchor','condition','init_label']
metrics=[k for k in worlds[0] if k not in metadata+['world']]
def cell(r):return tuple(r[k] for k in metadata)
grouped=defaultdict(list)
for r in rows:grouped[cell(r)+(int(r['world']),)].append(r)
errors={};errors['world_aggregation']=0.;count_checks=[]
for r in worlds:
    rr=grouped[cell(r)+(int(r['world']),)]
    count_checks.append(len(rr)==(10 if r['block']=='main_extension' else 50))
    for m in metrics:errors['world_aggregation']=max(errors['world_aggregation'],abs(np.mean([float(z[m]) for z in rr])-float(r[m])))
idx=np.random.default_rng(cfg['bootstrap_seed']).integers(0,20,(cfg['bootstrap_resamples'],20))
wm={}
for fam in cfg['main']['families']:
    for cond in cfg['main']['conditions']:
        rr=sorted([r for r in worlds if r['block']=='main_extension' and r['family']==fam and r['condition']==cond],key=lambda r:int(r['world']))
        wm[(fam,cond)]={m:np.array([float(r[m]) for r in rr]) for m in metrics}
errors['condition_estimates']=0.;errors['contrasts']=0.;sign_checks=[]
def estimates(vals):return [vals.mean(),*np.quantile(vals[idx].mean(axis=1),[.025,.975])]
for r in est:
    vals=wm[(r['family'],r['condition'])][r['metric']]
    errors['condition_estimates']=max(errors['condition_estimates'],max(abs(a-float(r[k])) for a,k in zip(estimates(vals),['mean','ci95_low','ci95_high'])))
for r in contrasts:
    lhs,rhs=r['contrast'].split(' minus ');vals=wm[(r['family'],lhs)][r['metric']]-wm[(r['family'],rhs)][r['metric']]
    errors['contrasts']=max(errors['contrasts'],max(abs(a-float(r[k])) for a,k in zip(estimates(vals),['mean','ci95_low','ci95_high'])))
    sign_checks.append(sum(vals>0)==int(r['positive_worlds']) and sum(vals<0)==int(r['negative_worlds']))

errors['population_decomposition']=0.;errors['monitoring_gap_identity']=0.;errors['quota_shares']=0.;errors['cost_aggregation']=0.;negative_endpoint_variance=[]
for r in rows:
    losses=np.array([float(r['g'+str(g)+'_loss']) for g in range(3)])
    th=theta[int(r['world'])] if r['block']=='main_extension' else np.array([-1,0,1])
    oracle=np.mean((th-th.mean())**2)+var
    errors['population_decomposition']=max(errors['population_decomposition'],abs(losses.mean()-float(r['population_loss'])),abs(float(r['population_loss'])-oracle-float(r['population_regret'])))
    errors['monitoring_gap_identity']=max(errors['monitoring_gap_identity'],abs(float(r['population_loss'])-float(r['monitoring_loss'])-float(r['monitoring_gap'])))
    if float(r['population_regret'])-(float(r['action'])-th.mean())**2 < -1e-12:negative_endpoint_variance.append(r)
    if r['condition']=='quota':
        for g in range(3):
            for kind in ['expected','realized']:errors['quota_shares']=max(errors['quota_shares'],abs(float(r[f'g{g}_{kind}_share'])-1/3))
        errors['quota_shares']=max(errors['quota_shares'],abs(float(r['effective_sample_size'])-96))

cost_z=[]
for r in costs:
    rr=[z for z in rows if cell(z)==cell(r)]
    ex=sum(float(z['cumulative_expected_invites']) for z in rr);actual=sum(int(z['cumulative_realized_invites']) for z in rr);vv=sum(float(z['cumulative_invite_variance']) for z in rr)
    z=(actual-ex)/math.sqrt(vv);cost_z.append(z)
    errors['cost_aggregation']=max(errors['cost_aggregation'],abs(z-float(r['standardized_difference'])),abs(ex-float(r['expected_total_invites']))/ex,abs(vv-float(r['conditional_variance_total']))/vv)

# Check matching identity via independent scalar expressions and finite differences in LOSS.
matching=[]
for c in [0,1.2]:
    a=1/(1+math.exp(-(2-c)));k=3*(1-a)
    def logistic(L):return .02+.96/(1+math.exp(-(2-c-3*L)))
    def exponential(L):return .02+.96*a*math.exp(-k*L)
    eps=1e-6;s1=(logistic(eps)-logistic(-eps))/(2*eps);s2=(exponential(eps)-exponential(-eps))/(2*eps)
    matching.append({'friction':c,'sigmoid_probability_at_zero':logistic(0),'exponential_probability_at_zero':exponential(0),'sigmoid_loss_derivative_fd':s1,'exponential_loss_derivative_fd':s2,'analytic_common_slope':-.96*3*a*(1-a),'probabilities_at_L1':[logistic(1),exponential(1)]})

# At the original optimum: independently compute large-batch weighted target under each error.
# A ratio of moments is deliberately NOT identified with finite-batch E[ratio].
targets=[]
def pfun(L,c,b,fam):
    a=1/(1+np.exp(-(2-c)))
    return .02+.96*(1/(1+np.exp(-(2-c-b*L))) if fam=='sigmoid' else a*np.exp(-b*(1-a)*L))
for fam in cfg['main']['families']:
    for condition in ['ipw_true','ipw_omit_friction','ipw_half_sensitivity']:
        biases=[]
        for th in theta:
            opt=th.mean();L=(opt-th)**2+var;truec=np.array([1.2,0,0]);p=pfun(L,truec,3,fam);q=p/p.sum()
            estimatedc=np.zeros(3) if condition=='ipw_omit_friction' else truec
            estimatedb=1.5 if condition=='ipw_half_sensitivity' else 3
            phat=pfun(L,estimatedc,estimatedb,fam)
            target=float(np.sum(q*th/phat)/np.sum(q/phat));biases.append(target-opt)
        targets.append({'family':fam,'condition':condition,'mean_initial_ratio_of_moments_bias':float(np.mean(biases)),'max_abs_bias':float(np.max(abs(np.array(biases))))})

sym_checks=[]
for r in sym:
    rr=[z for z in rows if z['block']=='exact_symmetric' and float(z['strength_anchor'])==float(r['beta']) and float(z['init_label'])==float(r['initial_action']) and z['condition']==r['condition']]
    final=np.array([float(z['final_action']) for z in rr])
    sym_checks.append(len(rr)==50 and sum(final<-.2)==int(r['n_left_below_minus_point2']) and sum(abs(final)<=.2)==int(r['n_center_between_point2']) and sum(final>.2)==int(r['n_right_above_point2']))

key_contrasts=[r for r in contrasts if r['metric'] in ['g0_loss','population_regret'] and r['contrast'] in ['endogenous minus static','ipw_omit_friction minus ipw_true','ipw_half_sensitivity minus ipw_true']]
hashes={'protocol':sh(EX/'PROTOCOL.md')==summary['frozen_sha256']['protocol'],'config':sh(EX/'config.json')==summary['frozen_sha256']['config'],'code':sh(EX/'run_extension.py')==summary['frozen_sha256']['code'],'all_recorded_outputs':all(sh(OUT/n)==h for n,h in summary['output_hashes'].items())}
passed=all(count_checks+sign_checks+sym_checks) and len(rows)==4500 and all(hashes.values()) and max(errors.values())<1e-9 and len(negative_endpoint_variance)==0
out={'status':'passed' if passed else 'failed','scope':'Independent review of formulas, aggregation, bootstrap, counts, quota allocations, cost summaries and weight misspecification; does not rerun full main simulation or import its code.','run_counts':dict(Counter(r['block'] for r in rows)),'max_errors':errors,'all_seed_counts_correct':all(count_checks),'all_contrast_sign_counts_correct':all(sign_checks),'all_symmetric_branch_counts_correct':all(sym_checks),'negative_endpoint_variance_count':len(negative_endpoint_variance),'hash_checks':hashes,'law_matching':matching,'initial_weighting_targets':targets,'key_recomputed_contrasts':key_contrasts,'cost_max_abs_standardized_difference':max(abs(z) for z in cost_z),'minor_provenance_gap':'Protocol says original configuration is hashed, but execution_start hashes selected original result files only; original configuration is embedded inside hashed original summary. No result-changing issue.'}
(HERE/'theory_extension_crosscheck.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
