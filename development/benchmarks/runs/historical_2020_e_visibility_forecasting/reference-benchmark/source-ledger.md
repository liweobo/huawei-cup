# Source ledger

## Boundary and acquisition

Reference directory: <https://github.com/zhanwen/MathModel/tree/master/国赛论文/2020年优秀论文/E>. The six PDFs were enumerated from the repository directory, downloaded read-only, checked against the repository Git blob identifiers, hashed, fully text-extracted and visually sampled. PDFs, extracted text and renders are ignored benchmark inputs and are not deliverables.

Every item found only in a paper—video frame, label pairing, timestamp mapping, scene dimension, calibration constant or local filename—is `REFERENCE_ONLY_INPUT`. Agreement among papers is `REFERENCE_CONSENSUS`, not proof of an official attachment. Award levels have no independently verified official source and remain `UNKNOWN`.

| ID | File / source | Git blob | SHA256 | Pages | Full text | Visual PDF pages checked | Award |
|---|---|---|---|---:|---|---|---|
| R1 | [E20102690219.pdf](https://github.com/zhanwen/MathModel/blob/master/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2020%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E20102690219.pdf) | `aacd72f8fb7e015f72307a17a5decfc851be7383` | `86320c72eee35afd672e50f01f8bf90441b4fb6388ea07e79a3b1be6fb1d5480` | 57 | YES | 1, 19, 26, 33, 34, 35, 38, 39, 40, 52, 53, 56, 57 | UNKNOWN / not verified |
| R2 | [E20104250114.pdf](https://github.com/zhanwen/MathModel/blob/master/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2020%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E20104250114.pdf) | `321e4537014b0f94b91293feb70b814ff45d8d11` | `c9ba1a0533442ec5b3ab8ad04c46314243c16705935e90dc10293df321045924` | 54 | YES | 1, 21, 33, 34, 35, 36, 37, 39, 42, 50 | UNKNOWN / not verified |
| R3 | [E20104590039.pdf](https://github.com/zhanwen/MathModel/blob/master/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2020%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E20104590039.pdf) | `904e48ee9cdfb49c115ada43893af093e50d4eed` | `05113d1f837ce617fa73b0f9953740425b49f29889d47e50b62606bd7b5042dd` | 27 | YES | 1, 6, 16, 21, 22, 23, 24, 25 | UNKNOWN / not verified |
| R4 | [E20104590100.pdf](https://github.com/zhanwen/MathModel/blob/master/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2020%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E20104590100.pdf) | `771d9dffd884d8228c84c4891dfb9da0ace1cd38` | `24ec704d8c60687a75fb84baece7c70dd4bb766aa164867c27a02df4779cdead` | 68 | YES | 1, 22, 35, 40, 42, 43, 47, 49, 55, 68 | UNKNOWN / not verified |
| R5 | [E20112870005.pdf](https://github.com/zhanwen/MathModel/blob/master/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2020%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E20112870005.pdf) | `a81e60608602b9f269e32a3beca945c140091ce7` | `e3cfc6ec1809ea1a17d36a327b3efb765a9ff647fc3e0f575cd822aeffa7a9e2` | 50 | YES | 1, 13, 18, 22, 24, 26, 33, 34, 35, 36, 37, 45 | UNKNOWN / not verified |
| R6 | [E20114820008.pdf](https://github.com/zhanwen/MathModel/blob/master/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2020%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E20114820008.pdf) | `f314baa17cb1137816443d2ec36d0d1bbd0a2e93` | `805528b2e142c0c78eaee3d03af7668fcfcb7dc455fcf45d58df72e9d7051b48` | 70 | YES | 1, 27, 32, 33, 37, 40, 41, 43, 44, 48, 50, 51, 52, 53, 67, 68 | UNKNOWN / not verified |

Extraction quality is `GOOD_WITH_EQUATION_GLYPH_NOISE` for all six: all 326 pages yielded text, while key equations, plots, tables and suspicious appendix code were verified visually.

## Method and claim ledger

| ID | Title / authors / institution | Q1 | Q2 | Q3 | Q4 | Airport video / highway images / AMOS | Absolute MOR / clearing claim | Validation / uncertainty | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| R1 | 能见度估计与预测; 宋智超、刘旗洋、季仁杰; 华东师范大学 | Correlation, Lasso, polynomial MOR fit | SIFT features + dense regression | Dark-channel two-region extinction with assumed 9m separation | Holt extrapolation | YES / YES / YES | 105–140m; ≈09:05 at 150m | Q4 in-sample fit; no future interval | HIGH on method; MEDIUM on formula transcription |
| R2 | 基于视频数据的能见度估计与预测; 夏文辉、陈昱行、袁晶贤; 中国石油大学（华东） | Normalized OLS for RVR/MOR | VGG16 four-band classifier; appendix target inconsistency | Hough/vanishing geometry with assumed 3.5m scene segment | Linear + GM(1,1) extrapolation | YES / YES / YES | claimed metric values; 10:44:31 linear crossing | Q4 in-sample fit; no future interval | HIGH |
| R3 | 能见度估计与预测; 张璇、刘晓强、彭文斌; 郑州大学 | Pearson/Spearman + nonlinear regression | CNN on author-defined 0.8 RVR + 0.2 MOR classes | Dark channel + cross-ratio, assumed 6m/9m/6m camera height and C0=1 | Cubic extrapolation | YES / YES / YES | 75–90m; ≈08:50 at 150m | Q4 in-sample fit; no future interval | HIGH |
| R4 | 大雾演化规律的量化分析与预测模型研究; 戴浩然、彭斐琳、智志洋; 郑州大学 | GA nonlinear MOR regression | Image-feature regression + BP residual fit | Contrast row + dark channel + assumed 6m lane scale/C0=1 | ARIMA, GM, cubic extrapolation | YES / YES / YES | ≈47m; 08:50:56 at 150m | Q4 in-sample fit; no future interval | HIGH |
| R5 | 基于深度学习的大雾条件下能见度估计与预测; 周尧、郑洁、侯贵洋; 南京审计大学/天津大学/中国科学院大学 | Nonlinear transformed RVR regression | ResNet34+LSTM six-band classifier | Dark channel + guided filter + assumed road/camera geometry | ARIMA + recursive Seq2seq | YES / YES / YES | 30–68m; 09:29:48–09:37:43 at 150m | short historical split only; model spread, no coverage | HIGH |
| R6 | 大雾天气下的能见度估计与预测问题; 赵宇峰、吴心思、琚悦琦; 浙江财经大学 | Quantile regression for RVR/MOR | 22-class transfer CNN | Dark channel; appendix hard-codes 30m despite calibration prose | PSO-NGBM + ARMA(3,3) | YES / YES / YES | 89–95m; no 150m time, 200m at 2016-04-15 07:39:47 | Q4 in-sample MAPE; no future interval | HIGH |

Detailed page evidence is preserved in [paper-reviews](paper-reviews/).
