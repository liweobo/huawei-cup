# Frozen problem facts

Source locators refer to `source-provenance/problem-transcription.txt` and verified EQ001-EQ076. Facts below are **PROBLEM_GIVEN_FACT** unless explicitly labeled otherwise.

Q1: one product has constant sales rate r (items/day, EQ001), fixed order fee c1 independent of quantity and variety (EQ002), own-storage cost c2 and rented-storage cost c3 per item per day with c2 <= c3 (EQ003-005). Shortage is allowed and reduces sales; the loss per item is c4 (EQ006). Delivery takes random X days (EQ007-008). Own capacity is Q0, each arrival replenishes on-hand inventory q to the fixed Q, Q0 < Q (EQ009-012). Order when inventory falls to L; determine the cost-minimizing L* (EQ013-015). The source does not specify a distribution for Q1 X, a finite horizon, initial inventory, a purchase price, an order-size limit, or a service-probability constraint.

Q2 provides the following scalar inputs and consecutive delivery-time observations. The observations are given data, **not a given population PMF**.

| Product | rate/day | order fee yuan | own yuan/item.day | rented yuan/item.day | printed c4 | own capacity | arrival target | lead records |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 康师傅精装巧碗香菇炖鸡面 | 12 boxes | 10 | .01 | .02 | .95 yuan/box.day | 40 boxes | 60 boxes | 36 |
| 心相印手帕纸10小包装 | 15 boxes | 10 | .03 | .04 | 1.50 yuan/box.day | 40 boxes | 60 boxes | 43 |
| 中汇香米5KG装 | 20 bags | 10 | .06 | .08 | 1.25 yuan/bag.day | 20 bags | 40 bags | 61 |

The full ordered lists, including the two zero-day observations for product 1, are in inputs.json and the preserved transcription. Q2 asks for each corresponding L*. EQ016-037 verify the scalar labels.

Q3: m products are ordered together from one supplier, with one common fixed order fee c1; they arrive simultaneously after common random X. Sales rates ri and unit volumes vi are known. Own/rented holding costs c2i/c3i and shortage cost c4i are expressed per volume per day. Total own volume Q0 and arrival target volume Q satisfy Q0<Q. An order is triggered when total on-hand volume q falls to L. Determine L*, own allocations Q0i and arrival targets Qi. The source does not specify an allocation-update rule, transfer charges, a lead-time distribution or dependence over orders. EQ038-065 verify all symbols.

Q4: combine Q2 products under Q3. Unit volumes v=(.05,.04,.10) m³, own capacity Q0=6 m³, target Q=10 m³ (EQ066-070). Common X is uniform between 1 and 3 days (EQ071). Other corresponding product data come from Q2. Determine L*, Q0i and Qi (EQ072-076). Whether the uniform distribution is continuous or integer-valued is not explicitly said; the primary continuous interpretation is MODELING_ASSUMPTION, checked against the discrete-uniform alternative.

Q5: sales are often random; ordering conditions change after some time. Discuss a mathematical model for adapting ordering/storage strategy. No stochastic demand law, parameters, change date, observation mechanism, horizon, service requirement or numerical data are supplied for Q5.

## MODELING_ASSUMPTION boundary

All non-source choices are in assumptions.md: long-run cost/day, lost-sale cost unit resolution, no backlog, one outstanding order, quantity determined at receipt to achieve the stated top-up, economical own-storage priority, static reserved capacity allocations, independent cycle lead draws, empirical PMF estimation, continuous fluid inventory and Q5 scenario laws. None of these is promoted into a problem-given fact.

Dependencies: Q1 -> Q2 through the single-item objective; Q1 -> Q3 through regenerative accounting; Q2 scalar costs + Q3 model + Q4 volumes/distribution -> Q4; Q1/Q3 state equations -> Q5 extension. No earlier historical results are modeling inputs.
