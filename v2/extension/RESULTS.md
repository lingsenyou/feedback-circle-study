# Executed exploratory extension: results and interpretation

This extension was designed after inspection of the original results and critical review. Its protocol, configuration and code were hashed before its new execution. It is not externally preregistered and does not replace the original 250-update primary result. Original study files were not modified.

Execution completed at **2026-09-28T05:02:00 UTC**. The run produced **4,500 new stochastic trajectories across 54 cells**, each with 1,000 updates and 96 accepted preferences per update. This is computational accounting, not an independent sample size: the main-family comparison uses the original 20 preference worlds and 10 fresh paired seeds each; the exact-symmetric experiment uses one fixed world and 50 paired seeds per cell. All new intervals are descriptive world-bootstrap intervals.

## What the extension changes scientifically

The original positive mean is retained. However, neither the identity of the disadvantaged group nor branch selection is universal. Exact symmetry exhibits initialization- and noise-dependent branching, and a more sensitive participation rule can have a locally stable center while also retaining distant stable branches. The ideal correction result is substantially weakened by two explicitly specified propensity errors. One alternative participation law preserves a positive average selection-amplification effect but changes both effect size and the direction in the two original counterexample worlds.

These results support a more precise paper about **conditional selection dynamics, branch dependence, and limits of ideal weighting**. They do not establish an AI developmental limit, learned knowledge-action dissociation, a generally new fairness mechanism, or a deployable correction algorithm.

## A. All original worlds and the two counterexamples

Re-reading the original run table exactly recovers the primary contrast: **0.7337720789610263**, bootstrap interval **[0.5158086270726144, 0.8971166793550999]**. Eighteen world means are positive and worlds 10 and 11 are negative; all ten original seed contrasts in each of those two worlds are negative.

| Quantity | World 10 | World 11 |
|---|---:|---:|
| theta0 | -1.021158 | -0.979564 |
| theta1 | -0.106224 | -0.129132 |
| theta2 | 1.128794 | 1.087834 |
| left preference spacing | 0.914933 | 0.850432 |
| right preference spacing | 1.235018 | 1.216966 |
| population-optimal starting action | 0.000471 | -0.006954 |
| initial selected-mixture mean | -0.024014 | -0.036908 |
| initial mean drift | -0.024484 | -0.029954 |
| original endogenous-minus-static group-0 loss | -0.485208 | -0.513810 |
| noiseless endpoint after 5,000 updates | -0.337170 | -0.377906 |
| original group-2 loss, endogenous | 2.078849 | 2.134844 |
| original group-2 loss, static | 1.343219 | 1.280339 |

The center group's mean lies to the left of the population optimum and is closer to group 0 than to group 2. Although group 0 has additional access friction, the initial accepted mixture drifts left. The endogenous recursion then approaches a left stable branch, reducing group-0 loss and increasing group-2 loss relative to static selection. This explanation is calculated from the model's actual preference geometry, not inferred from a socioeconomic label.

Numerical root finding detects two stable branches in both negative worlds, with an intervening unstable root. World 10: stable -0.337170 and 0.429177, unstable 0.104361. World 11: stable -0.377906 and 0.401430, unstable 0.091643. The declared optimum starts on the left side of those separating roots. Root grids do not prove completeness at tangencies or global stochastic basin boundaries.

Every world's geometry, seed contrasts, original trajectories, deterministic path and numerically detected roots are retained, so the two cases are displayed within the complete 20-world result rather than selected as a substitute for the mean.

## B. Exact-symmetric branching

Use theta=(-1,0,1), no access friction and the original sigmoid law. Static selection is frozen at **each cell's own initial action**, while endogenous participation keeps updating. Initial actions are 0, +/-0.01, +/-0.25 and +/-0.75; the latter pair was explicitly specified before extension execution to probe outer basins at beta=8.

| beta | Numerically detected locally stable roots | Other detected roots | Observed endogenous outcomes after 1,000 updates |
|---|---|---|---|
| 1.5 | 0 | none detected | All 50 seeds in all seven initializations ended within +/-0.2. |
| 3 | +/-0.453851 | 0, unstable | At initial 0: 20 seeds on the left, 30 on the right. At -0.01: 40 left, 10 right. At +0.01: 10 left, 40 right. At -0.25/-0.75: all 50 left. At +0.25/+0.75: all 50 right. |
| 8 | 0 and +/-0.925588 | +/-0.531997, unstable | All 50 seeds from initial 0, +/-0.01 or +/-0.25 ended centrally. All 50 from -0.75 went left; all 50 from +0.75 went right. |

