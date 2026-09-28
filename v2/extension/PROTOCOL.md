# Exploratory extension protocol, version 2.0.0

## Status and objective

This protocol is written **after the original simulation results and two rounds of critical review were inspected**. It specifies a new exploratory extension before executing its new trajectories. It is not an external preregistration, held-out confirmation, or a claim that these questions were specified before the original results. Original `study/` files are read-only inputs and must not be changed.

The purpose is to explain heterogeneity and conditional branch selection, challenge dependence on one participation law, and quantify the consequences of explicitly specified propensity errors and recruitment assumptions. No human, biological, clinical, or language-model experiment is performed. No attempt will be made to select parameters after seeing the extension results in order to favor a hypothesis. All configured cells and contrary results will be retained.

## Frozen inputs and pre-execution record

`config.json`, this file, and `run_extension.py` will be SHA-256 hashed in `results/execution_start.json` before calculations begin. Original configuration, run/world summaries, trajectories and preference-world file will also be hashed. The final report will identify software versions, counts, timings, checks and output hashes. A completed results folder will not be overwritten.

## Analysis A: original heterogeneity and geometry

Read all original main-scenario beta=3 endogenous/static run rows. Calculate each seed's paired group losses/regret and each world's mean contrast; retain all 20 worlds and all 200 seed contrasts. Reproduce the originally declared bootstrap using the original bootstrap seed. Describe the two observed negative worlds without selecting new worlds. Record theta, spacings, initial group losses/participation, initial conditional drift, deterministic endpoint/trajectory, and all numerically detected fixed points in the convex hull of group means. Draw no global completeness conclusion from a sign-change root grid. Save all original world trajectories relevant to both conditions for plotting.

## Common model

Three equally weighted groups, uniform preference noise of half-width 0.2, shared action, step size 0.05, and 96 accepted preferences per update are unchanged. Expected group loss is `(w-theta_g)^2 + 0.2^2/3`; population regret is `(w-mean(theta))^2`. Endpoint statistics average the last 50 **pre-update** decision rounds of 1,000 new updates. A final post-update action is separate. The extension does not overwrite the original 250-update primary result.

## Analysis B: exact symmetry and initialization

Use theta=(-1,0,1), zero access friction, the original sigmoid law, beta=1.5,3,8, and initial actions 0, +/-0.01, +/-0.25. Also include +/-0.75 **specified here before execution** to probe the outer basins suggested by the already observed beta=8 root structure. Run endogenous and static conditions for 50 paired random seeds per cell. Static participation is frozen at that cell's initial action, not forcibly at zero. Report all three groups, action, regret, realized/expected feedback shares, endpoint branch signs, and deterministic paths. Exactly symmetric noiseless initialization at zero stays there even when locally unstable; distinguish that identity from behavior under finite feedback noise. The different initializations use the same random draw stream, without antithetic mirroring; nominal runs are correlated within seed and no 20-world population-bootstrap inference applies to this single synthetic world.

## Analysis C: participation-law challenge

Use the original 20 theta worlds, the main friction vector (1.2,0,0), 10 fresh paired seeds per world, optimum initialization, and strength anchor 3. Compare the original sigmoid law with a bounded monotone exponential law. Let `a_g=sigmoid(2-c_g)` and `k_g=b*(1-a_g)`. Define

`pi_sigmoid(L,c;b)=0.02+0.96*sigmoid(2-c-b*L)`

`pi_exp(L,c;b)=0.02+0.96*a_g*exp(-k_g*L)`.

Both probabilities and their first loss derivatives match at **L=0**, separately for each group. This is a mathematical boundary reference, not necessarily an attainable expected group loss because preference noise has positive variance. They need not match at positive losses or along trajectories. The parameter b is a **local matching anchor**, not an assertion that numeric beta has equivalent global meaning across laws. This one contrast probes shape sensitivity; it is not a broad robustness survey or an empirical calibration.

## Analysis D: correction errors and invitation cost

For each family, compare endogenous unweighted, static, exact quota, self-normalized IPW with true probabilities, IPW using probabilities computed with access friction set incorrectly to zero, and IPW using half the true sensitivity anchor but the correct friction. Estimated weights remain positive. These are deterministic, structured misspecification scenarios, **not propensity estimates fitted from observed recruitment data**. They are selected before execution; no successful setting will be preferred afterward. Compute effective sample size `sum(weights)^2/sum(weights^2)`.

At each update keep probabilities fixed during recruitment. For natural collection, prospective groups are invited uniformly; unconditional success probability is mean(pi), accepted groups have probability pi/sum(pi), and invitations until 96 successes have distribution `96 + NegBin(96, mean(pi))`. For quota collection invite each group separately until 32 successes; sum `32+NegBin(32,pi_g)` across groups. Generate stopping counts independently of accepted values; this is an equivalent conditional sampling construction for the declared independent invitation model. Track expected and simulated realized costs, both endpoint and cumulative, and their difference relative to the model's negative-binomial variance. Acceptance budgets remain matched; invitation budgets do **not**. This study does not measure real recruitment costs or establish a fixed-budget policy ranking.

For all conditions record participant-weighted expected monitoring loss, population loss, and their gap; true-IPW learning does not automatically reweight the monitoring statistic.

## Randomness, inference and checks

Use seeds in the frozen config. Within each main world/seed and each exact-symmetric seed, reuse uniform group-selection draws and preference noise across conditions, laws, strengths and initializations. Use a separate invitation RNG so acquisition-cost sampling never changes preference trajectories. Quota uses 32 observations per group and the same additive noise batch. Save run-level and world-level endpoints and world-averaged checkpoints every 10 updates.

For the main-family comparison, average seeds within the original 20 worlds and use paired world-bootstrap intervals with 10,000 resamples. All new intervals are exploratory/descriptive and not multiplicity-adjusted. For the single exact-symmetric world report seed distributions/counts rather than treating seeds as independently sampled environments. Negative cases are reported, not removed.

Checks: probabilities positive, finite, at most one and normalized after conditioning; exact quotas; risk decomposition; true weighting moment identity; analytic participation derivatives versus finite differences; noiseless mirror symmetry; deterministic exact-zero symmetry; actual counts at least accepted counts; planned run count; expected-vs-realized invitations standardized using conditional negative-binomial variance; old input hashes unchanged. A cost discrepancy is diagnostic, not grounds for silently discarding a run. Checks cannot prove external validity or originality.

## Interpretation limits

Root grids detect sign-changing fixed points, not all tangencies. Local deterministic slopes are not global stochastic convergence theorems. Actual new outputs will determine which direction/branch statements survive. More trials do not establish a general law, knowledge retention, responsiveness, fairness in real AI, or deployment feasibility. Report all configured comparisons, including reversals, failures of corrections, and alternative-law differences.
