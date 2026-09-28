# Actual results of the synthetic mechanism simulation

The main execution completed all 7,200 planned trajectories (20 worlds, 10 paired training seeds, three scenarios, three feedback-sensitivity values, and four conditions). The machine-recorded execution interval was 2026-09-23 04:35:02–04:35:05 UTC. The core simulation and output generation took 2.655 seconds in this vectorized implementation. These counts do not represent participants, biological experiments, independently observed users, or language-model calls. The 20 worlds are the inferential replication units after averaging the ten seeds within each world.

The protocol, configuration, and code hashes were recorded before main execution in `results/execution_start.json`. This was a local record, not public preregistration. All planned cells and negative controls were retained.

## Primary result

In the main scenario at beta = 3, the final-50-round group-0 squared-error risk was 2.0785 with endogenous feedback and 1.3447 with the static-feedback control. The paired mean difference was **0.7338 (95% world-bootstrap interval 0.5158 to 0.8971)**. This is a synthetic squared-preference-unit difference, not a percentage or a clinical outcome. The static control freezes selection probabilities at the initial complete-information optimum; the contrast isolates allowing action-dependent participation to evolve under the specified model.

## Main scenario at beta = 3

| Condition | Group-0 risk | Population regret | Expected group-0 feedback share | Monitoring gap | Expected invitations per accepted observation |
|---|---:|---:|---:|---:|---:|
| Endogenous | 2.078482 | 0.215062 | 0.043066 | 0.639878 | 1.985742 |
| Static | 1.344710 | 0.022380 | 0.085880 | 0.432577 | 2.447368 |
| Group quota | 1.054503 | 0.000003799 | 0.333333 | approximately 0 | 5.103594 |
| Known-propensity self-normalized IPW | 1.075195 | 0.000808228 | 0.082941 | 0.388678 | 2.432439 |

All entries are means across worlds after seed averaging. Full world-bootstrap intervals for each entry are in `results/condition_estimates.csv`. Population regret is excess equal-population risk relative to the complete-information optimum, analytically equal to squared displacement of the action from the mean preference. The monitoring gap is fixed-population risk minus risk weighted by the feedback selection probabilities. Positive values mean feedback-weighted monitoring looks better than evaluation of the fixed population. The quota monitoring gap is zero by construction.

Endogenous minus static population regret was 0.192682 (95% interval 0.175200 to 0.208552). Endogenous minus quota group-0 risk was 1.023979 (0.752269 to 1.225218). IPW minus endogenous group-0 risk was -1.003288 (-1.199478 to -0.736481). These are secondary descriptive intervals, without multiplicity adjustment. IPW did not exactly reproduce quotas: its group-0 risk exceeded quota risk by 0.020691 (0.013122 to 0.028665), consistent with the finite-batch and variance limitations of self-normalized correction in this experiment. The simulation alone does not identify which component explains that residual.

## Scope-restricting controls

At beta = 0, endogenous and static conditions had identical paired trajectories and endpoints in every scenario. In the no-conflict scenario, endogenous-minus-static group risk and population-regret differences were exactly zero for every beta. In that case, group selection cannot alter the distribution of target preferences under the shared-noise pairing. These are model-based negative controls, not equivalence findings about external systems.

In the symmetric-access scenario at beta = 3, endogenous minus static population regret was 0.212413 (0.193726 to 0.228602); group-0 risk difference was 0.482458 (0.147481 to 0.800056). Group 0 has no special access barrier in that scenario and must be called a reference group rather than the low-access group. The heterogeneous preference centres still differ across generated worlds.

## What the results support

Under the specified participation function, dynamic selection can amplify population-objective drift beyond that produced by a frozen, biased feedback distribution. Matching accepted feedback counts does not remove that mechanism. Collection quotas and correction with known propensities greatly reduced objective drift in this model. Quotas required greater expected acquisition effort, and successful action correction did not by itself correct raw feedback-weighted monitoring.

## What the results do not establish

This study does not test knowledge retention, preference-prediction retention, human social mobility, language models, increasing AI capability, biological systems, or clinical care. Complete population preferences are available to the oracle by assumption. The adaptive learner begins at the exact optimum, so the experiment isolates drift rather than modeling initial training. The functional form of participation, synthetic loss scale, equal-group objective, and within-group noise are assumptions. The observed mechanism is preventable in this model and is not evidence of an unavoidable general-intelligence bottleneck.

## Verification

All runtime invariants passed. The saved-output audit independently recomputed metric identities, seed-to-world aggregation, the primary bootstrap interval, protocol/configuration/code hashes, and the terminal action from a closed-form sum of the stored actual feedback batches. The primary interval recalculation error was zero; the closed-form replay error was 1.11 x 10^-16. See `results/checks.json` and `results/independent_audit.json`.
