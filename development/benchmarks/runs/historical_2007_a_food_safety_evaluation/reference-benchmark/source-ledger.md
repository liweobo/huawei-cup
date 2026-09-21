# Reference Source Ledger

Scope: the six PDF files enumerated in the user-designated GitHub directory. Access date: `2026-09-21`. The directory label “优秀论文” is not evidence of a specific prize tier; every award level remains `UNKNOWN`.

## Reference-set integrity

| reference_id | filename | Git blob | bytes | SHA256 | pages | unique-content status |
|---|---|---:|---:|---|---:|---|
| `REF-01` | `1000401-A.pdf` | `aa07e43f2d41f5206f3397a476872660ddbec027` | 1,119,391 | `1a0b5f3ca8f4221304862508220a9a7792cdbd98aaf54c24dee21dd3e1f1c3be` | 22 | unique |
| `REF-02` | `10052A.pdf` | `b8c3be2c0b79ede06ee98b8124d10b647824ac87` | 526,502 | `ec2e0fe34a4fd7618e383f9ade93b41cfe20a256f0095241d1de96c991a33777` | 22 | exact extracted-text duplicate of `REF-06` |
| `REF-03` | `1028601.pdf` | `b0608098dc5aa39255442125eb66fb153d41efa6` | 1,400,411 | `2a9376fe9ea459a19b42a26867866c1c7015664ee4ddf64b9e136e015e111e7e` | 31 | unique |
| `REF-04` | `9000212.pdf` | `508966711b1e5d02b15e3f7127fe803f196585f5` | 520,333 | `097f02c60d1d0fe2369180b145bc7b510ebe2b60cc3e799e9daaa4d20ece5189` | 25 | unique |
| `REF-05` | `9001601.pdf` | `c13c888aa96e8b140209be47cf6b8edfae2cc70f` | 1,068,463 | `60591857de17afb477e253679702babfbb23536f433429f642f58d75f47649d1` | 42 | unique |
| `REF-06` | `9005210.pdf` | `d2112da4d90a3c190f3e1db2f9f8098d5781e892` | 526,500 | `b12f3e7b2d0fe52ea57f949d946595c44fb8c5ed3564de58af5ef774c26fd703` | 22 | exact extracted-text duplicate of `REF-02` |

`REF-02` and `REF-06` have different PDF bytes/metadata but identical extracted-text SHA256 `e91c811850a810ab6dda6d5407f2726fdabbbcadf9e17aaa936e126a6dad4d2a`; both visually identify team `9005210`, Air Force Engineering University College of Science, and the same authors. Consensus tables therefore report both `files/6` and `unique works/5` so the duplicate cannot inflate evidence.

## REF-01

- `filename`: `1000401-A.pdf`
- `url`: https://github.com/zhanwen/MathModel/blob/master/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2007%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/A/1000401-A.pdf
- `sha256`: `1a0b5f3ca8f4221304862508220a9a7792cdbd98aaf54c24dee21dd3e1f1c3be`
- `title`: 食品卫生安全保障体系数学模型及改进模型
- `authors`: 余家新；王高阳；罗自炎
- `institution`: 北京交通大学
- `pages`: 22
- `text_extraction_quality`: `GOOD_WITH_EQUATION_LAYOUT_CAVEATS`; Chinese body text and tables are readable; displayed equations were checked against rendered pages.
- `visual_verification`: `PASS`; cover, risk-model equations (PDF pp. 14-17), numerical tables/result (pp. 20-21), and conclusion (p. 22) inspected.
- `award_level`: `UNKNOWN`
- `award_verified`: `false`
- `problem_interpretation`: three-stage dietary-exposure system: intake, contaminant distribution, then regional/national exposure-risk evaluation and warning.
- `risk_definition`: mixed. It first defines risk as possibility plus adverse consequence; operationally it uses a sample exceedance probability (`PI`), an extreme-tail distribution (`TE`), a `99.999%` quantile, and a separate Pareto-style exposure index.
- `primary_output`: absolute daily-intake distribution, exceedance probability, and `Q_0.99999`; no relative composite ranking is the formal output.
- `threshold_source`: PTDI is named but not versioned; the numerical example instead compares dietary lead intake in `µg/person-day` with a blood-lead diagnostic concentration in `µg/L`, sourced only as an “international” standard.
- `evaluation_method`: multivariate-regression intake model; bootstrap plus Nakagami-m contamination approximation; PI exceedance estimate; EVT/Hill/Pareto tail estimate; point, single-random, and double-random variants.
- `weighting_method`: regression coefficients and regional aggregation weights, not MCDM importance weights; no expert-count or preference provenance.
- `normalization_method`: no candidate-set MCDM normalization; direct physical quantities and threshold comparisons.
- `hard_gate`: `HARD_GATE_IMPLICIT_BUT_INVALIDLY_MATCHED`; a threshold is intended as a gate, but output and comparator are different physical objects.
- `ranking_or_classification`: binary safe/unsafe language plus selection of high-PI regions for follow-up; formal ranking was added by the reference, not required by the problem.
- `uncertainty`: qualitative discussion only. Bootstrap is used to enlarge a small sample, not to report a quantile confidence interval; no tail-parameter or model-form interval.
- `reported_results`: reports `Q_0.99999 = 41.9259 µg` for a Beijing Dongcheng lead example, then claims lead-poisoning probability is far below `0.001%` and “meets requirements.”
- `reference_weakness`: `OUTPUT_THRESHOLD_SCOPE_MISMATCH`, `QUANTILE_TO_POISONING_PROBABILITY_PROMOTION`, `STANDARD_PROVENANCE_UNVERIFIED`, and false precision. The formal safety conclusion is unsupported by the stated comparison.
- `confidence`: `HIGH` for the extracted claims; `LOW` for the paper's real-world result validity.

