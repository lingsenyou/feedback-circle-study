# Feedback selection and local stability in adaptive decision systems

## Abstract

An adaptive system learns from people who participate, while its decisions may affect a wider population. We study the resulting mismatch with a reproducible scalar model and local dynamical analysis. The original experiment compared outcome-dependent participation with frozen selection, balanced collection, and known-probability correction across 20 parameter worlds and ten paired seeds. The primary group-specific loss contrast was 0.734 (95% world-bootstrap interval 0.516 to 0.897), but two of the twenty worlds had the opposite sign. An exploratory extension executed 4,500 additional trajectories, testing initial states, participation-law shape, and misspecified correction weights. In an exactly symmetric case, equal access did not prevent local instability: the central conditional-mean fixed point lost and later regained stability as participation sensitivity increased, with stable outer fixed points coexisting with the stable center at beta = 8. A matched exponential participation law retained a positive average loss contrast but changed its magnitude and heterogeneity. Omitting access friction from correction weights increased population regret from 0.000713 to 0.050245 in the extended sigmoid experiment. We derive local feedback-influence and monitoring-gap identities to separate sampling coverage, decision influence, and outcome loss. The study supplies an auditable mechanism analysis with explicit counterexamples and assumption sensitivity. It does not establish learned knowledge retention, language-model behaviour, or a developmental limit of AI.

Keywords: adaptive decision systems; feedback selection; participation bias; local stability; monitoring bias; simulation

## Introduction

Repeated adaptation can change who supplies the evidence used in the next update. If people experiencing higher loss participate less, training on the remaining feedback may move a shared decision away from the population it was intended to serve. The relevant population objective can remain fixed even while the feedback distribution changes. Distinguishing these two distributions is essential when assessing whether adaptation improves service.

The motivating idea comes from a distinction in human social life: knowing about other people's circumstances is different from continuing to receive consequential correction from them. A change in one's social setting may alter which concerns repeatedly influence decisions, even without erasing earlier knowledge. This is a thought experiment, not evidence that social mobility reduces empathy or that AI follows human developmental stages. Homophily can also facilitate beneficial behaviour, as an experimental study of health-behaviour adoption showed.[1] For AI, the useful question is structural: whose feedback can reach and change an adaptive system? We use feedback circle to describe participation, acceptance, and weighting during a specified period, without assigning feelings or social class to a model.

Performance-dependent participation and representation disparity have established theoretical precedents.[2,3,4,5,6] We examine a transparent special case to distinguish baseline selection from its dynamic amplification, identify when an average group-specific effect conceals counterexamples, and separate local instability from unequal access. Known-probability correction and balanced collection provide reference conditions. Additional analyses distinguish feedback influence from group loss and explain why correcting learning need not correct participant-weighted monitoring. The contribution is a reproducible combination of controlled comparisons, local analysis, and explicit sensitivity tests, rather than a new alignment algorithm or a claim of priority for feedback bias.

{{FIGURE1}}

Figure 1. The conceptual feedback circle. Access, submission, and acceptance can filter participation before feedback changes a system. Outcomes may affect subsequent participation. The schematic is broader than the implemented model, which represents participation probabilities and a scalar decision update. It contains no measured values.

## Related work

Performance-dependent retention can amplify representation disparity under repeated loss minimization. Hashimoto et al. studied this mechanism and a distributionally robust response.[2] Zhang et al. analyzed the interaction between group retention, sequential decisions, and fairness constraints.[4] Performative prediction provides a broader framework in which deployment changes the distribution encountered during learning.[3] Our declared evaluation objective differs from a model-dependent performative risk: we hold the affected population and its weights fixed while the submitted-feedback distribution changes.

Dean et al. studied participation and retraining across multiple services, including segmented equilibria.[5] Jin et al. examined polarization and group disparities at performatively stable solutions and interventions addressing stability and fairness.[6] The present model has one learner and no strategic competition between services. Its local calculations characterize specified scalar dynamics, rather than supplying a general theory of participation or competing agents.

Recursive weighted means also have established connections to mode seeking and robust location estimation. Comaniciu and Meer related mean shift to robust M-estimation.[7] Our loss-dependent weights admit an effective-objective interpretation, but the participation floor, group-specific access friction, and population evaluation objective need not match a standard kernel-density estimator. The contribution lies in the specified participation and monitoring comparisons, rather than discovery of weighted-mean multistability.

Selection correction is established in both learning and evaluation. Counterfactual risk minimization uses propensity-weighted estimates to learn from logged feedback, and self-normalized estimators have been studied for counterfactual learning.[8,9] Our weighting and quota conditions are simpler reference procedures, not implementations of those complete algorithms or newly proposed methods. Selective-label research concerns a related observation problem in which outcomes are available only under certain decisions.[10] Here, participation changes the mixture of submitted preferences.

These questions also motivate empirical AI research, although our simulation contains no language model. Feedback training involves particular evaluators,[11] and model opinion evaluations have found uneven alignment with demographic groups.[12] Sycophancy and preference-collapse research address additional ways in which feedback and objectives may diverge.[13,14,15] Catastrophic forgetting, conventions among interacting language models, and recursive-data model collapse concern distinct mechanisms.[16,17,18] None is established by observing selection effects in a scalar estimator.

## Methods

### Population objective and preference worlds