Here left/right are descriptive final-action buckets below -0.2/above +0.2; central is the interval between those cutoffs. These counts describe 50 specified synthetic draws, not human or environmental frequencies. Common random numbers correlate cells. The noiseless exactly-zero trajectory remains zero at every beta by symmetry, including beta=3 where that fixed point is locally unstable. Finite feedback noise breaks that exact identity.

All three group losses are saved. For example, at beta=3, initial 0, mean endpoint group losses are 1.397475, 0.217597 and 1.037719; the unequal left/right averages reflect the 20/30 branch split in the finite seed sample, not an intrinsic preference for a group label. At beta=8, initial +0.75, they are 3.718855, 0.868926 and 0.018997: local stability of the center does not imply attraction from all initial states.

## C. A locally matched exponential participation law

Let a_g=sigmoid(2-c_g), k_g=b(1-a_g), and define pi_g=0.02+0.96*a_g*exp(-k_g*L_g). At L=0, this matches the original sigmoid's participation probability and first loss derivative for each group. L=0 is a mathematical reference, not an attainable expected loss with the specified positive noise variance. Matching there does not equate either law at other losses; the anchor b=3 must not be described as globally equivalent sensitivity.

Fresh 1,000-update main-world results:

| Participation law | Endogenous-minus-static group-0 loss | Descriptive 95% interval | Positive/negative worlds |
|---|---:|---|---|
| Original sigmoid | 0.736484 | 0.517553 to 0.905720 | 18 / 2 |
| Locally matched exponential | 0.451047 | 0.410066 to 0.495010 | 20 / 0 |

The mean direction survives this one shape challenge. The two original negative worlds become positive under the exponential law: their endogenous actions are approximately +0.3439 and +0.2829, instead of approximately -0.3298 and -0.3798 under sigmoid in the new long runs. Therefore, even local matching of participation levels/slopes at one reference loss does not preserve global branch selection. This comparison is evidence of model sensitivity, not proof of general robustness.

## D. Propensity misspecification, monitoring and recruitment cost

The two misspecifications were fixed before execution: (i) pretend access friction is zero, and (ii) use half the true sensitivity anchor while retaining the correct friction. They are deliberately specified model errors, not propensities estimated from recruitment observations. All true sampling laws are unchanged when the estimator is misspecified.

For the matched exponential family, setting friction to zero changes both the zero-loss amplitude a_g and the derived decay rate k_g. Consequently, the same named misspecification is not an identical probability perturbation across families; compare it within each family rather than attributing their difference solely to an algorithmic property of IPW.

| Condition | Sigmoid regret | Exponential regret | Sigmoid expected invitations/item | Exponential expected invitations/item |
|---|---:|---:|---:|---:|
| Endogenous unweighted | 0.218120 | 0.139302 | 1.9834 | 1.7649 |
| Static | 0.022503 | 0.040390 | 2.4474 | 1.7308 |
| Balanced quota | 0.000003735 | 0.000003735 | 5.1030 | 2.1886 |
| True-propensity IPW | 0.000713 | 0.000298 | 2.4318 | 1.7310 |
| IPW omitting friction | 0.050245 | 0.092701 | 2.1420 | 1.7554 |
| IPW with half sensitivity | 0.101813 | 0.019617 | 2.0601 | 1.7375 |

The identical quota regrets across laws are a paired-draw identity: exact group counts and the same additive noise produce the same decisions, while recruitment costs differ. This is not independent confirmation by a second learner.

Under the sigmoid law, omitting access friction increases group-0 loss relative to true IPW by 0.481147 (descriptive interval 0.474306 to 0.487249); halving sensitivity increases it by 0.573577 (0.370342 to 0.718750). Under the exponential law, corresponding differences are 0.703041 (0.643146 to 0.767758) and 0.288899 (0.248343 to 0.332641). The amount of deterioration depends on the family and the error. These particular misspecifications still improve mean population regret relative to unweighted endogenous feedback; they do not show that all erroneous weighting makes outcomes worse than no correction.

