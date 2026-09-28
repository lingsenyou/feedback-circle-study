# Analysis plan fixed before the main simulation

This is a synthetic mechanism simulation, not a study of people, clinical care, biological systems, or large language models. This file and `config.json` are timestamped and hashed locally before the first main execution. This is not public preregistration. Results will be reported irrespective of their direction.

## Question and estimand

Does experience-dependent selection into feedback alter an adaptive scalar policy relative to a fixed, equally weighted three-group population objective? The predesignated low-access group is group 0 in the main and no-conflict scenarios. It is a reference group, without a special access barrier, in the symmetric scenario.

In each of 20 independent worlds, group preference centres are theta = (-1, 0, 1) plus independent Uniform(-0.15, 0.15) jitter. Individual feedback preferences are y = theta_g + Uniform(-0.2, 0.2). The global action w is initialized at the exact population optimum, the mean of the three centres. Every group shares squared-error loss, and the declared population objective always weights groups equally. Exact expected group risk is (w - theta_g)^2 + 0.2^2/3. The full-information optimum is a mathematical benchmark and an assumption; it is not a learned knowledge score.

## Participation and learning

Participation propensity is pi_g = 0.02 + 0.96 sigmoid(2 - friction_g - beta [(w - theta_g)^2 + 0.2^2/3]). Friction is (1.2, 0, 0) except in the symmetric scenario, where it is zero. The three candidate populations are equally sized. Conditional on a feedback observation being accepted, its group probabilities are pi_g / sum(pi). Each round uses exactly 96 accepted observations; this is conditional sampling, not observed recruitment of human participants. Feedback values have identically distributed independent within-group noise.

The learner uses w_next = 0.95 w + 0.05 batch_estimate. There are 250 updates, with 10 independent training seeds per world. The same pre-generated group-draw uniforms and preference-noise uniforms are reused across paired conditions, betas, and scenarios. The algorithm, noise scale, accepted feedback count, and update count are fixed across conditions. Acquisition costs are not equalized: expected invitations per accepted observation are reported separately under the specified propensity model.

Four conditions are run: (1) endogenous, uncorrected feedback; (2) static feedback, with propensities frozen at the initial optimum, removing the action-to-participation loop; (3) a quota of exactly 32 observations per group, requiring additional collection effort; and (4) endogenous feedback with self-normalized inverse-probability weighting using the known true group selection probabilities. Self-normalized IPW has finite-batch bias and is not claimed to be exactly unbiased. It assumes correctly known propensities and positivity; it is not a deployable real-world solution without further estimation.

The scenario grid includes main, symmetric, and no_conflict. In no_conflict, all group centres equal the world-specific mean of the original three centres. Beta is 0, 1.5, or 3. Total runs: 20 worlds x 10 seeds x 3 scenarios x 3 beta values x 4 conditions = 7,200. All combinations will be reported.

## Outcomes and analysis

Decision risks are measured before each round's update. Each run's endpoint is its mean over the final 50 decision rounds (rounds 201–250, or zero-based indices 200–249). The primary contrast is main scenario, beta 3: group 0 risk in endogenous minus static feedback. Positive values indicate worse service under the endogenous loop. This single contrast was chosen before main execution. All remaining contrasts are secondary or exploratory, and their intervals are descriptive rather than multiplicity-adjusted hypothesis tests.

Secondary outcomes are every group's risk; equally weighted population risk and regret relative to the oracle; expected and realized group 0 feedback shares; and monitoring bias. The monitoring gap is fixed-population expected risk minus risk weighted by the current feedback selection distribution. Positive gaps mean that feedback-weighted risk looks better than fixed-population risk. A sample-based monitoring gap is also reported using actual submitted preferences and the current action. The quota condition has zero population-versus-expected-feedback gap by construction; that identity is not an empirical discovery.

Training seeds are averaged within each world. Means and percentile 95% bootstrap intervals then resample the 20 worlds, with 10,000 bootstrap samples. Contrasts use paired world differences. Worlds, not rounds or feedback observations, are the inferential replication units. Uncertainty concerns these specified synthetic world and training distributions, not populations of people or AI architectures. No superiority, harm threshold, power calculation, or equivalence margin is asserted after seeing results.

## Checks and refutation boundaries

At beta 0, endogenous and static conditions must agree exactly under paired random numbers. Risk decomposition must satisfy population risk = oracle risk + (w - mean(theta))^2. No-conflict group risks must coincide. Group probabilities must sum to one, and quota counts must equal 32 per group. IPW numerator and denominator expectation identities are checked, without claiming exact unbiasedness of the self-normalized ratio. An actual endogenous sequence of realized feedback batches is stored and replayed; it must reproduce the online action to machine precision.

An endogenous-minus-static estimate near zero or negative would fail to support the proposed direction for the primary setting; uncertainty must remain visible. If correction restores the population objective, that supports a selection-and-estimation explanation rather than an unavoidable intelligence bottleneck. The experiment cannot establish preserved knowledge alongside lost responsiveness, effects in language models, effects of AI scale, human social-mobility claims, or biological/clinical relevance. The participation function and utility trade-offs are modeling assumptions. Starting at the oracle isolates drift away from a declared objective and does not model initial learning.

## Reproducibility

All run-level endpoints, world-level means, condition summaries, paired contrasts, aggregated trajectories, exact configuration, code hash, protocol hash, checks, elapsed execution time, and actual run counts are saved. An illustrative full feedback sequence is saved for exact replay. Remaining sequences are deterministically regenerable from the configuration and code. No real personal information or credentials are used.