## REF-02

- `filename`: `10052A.pdf`
- `url`: https://github.com/zhanwen/MathModel/blob/master/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2007%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/A/10052A.pdf
- `sha256`: `ec2e0fe34a4fd7618e383f9ade93b41cfe20a256f0095241d1de96c991a33777`
- `title`: 基于自助法和核密度估计的膳食暴露评估模型
- `authors`: 陆陶荣；张立森；朱丰
- `institution`: 空军工程大学理学院
- `pages`: 22
- `text_extraction_quality`: `GOOD_WITH_EQUATION_LAYOUT_CAVEATS`
- `visual_verification`: `PASS`; cover, product-distribution/Gauss-Legendre derivation, fuzzy matching table, warning rule, and conclusion inspected.
- `award_level`: `UNKNOWN`
- `award_verified`: `false`
- `problem_interpretation`: intake and contaminant probability models feed an absolute exposure distribution; its `99.999%` right quantile is compared with a daily intake warning standard.
- `risk_definition`: `QUANTILE / THRESHOLD COMPARISON`; the paper does not define its fuzzy matching score as a probability.
- `primary_output`: absolute contaminant intake CDF and `Q_0.99999`, followed by a binary warning decision.
- `threshold_source`: “nationally specified daily per-capita pollutant intake” or “national warning standard”; no concrete standard identifier, value, date, or scope.
- `evaluation_method`: stratified/repeated sampling; truncated-normal intake; bootstrap and lognormal-kernel density estimate for contamination; product distribution evaluated with Gauss-Legendre quadrature; fuzzy similarity to bridge unmatched data.
- `weighting_method`: author-defined fuzzy similarity scale `10,9,7,5,3,1,0` and normalized matching weights; these are data-bridging weights, not criterion-importance weights. Expert count and empirical calibration are absent.
- `normalization_method`: density normalization and matching-weight normalization; no alternative-set MCDM scaling.
- `hard_gate`: `HARD_GATE_EXPLICIT`; exceed the applicable intake standard -> warning. Applicability cannot be verified because the standard is unspecified.
- `ranking_or_classification`: binary warning only; no ranking and no multi-level class thresholds.
- `uncertainty`: mentions survey confidence rules and simulation diagnostics but gives no uncertainty interval for the extreme quantile.
- `reported_results`: gives the quantile equation and simulated demonstrations but no auditable real-data `Q_0.99999` value.
- `reference_weakness`: unverified threshold provenance, author-assigned fuzzy matching scale, no extreme-tail uncertainty, and no real-data numerical result. File is a duplicate of `REF-06`.
- `confidence`: `HIGH`.

## REF-03

