"""Independent checks for v2 local mean-map analysis (post-hoc extension)."""
from pathlib import Path
import json
import numpy as np

HERE=Path(__file__).resolve().parent
ETA=.05; VAR=.2**2/3

def participation(w, theta, beta, friction):
    s=1/(1+np.exp(-(2-np.asarray(friction)-beta*((w-theta)**2+VAR))))
    pi=.02+.96*s
    score=2*beta*(theta-w)*.96*s*(1-s)/pi
    return pi,score,s

def conditional_mean(w,theta,beta,friction,rho=None,h=0,j=0):
    if rho is None:rho=np.ones(len(theta))/len(theta)
    pi,score,s=participation(w,theta,beta,friction)
    q=rho*pi; q=q/q.sum()
    feedback=theta.copy();feedback[j]+=h
    return float(q@feedback)

def cov_derivative(w,theta,beta,friction,rho=None):
    if rho is None:rho=np.ones(len(theta))/len(theta)
    pi,score,s=participation(w,theta,beta,friction)
    q=rho*pi;q=q/q.sum();m=float(q@theta)
    return float(q@((theta-m)*score)),q

def bisection(fn,a,b):
    fa=fn(a);fb=fn(b)
    assert fa*fb<=0
    for _ in range(80):
        c=(a+b)/2;fc=fn(c)
        if fa*fc<=0:b=c;fb=fc
        else:a=c;fa=fc
    return (a+b)/2

theta=np.array([-1.,0,1.]);friction=np.zeros(3)
def central_slope(beta):
    se=1/(1+np.exp(-(2-beta*(1+VAR))))
    sm=1/(1+np.exp(-(2-beta*VAR)))
    return float(4*beta*.96*se*(1-se)/(2*(.02+.96*se)+(.02+.96*sm)))

thresholds=[bisection(lambda b:central_slope(b)-1,1.5,3),bisection(lambda b:central_slope(b)-1,3,5)]
cases=[]
for beta,brackets in [(1.5,[(-.001,.001)]),(3,[(-.6,-.3),(-.001,.001),(.3,.6)]),(5,[(-.001,.001)]),(8,[(-1,-.8),(-.6,-.5),(-.001,.001),(.5,.6),(.8,1)])]:
    roots=[]
    for a,b in brackets:
        root=bisection(lambda w:conditional_mean(w,theta,beta,friction)-w,a,b)
        deriv,q=cov_derivative(root,theta,beta,friction)
        slope=1-ETA+ETA*deriv
        roots.append({'root':root,'m_prime':deriv,'F_prime':slope,'locally_stable':bool(abs(slope)<1),'sampling_weights':q.tolist()})
    cases.append({'beta':beta,'central_closed_form_m_prime':central_slope(beta),'roots':roots})

# General unequal-population covariance derivative versus central finite differences.
rng=np.random.default_rng(20260927081);cov_errors=[];theta_errors=[]
for _ in range(200):
    th=np.sort(rng.uniform(-1.5,1.5,3));w=float(rng.uniform(-1.3,1.3));b=float(rng.uniform(0,8));fr=rng.uniform(0,2,3);rho=rng.dirichlet(np.ones(3));eps=1e-5
    analytic,q=cov_derivative(w,th,b,fr,rho)
    finite=(conditional_mean(w+eps,th,b,fr,rho)-conditional_mean(w-eps,th,b,fr,rho))/(2*eps)
    cov_errors.append(abs(analytic-finite))
    # Actual theta_j perturbation changes feedback content AND that group's participation.
    j=int(rng.integers(3));pi,score,s=participation(w,th,b,fr);m=conditional_mean(w,th,b,fr,rho)
    ps=2*b*(w-th[j])*.96*s[j]*(1-s[j])/pi[j]
    analytic_theta=q[j]*(1+(th[j]-m)*ps)
    hi=th.copy();lo=th.copy();hi[j]+=eps;lo[j]-=eps
    finite_theta=(conditional_mean(w,hi,b,fr,rho)-conditional_mean(w,lo,b,fr,rho))/(2*eps)
    theta_errors.append(abs(analytic_theta-finite_theta))

# Controlled feedback-only intervention retains baseline participation law.
# Verify implicit derivatives on the two beta3 attracting branches.
response=[]
for a,b in [(-.6,-.3),(.3,.6)]:
    root=bisection(lambda w:conditional_mean(w,theta,3,friction)-w,a,b)
    deriv,q=cov_derivative(root,theta,3,friction)
    for j in range(3):
        eps=1e-5
        hi=bisection(lambda w:conditional_mean(w,theta,3,friction,h=eps,j=j)-w,a,b)
        lo=bisection(lambda w:conditional_mean(w,theta,3,friction,h=-eps,j=j)-w,a,b)
        finite=(hi-lo)/(2*eps);analytic=q[j]/(1-deriv)
        response.append({'root':root,'group':j,'one_step_direct':float(ETA*q[j]),'frozen_weight_equilibrium':float(q[j]),'closed_loop_equilibrium':float(analytic),'finite_difference_closed_loop':finite,'absolute_error':abs(finite-analytic)})

# Exponential weights offer a separate analytic identity, not a claim of same roots.
expo_errors=[]
for _ in range(200):
    th=rng.uniform(-1.5,1.5,3);w=float(rng.uniform(-1,1));b=float(rng.uniform(0,8));rho=rng.dirichlet(np.ones(3));access=rng.uniform(0,2,3);eps=1e-6
    def exmean(x):
        p=rho*np.exp(-access-b*((x-th)**2+VAR));return float(p@th/p.sum())
    p=rho*np.exp(-access-b*((w-th)**2+VAR));q=p/p.sum();m=q@th
    expected=2*b*float(q@((th-m)**2));finite=(exmean(w+eps)-exmean(w-eps))/(2*eps)
    expo_errors.append(abs(expected-finite))

# Population-versus-feedback monitoring identity and common-function sign check.
monitor_errors=[];common_sign_violations=0
for _ in range(200):
    rho=rng.dirichlet(np.ones(5));loss=rng.uniform(0,4,5);pi=rng.uniform(.02,.98,5)
    z=rho@pi;j=rho@loss;feedback=(rho*pi)@loss/z
    covariance=rho@((pi-z)*(loss-j))
    monitor_errors.append(abs((j-feedback)-(-covariance/z)))
    common=.02+.96/(1+np.exp(-(2-2*loss)))
    common_cov=rho@((common-rho@common)*(loss-j))
    if common_cov>1e-14:common_sign_violations+=1

out={'status':'passed' if max(cov_errors+theta_errors+expo_errors)<2e-8 and max(x['absolute_error'] for x in response)<2e-7 and max(monitor_errors)<1e-12 and common_sign_violations==0 else 'failed',
     'scope':'Post-hoc analytic formula checks and numerical mean-map diagnostics; no claim of stochastic convergence or complete root enumeration.',
     'derivative_random_seed':20260927081,'central_stability_crossings':thresholds,'mean_map_cases':cases,
     'max_covariance_derivative_fd_error':max(cov_errors),'max_actual_theta_derivative_fd_error':max(theta_errors),'max_exponential_identity_fd_error':max(expo_errors),
     'feedback_only_response_checks':response,'max_monitoring_identity_error':max(monitor_errors),'common_decreasing_participation_sign_violations':common_sign_violations}
(HERE/'theory_verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
