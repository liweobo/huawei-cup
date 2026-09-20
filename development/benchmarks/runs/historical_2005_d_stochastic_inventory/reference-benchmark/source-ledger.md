# Source Ledger

Primary listing: [2005 excellent papers, D](https://github.com/zhanwen/MathModel/tree/master/国赛论文/2005年优秀论文/D)

The directory name establishes membership in the repository's excellent-paper collection. It does
not establish an official prize level, so every `award_level` below is `UNKNOWN` and every
`award_verified` is `false`. No official award record was located, and none is guessed.

| reference_id | filename | URL | Git blob SHA | SHA256 | size | pages | title | authors / institution | text extraction | visual check |
|---|---|---|---|---|---:|---:|---|---|---|---|
| R1 | `仓库容量有限条件下的随机存贮管理.pdf` | [raw](https://github.com/zhanwen/MathModel/raw/refs/heads/master/国赛论文/2005年优秀论文/D/仓库容量有限条件下的随机存贮管理.pdf) | `5a8eb88db9aa829aefa12354c1efcab8d268ac24` | `ae14eee4ff98f1b87f960825a1e869836d28f3d0b76db0658bce1f037c94e7bb` | 264029 | 19 | 仓库容量有限条件下的随机存贮管理 | NOT_STATED in PDF | full, 19/19 pages non-empty, no errors | title page + p.2/model page rendered |
| R2 | `仓库容量有限条件下的随机存贮管理2.pdf` | [raw](https://github.com/zhanwen/MathModel/raw/refs/heads/master/国赛论文/2005年优秀论文/D/仓库容量有限条件下的随机存贮管理2.pdf) | `a06374302d8419d657429631ab191b07ed51e2cf` | `68e9c590bf0409560d99a9ddcd1097f1f5f493715b28edc3d10275152846f4e5` | 336508 | 29 | 仓库容量有限条件下的随机存贮管理问题 | NOT_STATED in PDF | full, 29/29 pages non-empty, no errors | title page + K-S test page rendered |
| R3 | `仓库容量有限条件下的随机存贮管理3.pdf` | [raw](https://github.com/zhanwen/MathModel/raw/refs/heads/master/国赛论文/2005年优秀论文/D/仓库容量有限条件下的随机存贮管理3.pdf) | `1ff6fd39aaf7864222460b17dded0d086182b18e` | `fc8fe7f8f2f4da7a1f5cc243a248d8296654dc350411f6dd6243e3cd0a9e5b34` | 168097 | 9 | 仓库容量有限条件下的随机存贮管理 | NOT_STATED in PDF | full, 9/9 pages non-empty, no errors | title page + state/enumeration page rendered |

The listing also contains a `.DS_Store` file, which is not a reference.

PDF metadata carries no `/Title` or `/Author`; all three were produced by the same
`Foxit Reader PDF Printer Version 6.1.0.0923` and the body text names no authors or institutions,
so authorship is recorded as `NOT_STATED` rather than inferred.

## Structured fields

| field | R1 | R2 | R3 |
|---|---|---|---|
| main_model_family | Expected-loss minimization on a single cycle; own/rented holding split; Lingo NLP | Average-daily-loss as `f(L,X)`; discrete and continuous variants; `E[f(L,X)]` minimized by derivative and exhaustive search | Average-daily-loss over one order cycle with explicit `q2(t)`, `q3(t)`; six arrival-time states for the multi-item case |
| stochastic_assumptions | Normal family fitted to all three lead samples (SPSS); evaluated at `X = E[X]` for the reported optimum | K-S tests reject Normal, Uniform and Exponential; X treated as discrete, probability by empirical frequencies | Continuous time; X density fitted by a Lorentzian for product 1, empirical frequency table for the derived probabilities; multi-item uses six intervals of X |
| solution_method | SPSS distribution fitting, probability computation per cost case, Lingo NLP solve | Maple derivative of `E[f(L,X)]`; Matlab exhaustive integer search over L for Q2; staged-step exhaustive search for Q4 | Matlab iterative solve of `E[Y1(L,X)]`/`E[Y2(L,X)]`; for multi-item, 6^m state combination enumeration then per-state optimization |
| reported_results | L* = 34 boxes, 38 boxes, 39 bags; Q4 simultaneous order time 1.175 days, order point 6.24 m3, own volume 3.123 / 0.49 / 2.628 m3 | L* = 36, 45, 34; Q4 `minE[f(L,X)]` 17.494 with `L*` 7.3333 and per-item `L1..L3` 1.55 / 1.8 / 3.9833, `Q` 21.05 / 22.30 / 56.65, `Q0` 10.27 / 10.68 / 30.05 | L* = 41, 37, 36 (unrounded 41.3918 / 37.0612 / 36.4637); Q4 solution (L*, Q1..Q3, Q01..Q03) = (7.8, 3, 3, 4, 3, 3, 0) |
| Q1 covered | yes | yes | yes |
| Q2 covered | yes | yes | yes |
| Q3 covered | yes | yes | yes |
| Q4 covered | yes | yes | yes |
| Q5 covered | yes (demand and lead both random; (R,Q) policy) | yes (Markov-chain sales rate, periodic fixed order cost) | yes (random sales rate, joint density of X and r) |
| award_level | UNKNOWN | UNKNOWN | UNKNOWN |
| award_verified | false | false | false |
| confidence | medium | medium-high | medium |

## Extraction and verification method

Text was extracted with `pypdf` into `work/extracted/`. Because the PDF layout inserts per-span
line breaks, a joined-line rendering was produced into `work/rendered/readable-*.txt` for reading.
Representative first and second pages of each paper were rendered to PNG with the bundled Poppler
`pdftoppm` and inspected visually; the visible titles, abstracts and reported values match the
extracted text.

Per §47 the PDFs, extracted text and rendered images are untracked and excluded from the commit.
