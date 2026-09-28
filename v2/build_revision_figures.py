"""Publication plots from frozen outputs and declared exploratory mean-map checks."""
from pathlib import Path
import sys, csv, json, hashlib
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parent
if (ROOT/'_deps').exists(): sys.path.insert(0,str(ROOT/'_deps'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
BASE=ROOT.parent
FROZEN=BASE/'study' if (BASE/'study').exists() else BASE
OUT=ROOT/'figures'; OUT.mkdir(exist_ok=True)
C={'navy':'#17354C','teal':'#087F8C','amber':'#AE701B','purple':'#755AA6','gray':'#667580','light':'#D8E2E8'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.titlesize':10,'axes.labelsize':9,'legend.fontsize':7.5,'xtick.labelsize':8,'ytick.labelsize':8,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':C['gray'],'axes.labelcolor':C['navy'],'text.color':C['navy'],'xtick.color':C['gray'],'ytick.color':C['gray'],'savefig.facecolor':'white'})
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def save(fig,name):
    for ext in ['png','svg','pdf']:fig.savefig(OUT/(name+'.'+ext),dpi=400,bbox_inches='tight',pad_inches=.08)
    plt.close(fig)

def heterogeneity():
    rows=read(FROZEN/'results/run_metrics.csv')
    worlds=[]
    for w in range(20):
        vals={c:sorted([r for r in rows if r['scenario']=='main' and float(r['beta'])==3 and int(r['world'])==w and r['condition']==c],key=lambda r:int(r['seed'])) for c in ['endogenous','static']}
        ds=np.array([float(a['g0_risk'])-float(b['g0_risk']) for a,b in zip(vals['endogenous'],vals['static'])])
        assert len(ds)==10
        worlds.append({'world':w,'effect':float(ds.mean()),'seed_min':float(ds.min()),'seed_max':float(ds.max())})
    fig=plt.figure(figsize=(7.0,5.5)); gs=fig.add_gridspec(3,2,width_ratios=[1,1.22],hspace=.48,wspace=.37)
    ax=fig.add_subplot(gs[:,0]); order=sorted(worlds,key=lambda r:r['effect'])
    for y,r in enumerate(order):
        col=C['amber'] if r['effect']<0 else C['teal']
        ax.plot([0,r['effect']],[y,y],color=col,lw=1.6);ax.scatter(r['effect'],y,s=23,color=col,zorder=3)
    ax.axvline(0,color=C['gray'],lw=.8);ax.axvline(np.mean([r['effect'] for r in worlds]),color=C['navy'],lw=1,ls='--',label='World mean 0.734')
    ax.set(yticks=range(20),yticklabels=[str(r['world']) for r in order],xlabel='Group 0 loss difference\nEndogenous minus static',ylabel='Parameter world',title='A  All primary world effects')
    ax.legend(loc='lower right',frameon=False);ax.grid(axis='x',color=C['light'],lw=.5)
    tr=read(FROZEN/'results/trajectories_world.csv'); selected=[]
    # Column names are checked rather than inferred by order.
    timekey=next(k for k in ['completed_updates','round','step'] if k in tr[0])
    actionkey=next(k for k in ['action','w','mean_action'] if k in tr[0])
    for i,w in enumerate([0,10,11]):
        a=fig.add_subplot(gs[i,1]); effect=worlds[w]['effect']
        for cond,col,ls in [('endogenous',C['teal'],'-'),('static',C['purple'],'--')]:
            cell=sorted([r for r in tr if r['scenario']=='main' and float(r['beta'])==3 and int(r['world'])==w and r['condition']==cond],key=lambda r:float(r[timekey]))
            a.plot([float(r[timekey]) for r in cell],[float(r[actionkey]) for r in cell],color=col,ls=ls,lw=1.8,label=cond.capitalize())
            selected.extend({'world':w,'condition':cond,'completed_updates':r[timekey],'action':r[actionkey]} for r in cell)
        a.set_title(f'{chr(66+i)}  World {w}; loss difference {effect:+.3f}',loc='left')
        a.set_ylabel('Mean action');a.grid(color=C['light'],lw=.5)
        if i==0:a.legend(frameon=False,ncol=2,loc='best')
        if i==2:a.set_xlabel('Completed updates')
    save(fig,'figure5_world_heterogeneity');write(OUT/'figure5_world_effects.csv',worlds);write(OUT/'figure5_trajectories.csv',selected)
    return {'primary_mean':float(np.mean([r['effect'] for r in worlds])),'negative_worlds':[r['world'] for r in worlds if r['effect']<0]}

TH=np.array([-1.,0.,1.]); V=.2**2/3; ETA=.05
def mm(w,b):
    a=np.asarray(w); L=(a[...,None]-TH)**2+V; s=1/(1+np.exp(-(2-b*L))); pi=.02+.96*s
    q=pi/pi.sum(axis=-1,keepdims=True); m=(q*TH).sum(axis=-1)
    dp=-2*b*(a[...,None]-TH)*.96*s*(1-s)
    mp=(dp*(TH-m[...,None])).sum(axis=-1)/pi.sum(axis=-1)
    return m,mp
def roots(b):
    grid=np.linspace(-1.05,1.05,4001); f=mm(grid,b)[0]-grid; out=[]
    for i in range(len(grid)-1):
        if abs(f[i])<1e-12:out.append(float(grid[i]))
        if f[i]*f[i+1]<0:
            lo,hi=float(grid[i]),float(grid[i+1]); flo=float(f[i])
            for _ in range(48):
                mid=(lo+hi)/2; fm=float(mm(mid,b)[0])-mid
                if fm*flo<=0:hi=mid
                else:lo=mid;flo=fm
            out.append((lo+hi)/2)
    return sorted(set(round(x,11) for x in out))
def stability():
    fig,axs=plt.subplots(2,2,figsize=(7,6.1),gridspec_kw={'wspace':.37,'hspace':.45})
    beta=np.linspace(0,9,901); slopes=1-ETA+ETA*np.array([mm(0,b)[1] for b in beta]);a=axs[0,0]
    a.plot(beta,slopes,color=C['navy'],lw=1.6);a.axhline(1,color=C['gray'],ls='--',lw=1)
    for x in [1.95184250285,4.69112042173]:a.axvline(x,color=C['amber'],ls=':',lw=1)
    a.set(xlabel='Participation strength beta',ylabel='Central update slope F\'(0)',title='A  Local stability of the center',ylim=(.94,1.04));a.grid(color=C['light'],lw=.5)
    rr=[];a=axs[0,1]
    for b in np.linspace(0,9,181):
        for w in roots(float(b)):
            slope=float(.95+.05*mm(w,b)[1]);r={'beta':float(b),'fixed_point':w,'update_slope':slope,'locally_stable':abs(slope)<1,'residual':float(mm(w,b)[0]-w)};rr.append(r)
    for stable,col,label in [(True,C['teal'],'Locally stable'),(False,C['amber'],'Unstable')]:
        cell=[r for r in rr if r['locally_stable']==stable];a.scatter([r['beta'] for r in cell],[r['fixed_point'] for r in cell],s=3,color=col,label=label)
    a.set(xlabel='Participation strength beta',ylabel='Fixed point',title='B  Numerically located fixed points');a.legend(frameon=False,fontsize=7,loc='upper left');a.grid(color=C['light'],lw=.5)
    pathrows=[];palette={-.75:'#25479D',-.25:'#258A9B',-.01:'#7652A2',0:'#4E5964',.01:'#C4771C',.25:'#D46442',.75:'#AC204C'}
    for j,b in enumerate([3,8]):
        a=axs[1,j]
        for w0 in [-.75,-.25,-.01,0,.01,.25,.75]:
            w=float(w0);path=[w]
            for t in range(1000):w=.95*w+.05*float(mm(w,b)[0]);path.append(w)
            a.plot(range(1001),path,lw=1.25,color=palette[w0],ls='--' if w0==0 else '-',label=f'{w0:g}')
            pathrows.extend({'beta':b,'initial_action':w0,'completed_updates':t,'action':v} for t,v in enumerate(path))
        a.set(xlabel='Completed updates',ylabel='Action',title=f'{chr(67+j)}  Deterministic mean map; beta = {b}',ylim=(-1,1));a.grid(color=C['light'],lw=.5)
    axs[1,1].legend(title='Initial action',ncol=4,loc='upper center',bbox_to_anchor=(.47,-.25),frameon=False,fontsize=7,title_fontsize=8,columnspacing=.8,handlelength=1.5)
    save(fig,'figure6_stability_initialization')
    write(OUT/'figure6_slopes.csv',[{'beta':float(b),'central_update_slope':float(s)} for b,s in zip(beta,slopes)])
    write(OUT/'figure6_roots.csv',rr);write(OUT/'figure6_mean_map_paths.csv',pathrows)
    assert max(abs(r['residual']) for r in rr)<1e-9
    return {'largest_root_residual':max(abs(r['residual']) for r in rr),'roots_beta3':roots(3),'roots_beta8':roots(8),'note':'Exploratory numerical roots and conditional-mean paths; no stochastic convergence claim.'}

def extension():
    data=read(ROOT/'extension/results/condition_estimates.csv');contr=read(ROOT/'extension/results/contrasts.csv')
    conditions=list(dict.fromkeys(r['condition'] for r in data));print('extension conditions',conditions)
    labels={'endogenous':'Unweighted','static':'Static','quota':'Quota','ipw_true':'IPW true','ipw_omit_friction':'IPW no friction','ipw_half_sensitivity':'IPW half sensitivity'}
    fig,axs=plt.subplots(2,2,figsize=(7.35,6.05),gridspec_kw={'wspace':.65,'hspace':.5})
    a=axs[0,0];L=np.linspace(0,4,300);curves=[]
    for c,col,group in [(1.2,C['navy'],'Group 0'),(0,C['teal'],'Groups 1 and 2')]:
        sig=1/(1+np.exp(-(2-c)));vals={'sigmoid':.02+.96/(1+np.exp(-(2-c-3*L))),'exponential':.02+.96*sig*np.exp(-3*(1-sig)*L)}
        for family,v in vals.items():
            a.plot(L,v,color=col,ls='-' if family=='sigmoid' else '--',lw=1.5,label=f'{group}; {family}')
            curves.extend({'friction':c,'family':family,'loss':float(l),'participation':float(p)} for l,p in zip(L,v))
    a.set(title='A  Participation law challenge',xlabel='Expected group loss',ylabel='Participation probability');a.legend(frameon=False,fontsize=6.3,loc='upper right');a.grid(color=C['light'],lw=.5)
    a=axs[0,1];points=[]
    for y,family,col in [(1,'sigmoid',C['navy']),(0,'matched_exponential',C['teal'])]:
        r=next(r for r in contr if r['family']==family and r['contrast']=='endogenous minus static' and r['metric']=='g0_loss');m,lo,hi=map(float,[r['mean'],r['ci95_low'],r['ci95_high']]);a.errorbar(m,y,xerr=[[m-lo],[hi-m]],fmt='o',color=col,capsize=3);points.append(r)
    a.axvline(0,color=C['gray'],lw=.8);a.set(yticks=[0,1],yticklabels=['Exponential','Sigmoid'],ylim=(-.6,1.6),xlabel='Group 0 loss difference',title='B  Endogenous minus static');a.grid(axis='x',color=C['light'],lw=.5)
    for j,metric in enumerate(['population_regret','expected_invites_per_accepted']):
        a=axs[1,j]
        for family,col,offset,marker in [('sigmoid',C['navy'],.12,'o'),('matched_exponential',C['teal'],-.12,'s')]:
            for i,cond in enumerate(conditions):
                r=next(r for r in data if r['family']==family and r['condition']==cond and r['metric']==metric)
                m,lo,hi=map(float,[r['mean'],r['ci95_low'],r['ci95_high']]);a.errorbar(m,i+offset,xerr=[[m-lo],[hi-m]],fmt=marker,color=col,capsize=2,ms=4,label=('Sigmoid' if family=='sigmoid' else 'Exponential') if i==0 else None)
                points.append(r)
        a.set(yticks=range(len(conditions)),yticklabels=[labels.get(c,c) for c in conditions]);a.invert_yaxis();a.grid(axis='x',color=C['light'],lw=.5)
        if j==0:a.set_xscale('log');a.set(title='C  Correction sensitivity',xlabel='Population regret (log scale)')
        else:a.set(title='D  Recruitment assumptions',xlabel='Expected invitations per accepted item');a.legend(frameon=False,fontsize=7,loc='lower right')
    save(fig,'figure7_response_correction_costs');write(OUT/'figure7_participation_curves.csv',curves)
    (OUT/'figure7_plotted_estimates.json').write_text(json.dumps(points,indent=2),encoding='utf-8')
    return {'conditions':conditions,'note':'New 1000-round exploratory extension; endpoint rounds 951-1000; intervals over the same 20 worlds.'}

if __name__=='__main__':
    r={'executed_utc':datetime.now(timezone.utc).isoformat(),'numpy':np.__version__,'matplotlib':matplotlib.__version__,'heterogeneity':heterogeneity(),'stability':stability()}
    if (ROOT/'extension/results/condition_estimates.csv').exists():r['extension']=extension()
    (OUT/'figure_analysis_audit.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r,indent=2))
