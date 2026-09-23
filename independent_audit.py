"""Independent scalar-loop audit; does not import or modify run_study.py."""
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
cfg = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
summary = json.loads((ROOT / 'results/summary.json').read_text(encoding='utf-8'))
with (ROOT / 'results/run_metrics.csv').open(newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
theta = (np.asarray(cfg['theta_base']) + np.random.default_rng(cfg['world_seed']).uniform(
    -cfg['theta_jitter_halfwidth'], cfg['theta_jitter_halfwidth'], (cfg['worlds'], 3)))[0].tolist()
rng = np.random.default_rng(np.random.SeedSequence([cfg['training_seed'], 0, 0]))
draws = rng.random((cfg['rounds'], cfg['batch_size']))
noise = rng.uniform(-cfg['within_group_noise_halfwidth'], cfg['within_group_noise_halfwidth'],
                    (cfg['rounds'], cfg['batch_size']))
variance = cfg['within_group_noise_halfwidth'] ** 2 / 3
oracle = sum(theta) / 3
oracle_risk = sum((oracle - m) ** 2 + variance for m in theta) / 3
beta = 3.0
def participation(w):
    raw = [cfg['participation_floor'] + cfg['participation_span'] /
           (1 + math.exp(-(cfg['participation_intercept'] - cfg['friction'][g] - beta * ((w-theta[g])**2 + variance))))
           for g in range(3)]
    return raw, [x / sum(raw) for x in raw]

initial_raw, initial_p = participation(oracle)
checks = []
for condition in cfg['conditions']:
    w = oracle
    points = []
    for t in range(cfg['rounds']):
        raw, p = participation(w)
        if condition == 'static':
            raw, p = initial_raw, initial_p
        values, weights, groups = [], [], []
        for j in range(cfg['batch_size']):
            if condition == 'quota':
                g = j // (cfg['batch_size'] // 3)
            else:
                u = float(draws[t, j])
                g = 0 if u < p[0] else (1 if u < p[0] + p[1] else 2)
            groups.append(g)
            values.append(theta[g] + float(noise[t, j]))
            weights.append(1 / (3 * p[g]))
        risks = [(w-m)**2 + variance for m in theta]
        population = sum(risks)/3
        sampling = [1/3]*3 if condition == 'quota' else p
        weighted = sum(sampling[g] * risks[g] for g in range(3))
        observed = sum((w-y)**2 for y in values) / len(values)
        point = {
            'g0_risk': risks[0], 'g1_risk': risks[1], 'g2_risk': risks[2],
            'population_risk': population, 'population_regret': (w-oracle)**2,
            'feedback_weighted_risk': weighted, 'monitoring_gap': population-weighted,
            'sample_monitoring_gap': population-observed,
            'g0_feedback_share': groups.count(0) / len(groups),
            'g0_expected_feedback_share': sampling[0],
            'expected_invitations_per_accepted': sum(1/x for x in raw)/3 if condition == 'quota' else 3/sum(raw),
            'action': w,
        }
        if t >= cfg['rounds'] - cfg['endpoint_last_rounds']:
            points.append(point)
        estimate = sum(y*a for y,a in zip(values, weights))/sum(weights) if condition == 'ipw' else sum(values)/len(values)
        w = (1-cfg['learning_rate'])*w + cfg['learning_rate']*estimate
    independent = {k: sum(point[k] for point in points)/len(points) for k in points[0]}
    independent.update(action_after_last_update=w, oracle_action=oracle, oracle_risk=oracle_risk)
    stored = next(r for r in rows if r['scenario']=='main' and float(r['beta'])==beta and r['condition']==condition and r['world']=='0' and r['seed']=='0')
    errors = {k: abs(value-float(stored[k])) for k,value in independent.items()}
    checks.append({'condition': condition, 'max_absolute_error': max(errors.values()),
                   'errors': errors, 'independent_metrics': independent})

# Recompute the primary paired CI directly from run CSV, averaging seeds before bootstrap.
differences=[]
for world in range(cfg['worlds']):
    means={}
    for condition in ['endogenous', 'static']:
        subset=[float(r['g0_risk']) for r in rows if r['scenario']=='main' and float(r['beta'])==3 and r['condition']==condition and int(r['world'])==world]
        assert len(subset)==cfg['paired_seeds_per_world']
        means[condition]=sum(subset)/len(subset)
    differences.append(means['endogenous']-means['static'])
bootstrap_rng=np.random.default_rng(cfg['bootstrap_seed'])
samples=[]
for _ in range(cfg['bootstrap_resamples']):
    ids=bootstrap_rng.integers(0,cfg['worlds'],size=cfg['worlds'])
    samples.append(sum(differences[int(i)] for i in ids)/len(ids))
lo,hi=np.quantile(samples,[0.025,0.975])
primary={'mean':sum(differences)/len(differences),'ci95_low':float(lo),'ci95_high':float(hi)}
primary_errors={k:abs(v-summary['primary_result'][k]) for k,v in primary.items()}
hash_checks={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==summary[key]
             for name,key in [('run_study.py','code_sha256'),('config.json','config_sha256'),('PROTOCOL.md','protocol_sha256')]}
out={
    'status':'passed' if all(c['max_absolute_error']<1e-12 for c in checks) and max(primary_errors.values())<1e-12 and all(hash_checks.values()) else 'failed',
    'scope':'Independent scalar loop for main beta=3 world=0 seed=0 all four conditions; all-world primary CI from run CSV',
    'imports_main_study_code':False, 'hash_matches':hash_checks, 'scalar_checks':checks,
    'independent_primary':primary,'primary_absolute_errors':primary_errors,
    'bootstrap_unit':'20 parameter worlds; 10 paired seeds averaged within world',
    'endpoint':'50 pre-update decisions at zero-based rounds 200 through 249; not terminal post-update state',
    'ipw':'Code uses weights 1/(3*p_g); manuscript uses 1/pi_g. They differ by common sum(pi)/3 and yield the same self-normalized ratio. Ratio is not exactly unbiased.',
    'monitoring_gap':'Fixed equal-population expected risk minus current-feedback-weighted expected risk; positive values mean optimistic feedback-only monitoring.',
    'feedback_accounting':{'processed_feedback_instances':len(rows)*cfg['rounds']*cfg['batch_size'],
        'base_selection_uniforms':cfg['worlds']*cfg['paired_seeds_per_world']*cfg['rounds']*cfg['batch_size'],
        'base_preference_noise_draws':cfg['worlds']*cfg['paired_seeds_per_world']*cfg['rounds']*cfg['batch_size'],
        'note':'Common random numbers are reused across 36 condition/beta/scenario cells; 172.8 million processed instances are not independent data observations.'},
    'required_manuscript_clarifications':[
        'Define monitoring gap explicitly as J minus feedback-weighted risk, not an unspecified difference between them.',
        'Describe endpoints as last 50 pre-update decision rounds (201-250), rather than last 50 updates.',
        'If 172.8 million is mentioned, call it processed synthetic feedback instances across paired runs, not independent observations.']
}
(ROOT/'independent_audit.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':out['status'],'scalar_max_error':max(c['max_absolute_error'] for c in checks),'primary':primary,'hashes':hash_checks},indent=2))
