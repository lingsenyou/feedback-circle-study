# Local dynamics and feedback influence: verified theory notes for revision 2

Prepared 27 September 2026. This is an explicitly **post-hoc analytical extension** motivated by the original simulation and review. It does not amend the original execution protocol. The identities below follow from differentiation and local discrete-time stability analysis; no priority claim, new general theorem, or stochastic-convergence claim is made. Numerically located roots are separately labelled.

## 1. Model, target, and conditional mean map

Let there be finitely many groups `g=1,...,G` with fixed population weights `rho_g>0`, `sum rho_g=1`, and fixed preference means `theta_g`. Let `pi_g(w)>0` be continuously differentiable participation probabilities near the action under study. Participation selects groups, but within-group submitted noise has conditional mean zero: `E[y | g,w]=theta_g`. Conditional on acceptance,

`q_g(w) = rho_g pi_g(w) / Z(w)`, where `Z(w)=sum_h rho_h pi_h(w)`.

Define the feedback-mixture mean and population-optimal squared-loss action:

`m(w)=sum_g q_g(w) theta_g`, and `w*=sum_g rho_g theta_g`.

For an unweighted batch average of any finite size `B`, the update `w_next=(1-eta)w+eta ybar` satisfies the exact conditional identity

**(1)** `E[w_next | w]=(1-eta)w+eta m(w)=F(w)`.

The population optimum `w*` and the roots of `m(w)=w` need not coincide. Equation (1) is conditional on the current state. In general, `E[F(w_t)]` is **not** `F(E[w_t])`. Deterministic iteration of `F` is a mean-map diagnostic, not the exact unconditional stochastic mean trajectory.

The original study is the special case `G=3`, `rho_g=1/3`, `eta=.05`, and `B=96`. Unequal `rho` is introduced here to make the identity general, not to imply that unequal-mass simulations were part of the original experiment.

## 2. Derivative as a covariance: step-by-step identity

Define the participation score with respect to action:

`s_g(w)=d log pi_g(w)/dw=pi'_g(w)/pi_g(w)`.

Since `Z'(w)/Z(w)=sum_g q_g(w)s_g(w)`, differentiating the normalized sampling weights gives

**(2)** `q'_g(w)=q_g(w)[s_g(w)-E_q{s(w)}]`.

Multiplying by `theta_g` and summing gives

**(3)** `m'(w)=Cov_q(theta,s(w))=sum_g q_g(w)[theta_g-m(w)]s_g(w)`.

The covariance uses the currently accepted-feedback distribution `q`; it is not a population covariance unless the distributions coincide. The formula requires fixed preference means during differentiation. If the feedback locations themselves depend on `w`, add `E_q[theta'_g(w)]`.

For the study's bounded logistic response, put

`ell_g(w)=(w-theta_g)^2+v`, `u_g(w)=sigmoid(a-c_g-beta ell_g(w))`, `pi_g(w)=f+b u_g(w)`.

Then

`pi'_g(w)=2 beta b u_g(w)[1-u_g(w)](theta_g-w)`,

and therefore

**(4)** `m'(w)=2 beta sum_g q_g(w)[theta_g-m(w)](theta_g-w) b u_g(w)[1-u_g(w)]/pi_g(w)`.

Use `f=.02`, `b=.96`, `a=2`, and `v=.2^2/3` for the actual study. Equation (4) does not assume that `m'(w)` is globally positive or that increasing beta always increases it.

An optional contrasting identity illustrates why response-family assumptions matter. If positive selection weights have exponential form `pi_g(w)=A_g exp[-beta ell_g(w)]` (with admissible scaling if interpreted as probabilities), then `s_g=2 beta(theta_g-w)` and

**(5)** `m'(w)=2 beta Var_q(theta)`.

This identity is for that different response family. It does not imply the bounded logistic model has the same roots, thresholds, or global behavior. It is verified algebraically and by a separate finite-difference calculation.

## 3. Fixed points and local stability

A deterministic fixed point `wbar` satisfies `m(wbar)=wbar`. The derivative of the update map is

**(6)** `F'(wbar)=1-eta+eta m'(wbar)`.

For continuously differentiable scalar maps, `|F'(wbar)|<1` implies local asymptotic stability and `|F'(wbar)|>1` implies local instability. The equality cases require further analysis. Thus, for `eta>0`, the strict sufficient stability condition is

**(7)** `1-2/eta < m'(wbar) < 1`.

With `eta=.05`, this interval is `(-39,1)`. The common shorthand `m'<1` alone is insufficient for arbitrary participation laws; the lower bound must be retained unless nonnegative derivatives or another restriction are established.