The population comprises three equally weighted fictional groups, numbered 0, 1, and 2. In the conflicting-preference scenarios, each world's group means are theta = (-1, 0, 1) plus independent uniform perturbations between -0.15 and 0.15. Individual submitted preferences are y = theta_g + epsilon, where epsilon is independently uniform between -0.2 and 0.2. These quantities are dimensionless preference coordinates, not measurements of income, empathy, health, or social class. In the no-conflict scenario, all three groups share the same preference mean.

The action w is a single shared continuous decision. Expected group loss is L_g(w) = (w - theta_g)^2 + 0.2^2/3. The declared service objective is the equally weighted mean J(w) = [L_0(w) + L_1(w) + L_2(w)]/3, which remains fixed throughout all evaluations. Its optimum is w* = mean(theta), and population regret is J(w) - J(w*) = (w - w*)^2. Every learner in the original experiment starts at w*. This initialization deliberately isolates deviation from an initially population-optimal action. It does not model the acquisition of general intelligence.

Twenty independently generated parameter worlds were used. Each world had 10 paired feedback-noise seeds. The worlds vary preference means within the same simple family; they are not 20 substantively different real environments. The exact configuration, world parameters, seeds, and outputs are supplied with the code.

### Participation and adaptation

Before each update, group g has feedback participation probability pi_g = 0.02 + 0.96 sigmoid[2 - c_g - beta L_g(w)]. The lower and upper bounds preserve positive participation. The access-friction vector is c = (1.2, 0, 0) in the main and no-conflict scenarios, making group 0 the prespecified low-access group. The equal-access scenario sets all friction values to zero. Beta takes values 0, 1.5, and 3. Beta scales the loss term inside the sigmoid; beta = 0 removes loss dependence. Probability slopes and dynamics need not change monotonically with beta. This response function is a modelling assumption, not an estimated human behavioural law.

Because groups have equal population weights, feedback group probabilities are proportional to pi_g. Each update uses 96 accepted preferences. The uncorrected learner updates w to 0.95 w + 0.05 mean(y). There are 250 updates per run. Random draws for group selection and preference noise are paired across conditions within each world and seed. The original configuration was recorded before its main run; later analyses are separately labelled exploratory.

### Experimental conditions

Four conditions are compared in Figure 2. Endogenous feedback recomputes participation probabilities from the current action before every update. Static feedback freezes participation probabilities at the initial population-optimal action, thereby retaining baseline selection while disabling its dependence on subsequent outcomes. Balanced collection uses exactly 32 feedback samples from each group per update. Inverse-probability correction uses endogenous participation but replaces the ordinary batch mean with sum(y_i/pi_gi)/sum(1/pi_gi). This self-normalized estimator uses the true probabilities supplied by the simulator; estimation error and unobserved selection were not included in the original experiment. The later extension examines two explicitly specified probability errors, without fitting propensities from data.

All conditions use the same number of accepted feedback items and action updates. Balanced collection may require additional recruitment effort, and probability correction requires information that a deployed system may not possess. Equal accepted-feedback budgets therefore do not establish equal acquisition costs. The complete-information oracle w* is an analytic reference, not a trained model or an additional stochastic condition.

The original design contains 20 worlds x 10 seeds x 3 beta values x 3 scenarios x 4 conditions = 7,200 runs. There are no model-capacity comparisons, knowledge replay experiments, or human participant groups in this completed design. Those elements remain future work.

{{FIGURE2}}

Figure 2. Executed simulation design. Four adaptation conditions share a fixed three-group population objective, initial action, accepted-feedback budget, and update count. Three participation strengths and three preference/access scenarios provide controls. The 7,200 runs use 20 independently generated parameter worlds, with 10 paired random seeds per world. Balanced collection does not imply equal recruitment costs; inverse-probability correction assumes known selection probabilities.

### Outcomes and analysis

The primary comparison is group 0 expected squared loss under endogenous versus static feedback in the main scenario at beta = 3, averaged over the final 50 decision rounds before updating. A positive difference indicates worse service to this prespecified group. Secondary summaries include population regret, every group's loss, group 0 feedback share, and the fixed-population loss minus the loss weighted by current feedback probabilities. Lower loss is better. The feedback-weighted metric is an expectation under the simulator, rather than a survey of actual people.

Seed-level endpoints are first averaged within each world. Uncertainty intervals are obtained by paired bootstrap resampling of the 20 worlds, with 10,000 resamples. These intervals describe variation over the specified parameter-world distribution; they do not justify extrapolation to other model families or populations. Multiple secondary comparisons are descriptive, without confirmatory multiplicity-adjusted claims. Iteration checkpoints and individual feedback records are not treated as independent experimental units.

The analysis plan, configuration, and their hashes were saved locally before the main run. This was not an external preregistration. The code records execution metadata, invariant checks, and all run-level summaries. Conditions with beta = 0 provide an exact implementation check because the endogenous and static probability schedules should coincide. A separate replay check examines whether the realized batch sequence reproduces the same action trajectory.

### Analytical extension and local feedback influence

After inspecting the original results, we analyzed the conditional mean map. For fixed positive population weights rho_g summing to one, positive differentiable participation pi_g(w), and feedback with mean theta_g within each group, define Z(w) = sum_h rho_h pi_h(w), q_g(w) = rho_g pi_g(w) / Z(w), and m(w) = sum_g q_g(w) theta_g. The uncorrected learner satisfies the exact conditional identity F(w) = E[w_next | w] = (1 - eta)w + eta m(w). Differentiation gives

EQ: m'(w) = Cov_q(theta_g, d log pi_g(w) / dw).   (1)