True-IPW mean effective sample sizes are 47.38/96 for sigmoid and 76.22/96 for exponential. Participant-weighted monitoring still understates population loss after true-IPW learning: mean monitoring gaps are 0.388302 and 0.173924, respectively. Weighting the learning estimate does not automatically alter the monitoring population.

Invitations were also **simulated**, using an independent negative-binomial stopping count conditional on each round's participation probabilities. Natural sampling uniformly invites prospective groups until 96 acceptances; quota sampling targets each group until 32 acceptances. Across the 54 cells, cumulative actual/expected cost ratios range from 0.999196 to 1.000790; the largest absolute standardized difference is 3.16. No cells were discarded. These checks support the implementation of the declared recruitment model. They do not measure real recruitment effort and do not compare policies at equal invitation budgets.

## Verification and provenance

- Original source hashes are unchanged.
- Probability normalization error <=3.34e-16; risk decomposition error <=5.59e-16; true-IPW population-moment error <=2.33e-16.
- Analytic fixed-point derivatives agree with finite differences within 1.05e-10; noiseless mirrored endpoints agree exactly to stored precision.
- A separate scalar-loop verifier, without importing the runner, independently re-executed six selected 1,000-step trajectories across both laws, misspecified weighting, counterexample geometry and symmetry cases. Maximum discrepancy was 4.45e-16. It also checked all-run shares, ESS, invitation counts and exact quota cross-law equality. This is a spot-check audit plus invariants, not a second complete execution of every new trajectory.
- Full details: `results/execution_start.json`, `results/summary.json`, `results/checks.json` and `verification.json`.

## What is retained, narrowed or rejected

**Retained:** the original conditional positive average; the usefulness of a static control; selection-amplified deviation from a fixed population objective in two specified laws; oracle weighting/quota as ideal reference procedures; separation of learning and monitoring objectives.

**Narrowed:** group-specific disadvantage depends on preference geometry and branch selection, not access friction alone; larger sensitivity does not imply monotonic exclusion or a single stability regime; correction effects depend strongly on correctly representing selection and resource assumptions.

**Rejected by these counterexamples:** a claim that endogenous feedback invariably worsens group 0 relative to static selection; a claim that re-stabilizing the center ensures convergence from every initialization; a claim that the numerical beta value denotes equivalent global behavior across different participation laws.

**Still untested:** learned knowledge retention, direct causal responsiveness to a correction, foundation-model behavior, human social mobility, clinical utility, empirical participation laws and fixed-invitation-budget optimality. The extension does not justify claiming those findings.

## Files for scientific figures and tables

- `results/original_world_geometry.csv`: all 20 paired primary world effects, theta, drift and geometry.
- `results/original_primary_run_contrasts.csv`: 200 paired seed contrasts, all group outcomes.
- `results/original_primary_trajectories.csv`: original measured time courses for every world, both conditions.
- `results/deterministic_trajectories.csv`: main-world geometry and exact-symmetric paths, through 5,000 noiseless updates.
- `results/fixed_points.csv`: numerical roots, local slopes and derivative checks.
- `results/run_metrics.csv`: every new run, all group losses/shares, ESS, final actions, cumulative cost.
- `results/world_metrics.csv` and `results/trajectories_world.csv`: new seed-averaged outcomes and paths.
- `results/symmetric_seed_summaries.csv`: branch buckets and all-group results for each symmetric cell.
- `results/condition_estimates.csv` and `results/contrasts.csv`: descriptive world-bootstrap tables for main-law comparisons.
- `results/invitation_cost_checks.csv`: actual-versus-expected simulated acquisition costs for every cell.

Candidate figure structure: (1) all-world primary effect plot paired with the two negative-world action paths and preference geometry; (2) exact-symmetry initialization versus endpoint plot at beta 1.5/3/8, with all seeds and stable/unstable roots; (3) law/correction regret and group-loss panels with recruitment effort and ESS shown separately. These should be driven directly by saved outputs. No plots have been generated by this subtask.

## Reproduction

From this directory, use `python run_extension.py --output results_reproduced`, then compare numeric CSV files with the supplied run. Execution timestamps and timing fields will differ. Use `python verify_extension.py` for the independent selected-trajectory checks against the supplied `results` directory. The original `../../study/results` inputs must remain available at that relative location; their hashes are listed in the pre-execution record.