These are local claims about `F`. They do not prove global convergence, uniqueness, branch selection, or concentration of a finite-batch stationary distribution. Fixed points depend on the participation/preference model; their local stability additionally depends on `eta`.

## 4. Operational influence: immediate correction versus participation-mediated response

Group loss is not a response derivative. To define an explicit influence diagnostic, consider a **controlled feedback-only intervention**: increase group `j`'s submitted feedback mean by a small persistent amount `h`, while leaving the population objective, baseline preference parameters in the participation law, and all other feedback means unchanged. This is a perturbation of feedback content, not a claim that real underlying preferences changed.

The perturbed mixture mean is

`m(w,h)=sum_g q_g(w)theta_g + h q_j(w)`.

This intervention has three distinct responses:

1. **Immediate direct response at fixed current state:** `partial E[w_next|w,h]/partial h = eta q_j(w)`. This is the exact conditional one-step derivative for the specified intervention.
2. **Persistent response with sampling weights frozen:** if `q` is held fixed for all subsequent updates, the deterministic limiting action shifts by `q_j h`; its derivative is `q_j`, not `eta q_j`. The same statement holds for the limiting mean of the linear fixed-weight stochastic recursion under its usual finite-moment assumptions.
3. **Persistent response with participation allowed to change with action:** on a differentiable fixed-point branch satisfying `wbar(h)=m(wbar(h),h)`, the implicit-function identity at `h=0` is

**(8)** `d wbar / dh = q_j(wbar) / [1-m'(wbar)]`, provided `m'(wbar) != 1`.

For an adaptively reachable local equilibrium response, report (8) on a stable branch. A formal derivative at an unstable root is not evidence that the learner will track it. Near a threshold, the local derivative can be large while the neighborhood in which linear approximation is useful shrinks.

Equation (8) separates an accepted-feedback share from a local feedback-loop gain. At a fixed equilibrium the factor `1/[1-m']` is common to all feedback-only group interventions. Consequently, the loop gain changes absolute influence but **does not independently change the ratio of group influences at that same point**: the ratio is `q_j/q_k`. Group influence disparities arise through the selected distribution and equilibrium branch; do not claim an additional group-specific multiplier that this model lacks.

More generally, if intervention `h` directly changes participation or true preferences as well, the numerator is

**(9)** `partial_h m = E_q[partial_h theta_g] + Cov_q(theta, partial_h log pi_g)`.

The equilibrium derivative becomes `partial_h m/[1-partial_w m]`. Therefore, `q_j/(1-m')` must not be used for an actual preference/access intervention without checking its participation pathway.

For example, if the true `theta_j` changes in the study's logistic model, both its feedback mean and its loss-dependent participation change. At fixed `w`,

`partial_{theta_j} m = q_j {1 + (theta_j-m) [2 beta (w-theta_j) b u_j(1-u_j)/pi_j]}`.

At a fixed point `m=w`, this simplifies to

`q_j {1 - 2 beta (theta_j-w)^2 b u_j(1-u_j)/pi_j}`.

That quantity can differ considerably from `q_j`. It concerns another estimand and is not interchangeable with the controlled feedback-only diagnostic. None of these local mathematical influence measures is a validated measure of empathy, stakeholder welfare, or retained model knowledge.

## 5. Monitoring gap: a population-covariance identity

Fix a current action `w` and let `L_g=L_g(w)` be its expected group loss. Define `J=E_rho[L]` and `J_feedback=E_q[L]`, where `q_g=rho_g pi_g/E_rho[pi]`. Then the monitoring gap satisfies

**(10)** `G=J-J_feedback=-Cov_rho(pi,L)/E_rho[pi]`.

To verify the identity, multiply `G` by `Z=E_rho[pi]`: `ZG=E_rho[L]E_rho[pi]-E_rho[pi L]=-Cov_rho(pi,L)`. This holds pointwise at any fixed action, independently of the learning algorithm or whether that action minimizes population loss.

If participation is the **same nonincreasing function of loss in every group**, `pi_g=phi(L_g)`, then

`Cov_rho(phi(L),L) = (1/2) sum_{g,h} rho_g rho_h [phi(L_g)-phi(L_h)] [L_g-L_h] <= 0`.

Hence `G>=0` in this restricted case: participant-weighted monitoring cannot exceed the fixed-population expected loss. Strict positivity requires a nonzero weighted pair with different loss and strictly different participation. If participation depends on heterogeneous access friction or other group-specific variables, it need not be a common decreasing function of loss, and the covariance can have either sign. The study's main scenario has heterogeneous friction, so a general nonnegative-gap theorem must not be asserted for it. Its observed positive gaps remain numerical findings.