- `filename`: `1028601.pdf`
- `url`: https://github.com/zhanwen/MathModel/blob/master/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2007%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/A/1028601.pdf
- `sha256`: `2a9376fe9ea459a19b42a26867866c1c7015664ee4ddf64b9e136e015e111e7e`
- `title`: 食品卫生安全保障体系数学模型的建立及其改进理论问题的研究
- `authors`: 张亮；薛彦红；陈建军
- `institution`: 东南大学
- `pages`: 31
- `text_extraction_quality`: `GOOD_WITH_EQUATION_LAYOUT_CAVEATS`
- `visual_verification`: `PASS`; cover, risk-product distribution, importance-sampling discussion, quantile algorithm, and final limitation inspected.
- `award_level`: `UNKNOWN`
- `award_verified`: `false`
- `problem_interpretation`: estimate intake and contaminant distributions, reconcile unmatched samples, then estimate the absolute daily-intake distribution and `99.999%` quantile for warning.
- `risk_definition`: `QUANTILE / THRESHOLD COMPARISON`; no relative risk score.
- `primary_output`: absolute contaminant-intake CDF and `Q_0.99999`; binary safe/warning statement after comparison.
- `threshold_source`: an authority safety standard is invoked without identifier, unit, value, version, or date.
- `evaluation_method`: multistage sampling and CAC taxonomy; iterative reconstruction of nondetect distribution; parametric fitting or density evolution; product-distribution integration; Monte Carlo/importance sampling and order statistics for the tail.
- `weighting_method`: importance-sampling weights and regional mixture weights only; no MCDM preference weights.
- `normalization_method`: probability-density normalization; no candidate-dependent score normalization.
- `hard_gate`: `HARD_GATE_EXPLICIT`; `Q_0.99999 < standard` is treated as safe.
- `ranking_or_classification`: binary safe/warning; no ranking.
- `uncertainty`: recognizes tail difficulty and states at least `10^7` samples for its accuracy target, but reports no interval, bootstrap coverage, parameter uncertainty, or model-form sensitivity.
- `reported_results`: no real-data tail result; the paper explicitly states that actual monitoring data were unavailable and the algorithms were not empirically tested.
- `reference_weakness`: unspecified standard, no real-data validation, no tail uncertainty, and an internally weak claim that abundant measured samples necessarily lie to the right of the desired quantile.
- `confidence`: `HIGH`.

## REF-04

- `filename`: `9000212.pdf`
- `url`: https://github.com/zhanwen/MathModel/blob/master/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2007%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/A/9000212.pdf
- `sha256`: `097f02c60d1d0fe2369180b145bc7b510ebe2b60cc3e799e9daaa4d20ece5189`
- `title`: 食品卫生安全保障体系的数学模型及改进
- `authors`: `UNKNOWN` (the PDF contains no team/author page)
- `institution`: `UNKNOWN`
- `pages`: 25
- `text_extraction_quality`: `GOOD_WITH_EQUATION_LAYOUT_CAVEATS`
- `visual_verification`: `PASS`; abstract, risk equations, Monte Carlo quantile algorithm, numerical result, and recommendations inspected.
- `award_level`: `UNKNOWN`
- `award_verified`: `false`
- `problem_interpretation`: an age-specific dietary-exposure model; it explicitly argues that one unstratified `99.999%` intake quantile is insufficient without body-weight/age-specific toxicological capacity.
- `risk_definition`: absolute contaminant-intake distribution and extreme quantile relative to a toxicological intake threshold.
- `primary_output`: age-group intake distributions and `Q_0.99999`, followed by a threshold-based safety conclusion.
- `threshold_source`: reports lead `PTWI = 0.025 mg/week/kg` and converts it for `60 kg` to `0.214 mg/person-day`; it cites external literature but gives no standard edition/effective date.
- `evaluation_method`: hierarchical sample allocation; lognormal intake and beta contaminant distributions justified by maximum entropy; a matrix/moment construction and Monte Carlo approximation for exposure; histogram accumulation for the quantile.
- `weighting_method`: demographic proportions and food-structure shares; no preference-weighted composite evaluation.
- `normalization_method`: explicit unit/time/body-weight conversion to a daily person-level threshold; no candidate-set normalization.
- `hard_gate`: `HARD_GATE_EXPLICIT`; the quantile is directly compared with the converted intake threshold.
- `ranking_or_classification`: binary safety conclusion; no ranking. Its discussion of enterprise `A/B/C/D` levels describes an existing system, not a threshold it derives.
- `uncertainty`: no quantile interval, repeated-seed stability, parameter uncertainty, or tail coverage analysis.
- `reported_results`: `Q_0.99999 ≈ 0.027 mg/person-day` for lead from meat versus converted `0.214 mg/person-day`, yielding a low-pollution/satisfactory conclusion.
- `reference_weakness`: point-only extreme-tail claim, distributional assumptions with limited data, standard-version uncertainty, and no uncertainty margin. Unlike `REF-01`/`REF-05`, the displayed threshold conversion is dimensionally aligned.
- `confidence`: `HIGH` for reported method/result; `MEDIUM` for threshold provenance.