A fixed point wbar satisfies m(wbar) = wbar. The deterministic conditional-mean map is locally asymptotically stable when |1 - eta + eta m'(wbar)| < 1, or equivalently 1 - 2/eta < m'(wbar) < 1 for eta > 0. Equality requires further analysis. Iterating this map is not generally the same as the unconditional stochastic expectation E[w_t], and local stability does not prove global or finite-noise convergence. Appendix A provides the derivation.

We define a controlled feedback-only intervention: a persistent small amount h is added to one group's submitted mean while the population objective and the baseline preference parameters in the participation rule remain fixed. Participation may still respond indirectly to the changed action. The immediate conditional response is eta q_j(w). Freezing the sampling weights indefinitely gives persistent response q_j. On a smooth stable fixed-point branch, implicit differentiation instead gives

EQ: d wbar / dh = q_j(wbar) / [1 - m'(wbar)].   (2)

This is a local influence diagnostic distinct from loss or feedback share. The denominator is common to groups at a given equilibrium, so their response ratio remains q_j/q_k there. If an intervention changes true preferences or access directly, its additional effect on participation must enter the numerator. The reported derivative therefore does not describe every form of stakeholder correction.

For a fixed action, let J_feedback = sum_g q_g L_g and J = sum_g rho_g L_g. The monitoring difference has the identity

EQ: J - J_feedback = -Cov_rho(pi_g, L_g) / E_rho[pi_g].   (3)

If all groups share the same nonincreasing participation function of loss, this gap is nonnegative. Heterogeneous access friction removes that general sign guarantee. The identity holds regardless of how w was learned, explaining why a corrected training update can coexist with biased uncorrected monitoring. These are standard differentiation and change-of-measure identities applied to this model, not claims of new estimator theory. When participation depends on each group's quadratic loss, the same update also has an implicit optimization interpretation: defining P(w) = sum_g rho_g integral_0^L_g(w) phi_g(u) du for pi_g(w) = phi_g[L_g(w)] gives F(w) = w - eta P'(w)/[2Z(w)]. This effective objective generally differs from the declared population loss J. Appendix A derives the identity and its relation to the local-stability condition.

### Exploratory sensitivity experiments

The extension protocol, configuration, and code were recorded and hashed after the original results were known but before executing the new trajectories. All extension comparisons are exploratory. We retained every configured cell, including contrary outcomes. The extension used 1,000 updates, the same step size and batch size, and endpoints averaged over pre-update rounds 951-1000. It comprised 4,500 trajectories across 54 condition cells, separate from the original 250-update experiment.

First, we set exact preferences (-1,0,1), equal access, beta = 1.5, 3, or 8, and initial actions 0, +/-0.01, +/-0.25, and +/-0.75. Fifty paired seeds per cell compared endogenous with static participation. Static weights were frozen at each cell's own initial action. We reported all groups and terminal-state distributions. The threshold +/-0.2 summarizes central versus left/right terminal states; it is not a proven stochastic basin boundary. Seeds are repeated realizations in one world, not independently sampled populations. We also examined noiseless mean-map trajectories and bracketed numerical fixed points. Root searches do not establish completeness near tangencies.

Second, the original 20 preference worlds received ten fresh paired seeds under each of two participation laws. With a_g = sigmoid(2 - c_g) and sensitivity anchor b = 3, the alternative bounded exponential law was pi_exp(L,c;b) = 0.02 + 0.96 a_g exp[-b(1-a_g)L]. It matches the original sigmoid's probability and first derivative with respect to loss at L = 0, separately for each group. Zero is a mathematical matching reference, not an attainable expected loss under nonzero noise. The laws differ at positive losses, and their sensitivity parameters are not globally equivalent.

Each law was crossed with unweighted endogenous feedback, static selection, quota collection, true-probability weighting, weighting that incorrectly omitted access friction, and weighting that used half the correct sensitivity anchor. These are structured misspecifications, not propensities estimated from recruitment observations. We recorded the effective sample size (sum_i a_i)^2 / sum_i a_i^2 for batch weights a_i. Paired world-bootstrap intervals used 10,000 resamples and are descriptive, without multiplicity adjustment.

We separately simulated invitations under explicit recruitment assumptions. Uniform independent prospective invitations yield success probability mean(pi) for natural collection; invitations until 96 acceptances follow 96 + NegBin(96, mean(pi)), with NegBin counting failures. Targeted quota recruitment instead sums 32 + NegBin(32, pi_g) over groups. Probabilities remain fixed during each update. Independent stopping-count draws do not alter the accepted-feedback trajectories. Both expected and simulated realized costs are supplied; accepted budgets are matched, invitation budgets are not. These are model-based costs rather than observed human recruitment costs.

## Results

### Executed runs and primary comparison

All 7,200 original planned runs completed across 36 condition cells. Each run contained 250 updates and 96 accepted synthetic preferences per update. The design therefore processed 172.8 million synthetic feedback uses; paired conditions reused random draws, so these are not independent observations. The 20 worlds are the bootstrap units. Probability normalization, risk decomposition, quota counts, zero-beta equivalence, and exact replay checks passed. The maximum discrepancy in the analytic risk decomposition was 5.16e-16. No failed runs were removed.

In the main scenario at beta = 3, mean group 0 loss was 2.078 under endogenous feedback and 1.345 under static feedback. The primary paired difference was 0.734 (95% interval 0.516 to 0.897) squared preference units. Group 0's mean accepted-feedback share was 4.33% under endogenous feedback and 8.62% under the static control, compared with its fixed population share of 33.33%. Figure 3 shows the corresponding evolution rather than only the final endpoint.

{{FIGURE3}}

Figure 3. Observed simulation trajectories in the main scenario at beta = 3. Curves and uncertainty summaries are calculated from the executed runs, with seeds averaged within each world. Population regret is measured against the fixed equal-population oracle, and group 0 is designated by its access-friction parameter before observing outcomes. These are synthetic computational results, not observations from a language model or human population.

### Corrections and monitoring bias

Mean population regret in the primary setting was 0.215062 for endogenous feedback, 0.022380 for static feedback, 0.000004 for balanced collection, and 0.000808 for probability correction. Group 0 loss under the two corrective conditions was 1.055 and 1.075, respectively. The self-normalized correction did not exactly match the quota condition: its paired group 0 loss difference was 0.021 (95% interval 0.013 to 0.029). Correcting the fixed-population objective also changed the distribution of losses across other groups; Table 1 reports all three, rather than presenting group 0 alone.

The expected monitoring gap, defined as fixed-population loss minus feedback-weighted loss, was 0.640 under endogenous feedback and 0.433 under static feedback. A positive gap means that evaluation weighted like incoming feedback portrays lower loss than evaluation of the fixed population. The gap remained 0.389 after probability-corrected learning if monitoring itself was left uncorrected. The quota gap is zero by construction because feedback and population weights coincide. Expected invitations per accepted item were 1.99, 2.45, 5.10, and 2.43 for endogenous, static, quota, and corrected conditions, respectively. These are model-derived collection costs, not observed recruitment costs.

{{TABLE1}}

Table 1. Main-scenario outcomes at beta = 3, averaged over the final 50 decision rounds before updating. Values are means across 20 worlds after averaging 10 paired seeds per world. Population regret is measured against the equal-population optimum. Group 0 feedback share is a proportion of accepted feedback. Uncertainty for the primary paired comparison is reported in the text.

### Controls and boundaries

At beta = 0, endogenous and static endpoints were exactly identical under the paired draws in all scenarios. Without between-group preference conflict, their action paths were identical at every beta: group selection no longer changed the preference values used in a paired update. These exact identities validate the implementation and expose structural boundary conditions; they are not independent empirical discoveries. In the main scenario at beta = 1.5, the endogenous-minus-static group 0 loss difference was 0.593 (95% interval 0.530 to 0.659). With equal access friction, the same reference-group contrast was 0.027 (95% interval -0.045 to 0.097) at beta = 1.5 and 0.482 (95% interval 0.147 to 0.800) at beta = 3. Group 0 has no special access disadvantage in that scenario, and these estimates must not be interpreted as an intrinsic property of its label. Complete group and world summaries are retained in the repository. Replaying one saved endogenous feedback sequence reproduced its original action trajectory with zero numerical discrepancy; the replay checks determinism conditional on the realized sequence, not a separate feedback mechanism.

{{FIGURE4}}

Figure 4. Effects across participation strengths and control scenarios. Summaries use actual run outputs and world-level comparisons. Intervals show uncertainty across the 20 sampled parameter worlds, not across 7,200 independent real environments. Secondary comparisons are descriptive. The no-conflict and zero-outcome-dependence conditions test boundaries of the proposed mechanism.

### Environment differences include counterexamples

The original primary contrast was positive in 18 worlds and negative in worlds 10 and 11 (Figure 5). Their contrasts were -0.485208 and -0.513810, respectively, with all ten seed contrasts negative in each world. Across all worlds the range was -0.513810 to 1.174615. Every leave-one-world-out average remained positive, ranging from 0.710570 to 0.799434. Thus the reported positive average does not imply a uniform group-specific direction, and the two counterexamples do not invalidate the average estimand.

World-specific preference geometry helps explain the reversal. The initial feedback-mixture drift in the two negative worlds points toward the left, and subsequent endogenous trajectories further reduce the leftmost group's loss relative to static selection. A representative positive world drifts right. These cases retain the same access-friction vector. The direction therefore depends on the full participation and preference configuration, not on the group's label or access friction alone. Population loss and one group's loss must also be distinguished.

{{FIGURE5}}

Figure 5. Heterogeneity of the original primary effect. A, all twenty world means, sorted by effect; each averages ten paired seeds. The dashed line is the mean across worlds. B-D, stored world-mean action trajectories for one illustrative positive world and the two negative worlds. Selection of these examples was post hoc, and every world is retained in A. The two negative effects constrain a universal interpretation but do not refute the positive average.

### Equal access can coexist with local instability

In the exactly symmetric diagnostic, zero is a fixed point at every beta. Its conditional-mean update slope was 0.982545 at beta = 1.5 and 1.029222 at beta = 3, indicating local stability and instability, respectively. At beta = 3, numerically located stable noncentral roots were +/-0.453851. The central stability boundary was crossed near beta = 1.951843 and again near 4.691120. At beta = 8, the stable center coexisted with stable outer roots at +/-0.925588, separated by unstable roots at +/-0.531997 (Figure 6). Regaining central stability therefore does not imply uniqueness or global recovery. These scale-dependent values are diagnostics of the specified participation function.

Under endogenous participation, the stochastic initialization extension was consistent with this conditional picture. At beta = 3 and initial action zero, 20 of 50 terminal actions were below -0.2 and 30 were above +0.2; none lay between those thresholds. Starting at -0.25 or +0.25 put all 50 trajectories on the corresponding side at the terminal checkpoint. At beta = 8, all trajectories initialized at +/-0.25 ended within the central thresholds, whereas all initialized at +/-0.75 ended on their respective outer sides. Under endogenous participation at beta = 1.5, all tested initializations ended centrally. These finite-horizon counts do not prove long-run stochastic trapping. In exact noiseless arithmetic, starting at zero remains at zero even when that point is locally unstable.

At the positive stable beta = 3 root, the extreme groups' accepted-feedback shares were 0.020598 and 0.474449. Their immediate feedback-only influence derivatives were 0.001030 and 0.023722, and their persistent local branch derivatives were 0.036376 and 0.837881. The negative root exchanges the two groups. The common equilibrium gain changes absolute influence, while the ratio at the same root remains the sampling-share ratio. These operational derivatives supplement the loss results; they do not measure retained factual knowledge or human empathy.

{{FIGURE6}}

Figure 6. Exploratory conditional-mean analysis under exact symmetry. A, central update slope, with the local-stability boundary at one and the two numerical crossings indicated. B, fixed points located on a beta grid, classified by the local update slope; the search does not prove completeness at tangencies. C-D, deterministic mean-map trajectories for all seven stated initial actions at beta = 3 and 8. These curves are not stochastic mean trajectories. The original equal-access experiment included preference perturbations and is distinct from this exactly symmetric construction.

### Participation shape and correction errors change the results

With fresh seeds and a 1,000-update horizon, the sigmoid law produced a group 0 endogenous-minus-static contrast of 0.736484 (95% exploratory interval 0.517553 to 0.905720), again positive in 18 worlds and negative in two. The locally matched exponential law produced 0.451047 (0.410066 to 0.495010), positive in all twenty worlds. A positive average therefore persisted in this particular law challenge, while magnitude and heterogeneity changed. This is not a general robustness result across arbitrary participation laws.

Correction was sensitive to assumed probabilities (Figure 7). For the sigmoid law, population regret was 0.000713 with true probabilities, 0.050245 when friction was omitted, and 0.101813 when the sensitivity anchor was halved. The corresponding exponential-law values were 0.000298, 0.092701, and 0.019617. Omitting friction had a larger cost under the exponential law, whereas halving sensitivity had a larger cost under the sigmoid law. Thus there was no universal ordering of the two specified errors across response families. Quota regret was approximately 0.00000373 under both laws because paired quotas used the same accepted preference batches. Exact quotas cancel random variation in the group mixture. Their stationary expected population regret is eta v/[(2-eta)B] = 0.000003561 for v = 0.2^2/3, eta = 0.05, and B = 96 (Appendix A). The finite-run estimate is close to this analytic noise benchmark; it is not evidence of error-free learning.

True weighting reduced the mean batch effective sample size from 96 to 47.38 in the sigmoid setting and to 76.22 in the exponential setting. Expected invitations per accepted item were 2.43 and 1.73 for true weighting, versus 5.10 and 2.19 for quotas. The corresponding unweighted endogenous costs were 1.98 and 1.76. These comparisons describe the stated collection procedures at matched acceptance budgets; they do not establish superiority under equal invitation budgets.

The uncorrected monitoring gap remained 0.388302 under true weighting in the sigmoid setting and 0.173924 under the exponential law, despite small population regret. Quota monitoring had zero gap by construction. Equation (3) explains why improved learning and representative evaluation are separate requirements; a training correction does not force the monitoring covariance to vanish.

{{FIGURE7}}

Figure 7. Exploratory response-law and correction challenges. A, sigmoid and bounded exponential participation curves; probabilities and loss derivatives match only at zero loss. B, group 0 endogenous-minus-static contrasts. C, population regret under six conditions. D, expected invitations per accepted item under the stated recruitment procedures. B-D use rounds 951-1000 from fresh paired seeds in the original twenty worlds; intervals resample worlds and are descriptive. Log scaling in C makes near-zero quota regret visible. Misspecified weights are defined perturbations, not fitted probability estimates; costs are not matched between conditions.

## Discussion

### What the combined analysis establishes

The study connects three distinct observations within a specified adaptive system. Dynamic selection can worsen average service to a prespecified group relative to frozen selection, but preference geometry produces contrary cases. Equal access does not guarantee local stability of a shared decision, and restoration of central stability does not remove all alternative attracting states. Finally, correcting feedback weights during learning does not make participant-weighted monitoring representative of the intended population.

These mechanisms have substantial precedents in representation disparity, retention, and performative learning.[2,3,4,5,6,8,9] Our analysis makes their interaction inspectable through paired controls, all-world effects, local derivatives, and explicit misspecification challenges. It does not establish a previously unknown universal law. The principal analytical value is to keep questions separate that can otherwise be conflated: who participates, how a controlled correction changes the decision, and whether the resulting decision serves a declared population objective.

The covariance derivative in equation (1) gives a local explanation of the feedback loop. When changes in action alter participation in a way correlated with group preferences, the accepted-mixture mean changes with the action itself. Equation (2) shows that local persistence of this loop changes absolute feedback influence. Equation (3) separately identifies the selection component of the monitoring gap. None of these identities makes participation sensitivity intrinsically harmful or establishes the optimal social objective. The effective objective P explains why a convex population objective can coexist with multiple attracting mean-map states: loss-dependent participation changes the objective implicit in the update. This connection to weighted location estimation helps interpret the mechanism without assigning novel cognitive capacities to the scalar learner.

The return of central stability at high beta is also a consequence of the specified participation law. At the symmetric center, extreme-group sigmoid slopes shrink once their participation approaches the floor, reducing the derivative in equation (A1). Moreover, because expected loss is bounded below by the positive noise variance v, increasing beta without bound eventually drives every group's participation probability toward 0.02 and restores the population-mean conditional map. This limiting observation does not determine where finite-beta branches disappear or prove stochastic convergence. Regained stability should therefore be interpreted as response-law saturation, rather than AI maturation.

### The stronger knowledge and action hypothesis remains open

The original motivating question is whether an AI can retain accurate knowledge of a group while becoming less responsive to that group's corrections. The current experiment does not test this claim. The simulator knows preference distributions, but the learner updates one scalar estimate. It does not learn facts, predict stakeholder preferences, or retain a history of lived experience. An information oracle is not evidence of retained model knowledge.

A discriminating future study would use a shared learned model and matched held-out situations for factual prediction, preference prediction, decisions, and controlled corrections. Knowledge retention would require a prespecified equivalence margin rather than a nonsignificant decline. Reduced responsiveness would require a meaningful deficit in a defined correction-response estimand; worse decisions alone would not establish it. Providing correct decision-relevant information at action time, with matched-supervision controls, could distinguish information access from failure to use accessible information. Findings consistent with forgetting or restoration by information alone would narrow the hypothesis.

The human analogy remains a source of questions, not a biological explanation of AI. More capable models might widen their feedback coverage, and institutions might preserve participation despite unequal resources. Multi-agent simulations cannot by themselves establish representation of actual communities. Tests of human social transitions, model capacity, or real stakeholder participation require different evidence.

### Implications for panvascular research

Adaptive vascular research provides a possible application for evaluating who contributes to an evolving objective. Computational intravascular imaging and digital twins,[19] and AI-assisted vascular-material screening,[20] motivate collecting feedback across technical and clinical settings. A nationwide acute myocardial infarction cohort used treatment-propensity weighting and sensitivity analyses to address measured confounding.[21] That application illustrates the need to state what the weights correct: treatment allocation in the cohort and feedback participation here are different observation mechanisms. Neither approach removes unmeasured selection by definition.

Testing the present mechanism in panvascular research would require longitudinal records of who was eligible to contribute, who actually contributed, how decisions changed, and outcomes evaluated in a fixed target population. The cited studies provide clinical and computational context, not calibration or validation of this simulation's participation law. No clinical efficacy or vascular-device conclusion follows from the scalar preference coordinate.

### Limitations

The model imposes a shared scalar action, three fixed preference groups, equal population weights in the executed simulations, bounded independent noise, and specified participation rules. The original experiment starts at the population optimum. The extension varies initialization in an exactly symmetric setting and examines one alternative response family and two probability errors, not all plausible forms of participation, uncertainty, strategic behaviour, or changing needs. No response law was calibrated to human data.

Local mean-map analysis is deterministic and conditional. Numerical roots do not establish a complete bifurcation diagram, and finite-horizon branch counts do not establish stochastic convergence or permanent exclusion. The influence intervention shifts feedback content without directly changing underlying preferences; other interventions have additional pathways. The numeric stability thresholds depend on preference scale, noise and the chosen response family.

Known-probability weighting and quotas are idealized references. Self-normalized ratios have finite-batch behaviour, and weighting can reduce effective sample size. Structured probability errors do not substitute for estimating selection in practice. Invitation counts follow a declared probabilistic recruitment model; no real recruitment costs or equal-cost policy ranking were measured.

Bootstrap intervals characterize the specified worlds and procedures, not uncertainty about whether the model represents deployed AI. The 4,500 extension trajectories were exploratory and reused the original world geometries for the law challenge. They are not an independent replication across real environments, and their multiple comparisons have no confirmatory multiplicity adjustment. The original plan was locally recorded, not externally preregistered. No human, clinical, biological or language-model observations were used.

## Conclusions

Outcome-dependent participation can change both an adaptive decision and the population visible to its evaluation. In the specified scalar system, a positive average group-loss effect coexists with opposite-sign environments, equal access can coexist with local instability, and correction performance depends on probability and collection assumptions. Explicit influence and monitoring identities help separate these mechanisms. The broader question of retained knowledge with reduced responsiveness remains a distinct empirical hypothesis.

## Data and code availability

The original protocol, frozen simulation outputs, exploratory extension protocol and data, analytical verification, figure inputs and manuscript are available in the versioned repository at https://github.com/lingsenyou/feedback-circle-study/releases/tag/v0.2.5. Revision materials are versioned separately from the original experiment and historical working paper. All observations are synthetic; no private human or clinical data are included. Reproduction instructions distinguish original, exploratory and plotting environments.

## Acknowledgements

This project was supported by the National Natural Science Foundation of China (T2288101, 82170342) and Medical Engineering Joint Fund of Fudan University (yg2023-01). The language of this article has been polished with the assistance of AI-based language tools.

## Use of generative AI

OpenAI Codex assisted with literature retrieval, manuscript drafting and language editing, simulation programming and execution, mathematical checks, and figure preparation. This assistance was used throughout the preparation of the work under human guidance, task-specific instruction, active participation, and supervision. Additional AI agents supported internal checks; this process was not external peer review. Numerical results were generated by executing the released simulation code, and are distinguished from untested hypotheses. Human authors reviewed the manuscript and retain responsibility for its content, interpretations, and conclusions. AI tools are not authors.

## Conflicts of interest

Lingsen You, Li Shen, and Junbo Ge have participated in development of the XINSORB bioresorbable scaffold. This study does not evaluate XINSORB or any vascular device.

## Appendix A Derivations and verification

### Conditional mixture derivative

Write Z(w) = sum_g rho_g pi_g(w) and s_g(w) = pi'_g(w)/pi_g(w). Differentiating q_g = rho_g pi_g/Z yields q'_g = q_g[s_g - E_q(s)]. Since theta_g is held fixed, m' = sum_g theta_g q'_g = Cov_q(theta,s), proving equation (1). If the feedback means also depend on w, their derivative contributes an additional E_q(theta'_g) term. Differentiating F(w) = (1-eta)w + eta m(w) gives the stated scalar local-stability condition.

For bounded sigmoid participation, put u_g = sigmoid[2-c_g-beta L_g(w)]. Then pi'_g(w) = 2 beta(0.96)u_g(1-u_g)(theta_g-w). In the exact symmetric case, write u_e = sigmoid[2-beta(1+v)], u_m = sigmoid(2-beta v), pi_e = 0.02+0.96u_e and pi_m = 0.02+0.96u_m, where v = 0.2^2/3. Substitution at zero gives

EQ: m'(0) = 4 beta(0.96)u_e(1-u_e) / (2 pi_e + pi_m).   (A1)

The decimal stability crossings were obtained numerically from m'(0) = 1. Bracketed roots and finite-difference checks are supplied with the code; the root search is not a completeness proof.

### Feedback intervention derivative

For the feedback-only intervention, m(w,h) = m(w,0) + h q_j(w). At a fixed state its update derivative is eta q_j. On a differentiable fixed-point branch wbar(h) = m(wbar(h),h), implicit differentiation gives [1-m'(wbar)] d wbar/dh = q_j(wbar), proving equation (2) when the denominator is nonzero. Interpreting this as an attracting equilibrium response additionally requires a stable branch. Near the stability boundary, a large derivative need not remain informative for a finite intervention. If h also changes participation, the numerator becomes E_q(partial_h theta) + Cov_q(theta, partial_h log pi), rather than simply q_j.

### Monitoring identity

Multiplying J-J_feedback by Z = E_rho(pi) gives E_rho(L)E_rho(pi)-E_rho(pi L), proving equation (3). Under a common nonincreasing participation function phi, twice Cov_rho(phi(L),L) equals the sum over g,h of rho_g rho_h[phi(L_g)-phi(L_h)] (L_g-L_h), whose terms are nonpositive. This sign argument fails when heterogeneous friction prevents participation from being a common function of loss.

### Effective objective and mean map

Suppose pi_g(w) = phi_g[L_g(w)] with differentiable positive phi_g, fixed theta_g, and L_g(w) = (w-theta_g)^2+v. Define P(w) = sum_g rho_g integral_0^L_g(w) phi_g(u) du. The chain rule gives

EQ: P'(w) = 2 sum_g rho_g pi_g(w)(w-theta_g) = 2Z(w)[w-m(w)].   (A2)

Consequently F(w) = w - eta P'(w)/[2Z(w)]. This is a normalized gradient step on P, not generally on J. At a fixed point, differentiating (A2) gives P''(wbar) = 2Z(wbar)[1-m'(wbar)]. Positive curvature is necessary for the stated strict local-attraction criterion but is not sufficient by itself: the discrete step also requires 0 < eta P''(wbar)/[2Z(wbar)] < 2. These statements concern the deterministic conditional mean map and do not establish monotone descent by the noisy finite-batch process.

For sigmoid participation and beta > 0, a primitive of phi_g(L) is 0.02L - (0.96/beta) log[1+exp(2-c_g-beta L)], up to an additive constant. At beta = 0, participation is constant in loss and its primitive is pi_g L. With fixed finite access frictions and v > 0, pi_g(w) tends to 0.02 as beta tends to infinity, so m(w) tends to sum_g rho_g theta_g. This limiting algebra does not locate finite-beta bifurcations. The relation to robust location estimation is interpretive; no new optimization algorithm is claimed.[7]

### Quota noise benchmark

With exact group quotas matching rho_g, the batch mean is w* = sum_g rho_g theta_g plus zero-mean independent preference noise of variance v/B. Writing e_t = w_t-w* gives e_(t+1) = (1-eta)e_t+eta epsilon_batch. For 0 < eta < 2, its stationary variance is eta^2(v/B)/[1-(1-eta)^2] = eta v/[(2-eta)B]. Since population regret equals e_t^2, this is also its stationary expectation. The formula is an analytic benchmark under exact quotas and the stated independent noise, not a confidence interval for the finite-run estimate.

### Independent numerical checks

A separate implementation checked covariance and intervention derivatives by finite differences and resolved perturbed fixed points rather than differentiating the original simulation code. Covariance and true-preference derivative errors were below 3 x 10^-9; stable-branch feedback-only derivative error was below 5 x 10^-10. Plotting inputs, root residuals, world-level results and execution hashes are released. These checks support implementation and algebra, not originality or external validity.

## References

[1] Centola D. An experimental study of homophily in the adoption of health behavior. Science. 2011;334(6060):1269-1272. https://doi.org/10.1126/science.1207055

[2] Hashimoto T, Srivastava M, Namkoong H, Liang P. Fairness Without Demographics in Repeated Loss Minimization. Proceedings of the 35th International Conference on Machine Learning. PMLR. 2018;80:1929-1938. https://proceedings.mlr.press/v80/hashimoto18a.html

[3] Perdomo J, Zrnic T, Mendler-Dunner C, Hardt M. Performative Prediction. Proceedings of the 37th International Conference on Machine Learning. PMLR. 2020;119:7599-7609. https://proceedings.mlr.press/v119/perdomo20a.html

[4] Zhang X, Khalili MM, Tekin C, Liu M. Group Retention when Using Machine Learning in Sequential Decision Making: the Interplay between User Dynamics and Fairness. Advances in Neural Information Processing Systems. 2019;32. https://papers.nips.cc/paper_files/paper/2019/hash/7690dd4db7a92524c684e3191919eb6b-Abstract.html

[5] Dean S, Curmei M, Ratliff L, Morgenstern J, Fazel M. Emergent specialization from participation dynamics and multi-learner retraining. Proceedings of the 27th International Conference on Artificial Intelligence and Statistics. PMLR. 2024;238:343-351. https://proceedings.mlr.press/v238/dean24a.html

[6] Jin K, Xie T, Liu Y, Zhang X. Addressing Polarization and Unfairness in Performative Prediction. Proceedings of the AAAI Conference on Artificial Intelligence. 2026;40(27):22408-22416. https://doi.org/10.1609/aaai.v40i27.39399

[7] Comaniciu D, Meer P. Mean Shift: A Robust Approach Toward Feature Space Analysis. IEEE Transactions on Pattern Analysis and Machine Intelligence. 2002;24(5):603-619. https://doi.org/10.1109/34.1000236

[8] Swaminathan A, Joachims T. Counterfactual Risk Minimization: Learning from Logged Bandit Feedback. Proceedings of the 32nd International Conference on Machine Learning. PMLR. 2015;37:814-823. https://proceedings.mlr.press/v37/swaminathan15.html

[9] Swaminathan A, Joachims T. The Self-Normalized Estimator for Counterfactual Learning. Advances in Neural Information Processing Systems. 2015;28. https://papers.nips.cc/paper/2015/hash/39027dfad5138c9ca0c474d71db915c3-Abstract.html

[10] Wei D. Decision-Making Under Selective Labels: Optimal Finite-Domain Policies and Beyond. Proceedings of the 38th International Conference on Machine Learning. PMLR. 2021;139:11035-11046. https://proceedings.mlr.press/v139/wei21a.html

[11] Ouyang L, Wu J, Jiang X, et al. Training language models to follow instructions with human feedback. Advances in Neural Information Processing Systems. 2022;35:27730-27744. https://arxiv.org/abs/2203.02155

[12] Santurkar S, Durmus E, Ladhak F, Lee C, Liang P, Hashimoto T. Whose Opinions Do Language Models Reflect? Proceedings of the 40th International Conference on Machine Learning. PMLR. 2023;202:29971-30004. https://proceedings.mlr.press/v202/santurkar23a.html

[13] Sharma M, Tong M, Korbak T, et al. Towards Understanding Sycophancy in Language Models. International Conference on Learning Representations. 2024. https://openreview.net/forum?id=tvhaxkMKAn

[14] Xiao J, Li Z, Xie X, et al. On the Algorithmic Bias of Aligning Large Language Models with RLHF: Preference Collapse and Matching Regularization. arXiv preprint. 2024; revised 2025. https://arxiv.org/abs/2405.16455v2

[15] Chakraborty S, Qiu J, Yuan H, et al. MaxMin-RLHF: Alignment with Diverse Human Preferences. Proceedings of the 41st International Conference on Machine Learning. PMLR. 2024;235:6116-6135. https://proceedings.mlr.press/v235/chakraborty24b.html

[16] Kirkpatrick J, Pascanu R, Rabinowitz N, et al. Overcoming catastrophic forgetting in neural networks. Proceedings of the National Academy of Sciences. 2017;114(13):3521-3526. https://doi.org/10.1073/pnas.1611835114

[17] Ashery AF, Aiello LM, Baronchelli A. Emergent social conventions and collective bias in LLM populations. Science Advances. 2025;11:eadu9368. https://doi.org/10.1126/sciadv.adu9368

[18] Shumailov I, Shumaylov Z, Zhao Y, Papernot N, Anderson R, Gal Y. AI models collapse when trained on recursively generated data. Nature. 2024;631:755-759. https://doi.org/10.1038/s41586-024-07566-y

[19] You L, Yao J, Qiu Y, Wang Y, Sun Y, Zhang R, Shen L, Ge J. From intravascular imaging to adaptive vascular care: intelligent photonics and digital twins in panvascular disease. Light: Science & Applications. 2026;15(1):335. https://doi.org/10.1038/s41377-026-02410-6

[20] You L, Guo Y, Peng Z, Wang W, Shen L, Ge J. AI-assisted generation and screening of PLLA modifiers for bioresorbable vascular scaffolds. Chinese Science Bulletin. 2026;71(19):4653-4662. In Chinese. https://doi.org/10.1360/CSB-2026-0332

[21] You L, Li H, Lu Z, Wang Y, Hong S, Wang M, Zang T, Huang L, Shen L, Ge J. Intra-aortic balloon pump use and in-hospital mortality in acute myocardial infarction with Killip class III or IV: a nationwide cohort study. Biomarker Research. 2026;14:97. https://doi.org/10.1186/s40364-026-00993-1
