# Reference Consensus

## Where all three references agree

1. Problem reading. Q1-Q4 describe constant sales rates, a random delivery lead time, a fixed own
   warehouse capacity, a rented overflow, and a shortage penalty. All three adopt this skeleton
   and none disputes it.
2. Capacity handling. `Q0` is a hard own-storage capacity; excess stock is held in rented space
   and charged at `c3`. No one truncates, rejects or discards stock. The blind run does the same.
3. Shortage semantics. Shortages are lost sales. No reference models backorders or delayed
   service.
4. Cost components. A fixed order fee, own holding, rented holding and a shortage charge. All
   three aggregate these into a per-cycle cost and then divide by cycle length.
5. Objective form. Minimise an expected cost expressed per unit time, with `L` (and for Q3/Q4 the
   allocations) as the decision variables.
6. Joint ordering. Q3/Q4 items are ordered together and arrive together, sharing one own volume
   `Q0` and one arrival target `Q`, with no cross-item transfers.
7. Own-first storage. Goods fill own capacity before renting, and are drawn from rented storage
   first when sold. R1 and R3 state this explicitly; R2's case analysis implies it.
8. Q2 uses the given delivery data directly. Whatever law they choose, all three derive the lead
   probabilities from the 36/43/61 observations rather than from an outside source.

## Where the references split

1. Lead-time law. R1 fits a Normal to every product. R2 tests Normal, Uniform and Exponential,
   rejects all three, and uses the empirical frequency table. R3 fits a Lorentzian for product 1
   and uses empirical probabilities elsewhere.
2. Q4 uniform reading. R1 uses the continuous Uniform(1,3). R2 states the arrival time is an
   integer and uses a discrete uniform on {1,2,3}. R3 sidesteps it with six state intervals.
3. `c4` unit. R1 charges a per-unit shortage amount. R2 and R3 include a duration factor.
4. Allocation reporting. R1 reports an order-time residual volume, R2 reports stored `Q_i`/`Q0_i`,
   R3 reports integer state combinations.
5. Optimality claims. R1 and R3 claim optimality outright; R2 claims a global optimum for Q2 but
   only an approximate one for Q4 with a stated error radius.

Because of splits 1, 2 and 3, the reference set does not establish a single consensus answer for
any of the three products. The reported `L*` values are 34/36/41, 38/45/37 and 39/34/36 for
products 1, 2 and 3 respectively, and the spread is explained by these convention choices.

## Consensus that the blind run satisfies

| consensus element | blind run status |
|---|---|
| Constant-rate, random-lead, capacity-limited structure | satisfied |
| Hard own capacity with rented overflow | satisfied |
| Lost-sales shortages | satisfied |
| Four cost components, expected cost per unit time | satisfied |
| Joint ordering with shared capacity | satisfied |
| Own-first storage | satisfied |
| Q2 law derived from the given data | satisfied |

The blind run is within the reference consensus on every structural element. Its divergences from
individual papers are all in the directions the split analysis supports: it uses the empirical law
where R2's test justifies it, it carries both Q4 uniform readings where the references split, and
it preserves the `c4` ambiguity where all three silently choose.

## Consensus the blind run adds to

No reference states an intra-cycle event order, reports an uncertainty on any estimate, defines a
service metric, or establishes the renewal basis of its long-run rate. These are additions rather
than disagreements; the references neither affirm nor contradict them.
