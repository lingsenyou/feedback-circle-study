# Independent audit of the proposed potential interpretation and quota benchmark

Audit date: 2026-10-06. No manuscript, experiment, or historical result file was edited. These checks concern explanatory algebra for the existing completed study, not a new experiment or an assertion of originality.

## Verdict

The proposed identities and quota stationary-variance benchmark are correct under the stated assumptions. Two qualifications are essential: the sigmoid primitive displayed with division by beta assumes beta > 0; a local minimum of the potential is not automatically stable under a discrete update of arbitrary step size. No new stochastic experiment is needed for this addition.

## Potential identities

Let population weights rho_g be fixed and positive, sum to one, and let theta_g and v be fixed. Suppose pi_g(w) = phi_g(L_g(w)), with differentiable positive phi_g and L_g(w) = (w-theta_g)^2+v. Define

P(w) = sum_g rho_g integral_0^{L_g(w)} phi_g(u) du,
Z(w) = sum_g rho_g pi_g(w),
m(w) = sum_g rho_g pi_g(w) theta_g / Z(w).

The chain rule gives

P'(w) = 2 sum_g rho_g pi_g(w)(w-theta_g) = 2 Z(w)(w-m(w)).

Consequently the conditional-mean update satisfies the exact representation

F(w) = (1-eta)w + eta m(w) = w - eta P'(w)/(2 Z(w)).

This is a state-dependent, rescaled gradient step on P. It does not by itself guarantee a decrease of P at every discrete update. P is a representation of the conditional adaptation dynamics, not the fixed population loss J or a claimed optimal social objective.

Differentiating again gives P'' = 2 Z'(w)(w-m(w)) + 2 Z(w)(1-m'(w)). At a fixed point wbar = m(wbar),

P''(wbar) = 2 Z(wbar)(1-m'(wbar)).

The local update derivative is F'(wbar) = 1 - eta P''(wbar)/(2 Z(wbar)). Thus local asymptotic stability requires

0 < eta P''(wbar)/(2 Z(wbar)) < 2,

equivalently 1-2/eta < m'(wbar) < 1. A strict local maximum has m'>1 and is unstable for eta>0. A strict local minimum needs the additional upper step-size/curvature bound. Equalities require further analysis. These are statements about the deterministic conditional map; they do not prove global convergence or stochastic trapping.

## Sigmoid primitive and sensitivity limit

For beta>0 and phi_g(L) = 0.02 + 0.96 sigmoid(2-c_g-beta L), an antiderivative is

H_g(L) = 0.02 L - (0.96/beta) log(1+exp(2-c_g-beta L)).

The integral from zero is H_g(L)-H_g(0). Its derivative is exactly phi_g(L). Use a numerically stable softplus/logaddexp evaluation if plotting the potential. At beta=0, phi_g is constant in L, and the integral is [0.02+0.96 sigmoid(2-c_g)] L; the beta>0 expression should not be evaluated literally.

With fixed finite friction values, v>0 and the positive participation floor, each pi_g(w) tends to 0.02 as beta tends to infinity, and m(w) tends to the fixed-population mean sum_g rho_g theta_g. A pointwise description at each fixed action is sufficient for the paper. In this exact model there is also the stronger bound

0 <= pi_g(w)-0.02 <= 0.96 exp(2-c_g-beta v),

which is uniform over all real w because L_g(w)>=v. For finite groups, |m(w)-mu| <= [0.96 exp(max_g(2-c_g)-beta v)/0.02] sum_g rho_g |theta_g-mu|, where mu=sum rho theta. Therefore do not say uniform convergence is impossible. The simple limit statement does not establish how numerically observed finite-beta branches continue, merge, or disappear, or establish a complete bifurcation diagram. Both v>0 and floor>0 matter; the same conclusion need not hold when either is removed.

## Exact quota noise benchmark

Under equal group quotas, B=96, exactly B/3 accepted values per group, independent mean-zero noise variance v=0.2^2/3, and eta=0.05, the batch mean is mu plus noise with variance v/B. Writing e_t=w_t-mu gives

e_{t+1}=(1-eta)e_t+eta noise_t.

With e_0=0, Var(e_t)=[eta/(2-eta)](v/B)[1-(1-eta)^(2t)]. The stationary expected population regret is

E[(w-mu)^2]=[eta/(2-eta)] v/B = 3.5612535612535624e-6.

This is the expected stationary regret of the specified fixed-step quota algorithm, not a universal lower bound for every estimator. The original pre-update endpoint window t=200,...,249 has expected mean regret 3.561253560361302e-6; the exploratory t=950,...,999 window has 3.561253561253562e-6. The observed exploratory quota mean is 3.734711835995515e-6 and was already obtained from completed runs. No new simulation is needed to derive the benchmark.

## Independent numerical evidence

A fresh in-memory calculation used NumPy, did not import the experiment/theory implementations, and wrote no experiment outputs. Random verification seed: 2026100602. Across 1,000 random three-group configurations with unequal Dirichlet population weights, friction in [0,2], beta in [0.1,8], normal preferences/actions, and central difference h=1e-5:

- Maximum absolute P' versus primitive finite-difference discrepancy: 1.363856250158335e-10.
- Maximum conditional-map versus potential-step discrepancy: 4.440892098500626e-16.
- At the existing beta=3 and beta=8 fixed points, maximum discrepancy in P''=2Z(1-m') was 3.3306690738754696e-16.
- For beta=3, P'' at zero is -0.5466080991080787 and at the positive stable root 0.45385133322126614 is 0.5839563293079648.
- For beta=8, P'' at zero is 0.5536658553860834, at the positive unstable root 0.5319972336839589 is -0.6142324064648313, and at the positive stable root 0.9255883072331241 is 0.5301161593432768.

These signs agree with the previously reported local stability classifications. The addition can improve interpretation, but standard calculus identities and an EMA variance calculation should not be presented as a newly discovered general theory.