Correcting the learning objective does not algebraically remove this monitoring gap. Even at `w*`, loss differences can remain among groups, and a feedback-weighted evaluation can retain a nonzero covariance with participation. Exact population quotas make `q=rho` and thus `G=0` by construction. Known-probability correction of the monitoring estimator can target population loss, but self-normalized finite-batch ratios need not be exactly unbiased. This identity explains the distinction between learning correction and monitoring correction without proposing a new algorithm.

## 6. Exactly symmetric special case: analytic formula and numerical diagnostics

This new diagnostic sets `theta=(-d,0,d)`, equal population weights and zero friction, with `d=1` for reported numbers. Symmetry gives `m(0)=0` for every beta. Let

`u_e=sigmoid(a-beta(d^2+v))`, `u_m=sigmoid(a-beta v)`,

`pi_e=f+b u_e`, and `pi_m=f+b u_m`.

Substituting into (3) gives the analytic expression

**(11)** `m'(0)=4 beta d^2 b u_e(1-u_e)/(2 pi_e+pi_m)`.

At the center, this derivative is nonnegative, so stability changes at `m'(0)=1` for the positive step size used here. The *formula* is analytic; the decimal solutions below are numerical.

| beta | m'(0) | F'(0), eta=.05 | central fixed point |
|---|---:|---:|---|
| 1.5 | 0.6509062601 | 0.9825453130 | locally stable |
| 3 | 1.5844493964 | 1.0292224698 | locally unstable |
| 5 | 0.8296124345 | 0.9914806217 | locally stable |
| 8 | 0.0758248933 | 0.9537912447 | locally stable |

Bisection in the independently specified brackets `[1.5,3]` and `[3,5]` locates central stability crossings at **beta=1.9518425028502513** and **4.691120421725749**. The central point loses and subsequently regains local stability in this example. These values depend on preference scale, noise, response intercept, floor, and span. They are not universal AI thresholds.

At beta3, root calculations locate stable noncentral fixed points `wbar=±0.4538513332212661`, each with `m'=0.433751186578305` and `F'=0.9716875593289152`. The zero fixed point is unstable. At exactly zero and without noise or perturbation, the deterministic recursion remains exactly zero; local instability means small departures can grow, not that exact symmetry moves by itself.

At beta8, verified roots include the stable center, stable outer roots `±0.9255883072331241` with `F'=0.9556331921485759`, and intervening unstable roots `±0.5319972336839589` with `F'=1.0476978098600664`. Thus restoring local central stability does not ensure uniqueness or remove all outer attractors. Bracketed root finding establishes these roots and their local derivatives; it is not a proof that no additional roots or tangencies exist.

For the positive stable beta3 branch, the controlled influence measures are:

| Group, preference | sampling share q_g | one-step direct eta*q_g | frozen-weight persistent q_g | closed-loop local persistent q_g/(1-m') |
|---|---:|---:|---:|---:|
| 0, -1 | 0.02059805 | 0.00102990 | 0.02059805 | 0.03637632 |
| 1, 0 | 0.50495257 | 0.02524763 | 0.50495257 | 0.89175033 |
| 2, +1 | 0.47444938 | 0.02372247 | 0.47444938 | 0.83788146 |

The negative branch interchanges the two extreme groups. These quantities are post-hoc deterministic diagnostics from an exactly symmetric parameter setting, not estimates from the original 20 jittered worlds. They provide an operational measure of feedback influence but do not establish the broader retained-knowledge/lost-responsiveness hypothesis.

## 7. Independent verification and artifacts

`theory_verify.py` is self-contained and does not import or modify `run_study.py`. It saves `theory_verification.json` and checks:

- the general covariance derivative against central finite differences in 200 randomly generated cases, including unequal population weights;
- the actual preference-shift derivative, including participation mediation, against finite differences;
- the exponential response identity against a separate finite-difference calculation;
- both stable beta3 branches' implicit feedback-only equilibrium derivatives against independently resolved roots at `h=±1e-5`;
- the analytic central derivative, bracketed crossings, and reported numerical fixed points.
- the monitoring covariance identity and its restricted sign condition under a common decreasing participation function.

All checks pass at the stated numerical tolerances. The covariance and actual-preference finite-difference errors are below `3e-9`; equilibrium-response derivative error is below `5e-10`. Numerical checks support the algebra and implementation but do not replace the derivations or prove global behavior.

## 8. Manuscript-ready English: Methods

### Post-hoc analysis of the conditional mean map and feedback influence

To explain the simulated dynamics, we added an analytical extension after the original experiment. Let the fixed population weights be rho_g, the accepted-feedback probabilities be q_g(w)=rho_g pi_g(w)/sum_h rho_h pi_h(w), and the feedback-mixture mean be m(w)=sum_g q_g(w) theta_g. The uncorrected learner has conditional mean update F(w)=(1-eta)w+eta m(w). Differentiating the normalized weights yields m'(w)=Cov_q[theta_g, partial_w log pi_g(w)]. A fixed point wbar satisfies m(wbar)=wbar and is locally asymptotically stable for the deterministic map when |1-eta+eta m'(wbar)|<1. This analysis concerns the conditional mean map; it does not equate its iterations with the full stochastic expected trajectory or establish stochastic convergence.

We also defined a local feedback-influence diagnostic distinct from group loss. A small persistent intervention h shifts one group's submitted feedback mean while keeping the objective and the baseline participation law fixed; participation may still change indirectly through the resulting action. The immediate conditional response is eta q_j(w). With participation weights frozen indefinitely, the equilibrium response is q_j. On a smooth stable branch with action-dependent participation, implicit differentiation gives d wbar/dh=q_j(wbar)/[1-m'(wbar)]. These are controlled feedback-only derivatives. If an intervention also changes true preferences or access, its direct effect on participation must enter the numerator separately.

