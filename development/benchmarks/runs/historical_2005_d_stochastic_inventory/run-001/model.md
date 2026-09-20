# State and analytic/event model

The existing Skill routes used are analyze_problem -> input audit -> design_model -> build_baseline -> run_experiment -> validate_model -> reviewer. The dynamic-state and mechanism-closure references apply; classification, ordinal, longitudinal-prediction and spectral contracts do not. No learned prediction dataset or train/test entity split is fabricated for this simulation.

## Regenerative model for Q1-Q4

State: time t, nonnegative on-hand vector I, pending-order flag and scheduled arrival time, cumulative received/fulfilled/lost demand, component costs. Own/rented amounts derive from I and reserved own capacities a. Inventory position is I plus the **receipt-time top-up commitment**, whose exact quantity is determined at receipt; it is not an independent order-time fixed pipeline quantity. Unmet demand is lost, so there is no backlog state.

Policy: for Q1/Q2 use b=Q, a=Q0, rate d=r and reorder point L, with tau=(Q-L)/r. For Q3/Q4 choose target volume b_i, own allocation a_i and trigger age tau. Feasible set: 0<=a_i<=b_i, sum a_i=Q0, sum b_i=Q, 0<tau<=max_i(b_i/d_i). Equivalent source decision L=sum_i(b_i-d_i*tau)+. This includes products becoming empty before the joint trigger. One outstanding order prevents duplicate triggers.

Random input: cycle lead X; common across products in Q3/Q4. Transition: before arrival I_i(t)=(b_i-d_i*t)+, order at tau, arrival at T=tau+X. Receive b_i-I_i(T-) and return to state b. Lost quantity is d_i*(T-b_i/d_i)+. Hard assertions check capacity split, nonnegative inventory, target sums, receipt nonnegativity, and single pending order at every event.

Conservation per item per cycle: b_i + received_i - fulfilled_i = b_i at the next post-arrival boundary. Before receipt: b_i - fulfilled_i = I_i(T-). Demand=fulfilled+lost; lost demand does **not** subtract from on-hand stock. No disposal. Own<=a_i, sum own<=Q0; rented=sum max(I_i-a_i,0) stores all excess, and own+rented=sum I_i.

For z>=0 define A(z,d,T)=[z²-(z-dT)+²]/(2d). Own holding exposure is A(b,d,T)-A(b-a,d,T), rented exposure A(b-a,d,T). Cycle cost C=k+sum[h*A(b)+(g-h)*A(b-a)+p*d*(T-b/d)+]. The renewal reward objective is J=E[C]/E[T], E[T]=tau+E[X]. Q1 is the argmin of this expression over legal L for a specified lead law with finite required moments. Q3 minimizes the same expression over tau,a,b. Finite mean X and positive finite E[T] are required; the alternative quadratic penalty also needs a finite second moment.

For empirical laws, all expectations are finite sums: exact conditional expectation, no Monte Carlo required. Q2 checks every smooth interval endpoint and bounded scalar minimum separated by lead/own-capacity breakpoints; also enumerates integer L. A possible open-boundary infimum is disclosed rather than called an attained optimum.

For continuous X~Uniform(l,u): E[(z-d(tau+X))+²] = { (z-d(tau+l))+³-(z-d(tau+u))+³ }/[3d(u-l)], and E[(tau+X-b/d)+] = { (tau+u-b/d)+²-(tau+l-b/d)+² }/[2(u-l)]. Thus Q4 uses closed-form expectations. Feasible multistart continuous optimization is a bounded search, not a proof of global optimality. Softmax allocations give own volume Q0 and rented target volume Q-Q0 by construction; tau is a logistic fraction of maximum depletion time. Exact expected cost selects candidates; independent simulated trajectories audit the selected policy. No stochastic search/evaluation seed reuse occurs.

## Baseline and model comparison

Single item baseline: L=min(r*mean lead,Q-1e-6), a feasible expected-lead coverage rule. Joint baseline: b proportional to d, a=Q0*d/sum(d), tau=max(1e-6,Q/sum(d)-E[X]). All baselines run under the same stochastic laws, cost components and simulation protocol as the primary policy. Candidates are (1) exact regenerative expectation, selected primary; (2) event simulation, independent implementation check; (3) Q5 finite nonstationary scenario. A generic Markov/MDP/RL framework is unnecessary.

## Replications, uncertainty and terminal rules

One Q1-Q4 Monte Carlo replication is a complete N-cycle path. Report R independent path cost/day ratios, their mean, standard error across R, and Student-t 95% interval. N=512/1024 and R=128/256 assess ratio bias/horizon and replication stability. Aggregate exact E[C]/E[T] is the reference. Confidence in policy difference uses paired path differences with shared indexed random lead scenarios. Individual periods/time points are never treated as independent samples.

Exact service measures: per-product stockout probability P(T>b/d), fill=1-E[lost]/(d*E[T]); joint cycle stockout is P(T>min_i b_i/d_i). MC reports event counts with a binomial interval only for the iid regenerative cycle events; Q5 service uncertainty uses independent full-horizon trajectories. Zero/few events do not prove zero risk. Source-distribution uncertainty is separate from Monte Carlo uncertainty.

## Q5 finite scenario

On each day requests follow a constant within-day rate r_i times a shared two-point multiplier. Change day 60 raises rates by 25%. Events are midnight (new exogenous rate and policy review), aggregate threshold crossing, stock depletion and arrival; continuous holding and fulfilled/lost demand are integrated between event times. Arrival is processed before same-time review. Static policy keeps Q4 L; adaptive policy scales that L by the past 14 completed days' mean demand multiplier, capped below Q. Decisions do not see future multipliers. Horizon is 120 days, initialized at target, no warm-up. This is an executed hypothetical scenario and a model discussion, not a 2005D empirical estimate or a globally optimal adaptive solution.
