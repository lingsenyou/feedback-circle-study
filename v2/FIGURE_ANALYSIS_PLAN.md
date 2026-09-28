# Exploratory figure analysis plan

Recorded after the original results and review diagnostics were known and before executing the v2 plotting analysis. This is not a preregistration or a new confirmatory study.

Figure 5 will show all twenty original primary paired world means, with no selection by sign, and original stored action trajectories for worlds 0, 10 and 11. World 0 is an illustrative positive case; worlds 10 and 11 are the two observed negative cases, selected explicitly after inspecting results. The displayed trajectories are world means, not single seeds.

Figure 6 will use the exact symmetric special case theta=(-1,0,1), c=(0,0,0), noise variance 0.2^2/3 and learning rate 0.05. It will display central conditional-mean slopes for beta=0..9, sampled fixed points on a 181-point beta grid and a 4,001-point action grid from -1.05 to 1.05, and deterministic conditional-mean trajectories over 1,000 updates at beta=3 and beta=8. Initial states are 0, +/-0.01, +/-0.25 and +/-0.75, all displayed. Root search uses sign changes, exact near-zero grid points and bisection; it does not prove root completeness near tangencies or constitute a full bifurcation theorem. Stable/unstable labels use the local update derivative. Critical boundary values are already known from the preceding reviewer diagnostics.

The plotted analysis will preserve the original data, export numerical plot inputs, and label these added analyses exploratory. Stochastic initialization and response-law experiments are separately specified and executed under extension/PROTOCOL.md.