For an exactly symmetric diagnostic with theta=(-1,0,1) and equal access, zero is always a fixed point. Writing u_e=sigmoid[2-beta(1+v)], u_m=sigmoid(2-beta v), pi_e=.02+.96 u_e and pi_m=.02+.96 u_m gives m'(0)=4 beta(.96)u_e(1-u_e)/(2 pi_e+pi_m), where v=.2^2/3. We numerically located stability crossings and nonzero roots, checked the general derivative by finite differences, and verified local intervention derivatives by resolving perturbed fixed points. These diagnostics were exploratory and were not part of the original locally recorded simulation plan.

For any fixed action, the population-minus-feedback monitoring gap also satisfies G=-Cov_rho(pi_g,L_g)/E_rho[pi_g]. If all groups share the same decreasing participation function of loss, the covariance is nonpositive and G is nonnegative. Group-specific access friction removes that general sign guarantee. The identity holds independently of the learning rule and explains why correcting the action's training objective need not correct a participant-weighted evaluation.

## 9. Manuscript-ready English: Results

### Conditional mean dynamics explain instability and unequal feedback influence

In the exactly symmetric diagnostic, the derivative of the conditional mean update at zero was 0.982545 at beta1.5 and 1.029222 at beta3. Thus the central point was locally stable in the former setting and unstable in the latter, despite equal access friction. At beta3, stable noncentral fixed points occurred at ±0.453851. This provides a mechanism by which small departures from symmetry can lead to different attracting branches; it does not attribute deterioration to an intrinsic group label. Numerical crossings of the central stability boundary occurred at beta≈1.951843 and 4.691120. The center was stable again at beta5. At beta8, a stable center coexisted with stable outer roots at ±0.925588 and intervening unstable roots at ±0.531997. Consequently, local central stability and uniqueness are distinct, and exclusion should not be assumed to increase monotonically with the participation-sensitivity parameter.

At the positive stable beta3 branch, the extreme groups' accepted-feedback shares were 0.020598 and 0.474449. Their immediate feedback-only influence derivatives were 0.001030 and 0.023722, respectively; their persistent local equilibrium derivatives were 0.036376 and 0.837881. The negative branch exchanged the extreme groups' roles. The common equilibrium gain increased the absolute local effect of feedback relative to frozen sampling weights, while the ratio of group influences remained determined by their sampling shares at that point. These analytically defined influence measures supplement the loss outcomes and should not be interpreted as learned knowledge, empathy, or evidence from human stakeholders.

## 10. Manuscript-ready English: Limitations and positioning

The mean-map extension characterizes local deterministic stability and controlled feedback influence in a specified scalar system. A stable deterministic branch need not characterize the stationary behavior of every finite-batch stochastic learner, and numerical root searches do not prove a complete global bifurcation diagram. The intervention shifts feedback content without changing underlying preference parameters; actual changes in preferences or access have additional participation-mediated effects. The stability crossings depend on the chosen preference scale and participation function and are not universal thresholds. We present the identities as standard local analysis applied to an auditable example, without claiming priority for feedback-induced instability or a general theory of AI development.