## REF-05

- `filename`: `9001601.pdf`
- `url`: https://github.com/zhanwen/MathModel/blob/master/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2007%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/A/9001601.pdf
- `sha256`: `60591857de17afb477e253679702babfbb23536f433429f642f58d75f47649d1`
- `title`: `UNKNOWN` (the PDF begins at “1 问题的重述”; no title/author cover is present)
- `authors`: `UNKNOWN`
- `institution`: `UNKNOWN`
- `pages`: 42
- `text_extraction_quality`: `GOOD_WITH_EQUATION_LAYOUT_CAVEATS`; appendix code is readable, while several polynomial equations required page-image confirmation.
- `visual_verification`: `PASS`; opening page, contaminant standard table, risk CDF, roots/quantile result, conclusion, and cited-standard page inspected.
- `award_level`: `UNKNOWN`
- `award_verified`: `false`
- `problem_interpretation`: fit region-season-food-contaminant distributions and integrate them to obtain an absolute intake quantile, then use it for a food-safety decision and national assurance-system database.
- `risk_definition`: absolute exposure CDF and `Q_0.99999`; `Pq` is a CDF value, not a separate harm probability.
- `primary_output`: a polynomial CDF, a `99.999%` intake quantile, and a binary safety conclusion.
- `threshold_source`: cites `GB 2762-2005 食品中污染物限量`, issued `2005-01-25`, and reports a cereal lead limit of `0.2 mg`; the paper does not preserve the denominator in its comparison and uses a food-content limit against a daily-intake output.
- `evaluation_method`: multistage sampling; BP neural network with rough-set/GA initialization; polynomial contaminant density fitting; direct integration and root solving.
- `weighting_method`: sampling weights and rough-set neural-network feature weights; no MCDM criterion weights.
- `normalization_method`: neural-network/data preprocessing is discussed, but no candidate-set evaluation normalization is used; the final comparison is a nominally fixed regulatory comparison.
- `hard_gate`: `HARD_GATE_IMPLICIT_BUT_INVALIDLY_MATCHED`; a regulatory cutoff is used, but the assessed quantity and standard scope/unit do not match.
- `ranking_or_classification`: binary safety classification; no formal ranking.
- `uncertainty`: none for distribution fit, root selection, quantile, or standard comparison.
- `reported_results`: solves `Pq=0.99999`, obtains two positive real roots (`0.0240901` and `0.989689 µg`), selects `0.989689 µg`, compares it with reported `0.2 mg`, and generalizes the “safe” result nationally.
- `reference_weakness`: `OUTPUT_THRESHOLD_SCOPE_MISMATCH`, ambiguous root selection/CDF validity, false precision, no uncertainty, and unsupported geographic/population generalization. This is a demonstrated invalid-compliance failure mode.
- `confidence`: `HIGH` for what the paper states; `LOW` for result validity.

## REF-06

- `filename`: `9005210.pdf`
- `url`: https://github.com/zhanwen/MathModel/blob/master/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2007%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/A/9005210.pdf
- `sha256`: `b12f3e7b2d0fe52ea57f949d946595c44fb8c5ed3564de58af5ef774c26fd703`
- `title`: 基于自助法和核密度估计的膳食暴露评估模型
- `authors`: 陆陶荣；张立森；朱丰
- `institution`: 空军工程大学理学院
- `pages`: 22
- `text_extraction_quality`: `GOOD_WITH_EQUATION_LAYOUT_CAVEATS`
- `visual_verification`: `PASS`; its cover and critical pages match `REF-02` visually.
- `award_level`: `UNKNOWN`
- `award_verified`: `false`
- `problem_interpretation`, `risk_definition`, `primary_output`, `threshold_source`, `evaluation_method`, `weighting_method`, `normalization_method`, `hard_gate`, `ranking_or_classification`, `uncertainty`, `reported_results`, `reference_weakness`: identical to `REF-02`.
- `confidence`: `HIGH`; exact duplicate status verified by full extracted-text hash and binary text comparison.
