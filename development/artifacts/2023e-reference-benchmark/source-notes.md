# Primary Paper Review Notes

POST_HOC REFERENCE；物理PDF页码（含封面）。方法/结果全文审读的范围见source-ledger；论文自报分数未经复现，全部跨论文性能比较为NOT DIRECTLY COMPARABLE。

## P01 — E23100650012.pdf

[完整PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P01.pdf)

正文范围：2–48；附录抽查页：[55, 56, 57, 58, 59]。

### Q1a

pp.12–13: onset offset + repeat image time; 6 mL OR 33%; first observed hit; 23/100. Table sub077 time 4.119 differs from current minimum; no label identity assumption.

### Q1b

pp.9–20: variance 72→69, Spearman union-find redundancy, onset-delay weight exp/power, model/representation/parameter ablation table. Appendix pp.55–56 fits and predicts train_x; reported very small errors cannot be trusted as OOF.

### Q2a

pp.22–25: time-only linear/RF/GBDT/tree; claims 5-fold 80/20; Appendix p.59 training score. Sparse early time data acknowledged; tree jaggedness not physiologic discovery.

### Q2b

pp.28–31: clinical table includes 90-day mRS and E–W variables; spectral grouping 61/18/21; not trajectory-shape clustering; 4 cluster-family comparison, silhouette/DB, portraits.

### Q2c

pp.32–36: within/between-subgroup treatment counts and 3 cases; episode timing inferred, unsupported efficacy narratives.

### Q2d

pp.36–38: HM/ED corr 0.47 and 3 case plots interpreted as lag; no lag estimator or uncertainty; weak correlation does not exclude linear relation.

### Q3a

pp.39–43: 103→67 features, Borderline-SMOTE, nominal stacking, fivefold; reports precision/recall with ambiguous averaging; cannot establish resampling isolation.

### Q3b

pp.43–45: retain baseline, add 5 temporal/volume summaries (recovery duration, HM/ED maxima, expansion durations). Same-model before/after table; no verified time cutoff; imports HM threshold for ED without justification.

### Q3c

pp.45–48: PCA in predicted expansion subgroup; suggests factors/clinical advice. Not fully aligned to mRS-specific explanation; PCA variance is not target importance.

### Evidence caveats

- TRAINING_EVALUATION_CONFIRMED，PDF pp.55,56,59。
- OUTCOME_IN_GROUP_DISCOVERY_CONFIRMED，PDF pp.28。90-day mRS is clustering input; retrospective description possible, prospective subgroup assignment not validated.
- REFERENCE_LEAKAGE_RISK，PDF pp.43,44。Future/90-day cutoff absent; actual post90 rows unverified.
- REFERENCE_CAUSAL_CLAIM_WEAKNESS，PDF pp.34,35,36,38。

## P02 — E23102550019.pdf

[完整PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P02.pdf)

正文范围：2–48；附录抽查页：[]。

### Q1a

pp8–10: onset offset+followup delay,≥6mL OR≥33%, earliest≤48h; serial/duplicate-person repair claims not independently accepted.

### Q1b

pp10–14: explicitly changes target to unrestricted expansion; Bernoulli/GaussianNB by feature type, linear probability fusion on100. No independently validated score.

### Q2a

pp14–18: LOESS vs exp(a*t²+b*t+c), rise-fall rationale, fit residual only.

### Q2b

pp18–24: unfolds observations and repeats clinical features including90daymRS; says duplication increases chance same-person rows remain together. KMeans3 groups32/61/7; entity consistency not guaranteed.

### Q2c

pp24–30: min adjacent slope perperson,7treatmentregression,80/20; assumes treatment begins firstscan, therapies independent and sole cause ofEDchanges; unsupported efficacy ranks.

### Q2d

pp30–33:130followupentities, analogousHM/EDtreatmentregression,correlation.3052; no baselineadjustment/lag.

### Q3a

pp33–37: tree/RF/XGBregressors, chooses tree byMSE, displays same100trainingpatients; independent score provenance absent.

### Q3b

pp37–40: unfolds visits into rows with patientattributes/target,tree,group/timeboundary absent.

### Q3c

pp40–47:104features domainPearsonheatmaps; pp44–45 reversesmRSseverity direction; unsupported advice.

### Evidence caveats

- TARGET_DEFINITION_DIFFERENCE，PDF pp.10。
- OUTCOME_IN_GROUP_DISCOVERY_CONFIRMED，PDF pp.18。
- PSEUDOREPLICATION_AND_ENTITY_ASSIGNMENT_RISK，PDF pp.18,19,38。
- EXPOSURE_TIMING_ASSUMED_AND_CAUSAL_CLAIMS，PDF pp.8,24,27,28,29,30。
- MRSSCALE_DIRECTION_ERROR，PDF pp.44,45。

## P03 — E23103530067.pdf

[完整PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P03.pdf)

正文范围：2–79；附录抽查页：[]。

### Q1a

pp9–11: onsetoffset≤48h,baseline6mL OR33%,chronologicalstop.

### Q1b

pp12–26: retain biologicallyplausibleoutliers,BP/agecoding,MI40→RF20,5fold4models. p25tableLightGBM.800>RF.775 buttextcallsRFbest; selectionisolationunverified.

### Q2a

pp26–38: polynomial2–5,piecewise/Hermite,GaussianR².1004; chooses firstvisitresidual foranswer; nogroupedOOF.

### Q2b

pp39–49: clinical/history+time/volume Kmeans/FCM; FCM266+100+84'patients'=450rows for100people. Notconfirmedentityshapegrouping.

### Q2c

pp49–51: RFholdoutpermutation; positiveimportance erroneouslyinterpretedbeneficialtreatmentdirection.

### Q2d

pp51–55: corr,Gaussianmixturelikefit,ANOVA,permutation; p53explicitcorrelation≠causation; nolagmodel.

### Q3a

pp55–64: RFselection,nominal.15–.35accuracy,MLKNNfails,regressorCARTMSE2.23; distance-awaremetricbutnoformalordinal.

### Q3b

pp64–68: allfollowupwide+baseline,missingindicators,sameCARTMSE2.197; nocutoff;replace/addindicatorwordingconflicts.

### Q3c

pp68–77: domaincorrelation/ANOVA;p71recognizesindicationseverity;p76stillrecommendsefficacy; uncertainty/externalvalidationfuture.

### Evidence caveats

- PSEUDOREPLICATION_CONFIRMED_IN_REPORT，PDF pp.46,47。
- PREPROCESSING_ISOLATION_UNVERIFIED，PDF pp.16,24,25。
- REFERENCE_LEAKAGE_RISK，PDF pp.64,65,66,67。No cutoff; actualpost90notreproduced.
- REFERENCE_CAUSAL_CLAIM_WEAKNESS，PDF pp.51,76。Explicitcaveats pp53,71 also exist.

## P04 — E23103570015.pdf

[完整PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P04.pdf)

正文范围：2–116; generic literature pp105–109 skimmed；附录抽查页：[]。

### Q1a

pp7–19:serial/time,missingvolumezero,ORthreshold;p12writes|Vlater−Vfirst|,timeoriginimplementationunclear.

### Q1b

pp19–36:clinical/HMimaging,correlation+GBDT,randomsearchCVearlystopclaims,validation95.2%;p20unlabeled101–160testlabelprovenanceunclear.

### Q2a

pp37–45:days,4SDlongfollowuppatientremoval,OLS1–7/LAR/Gaussian2–5comparisons,extrapolationrationale; finalcurveinconsistent(thirdGaussianvsfirstLARresidual); entitymeansignedresidual,nogroupedCV.

### Q2b

pp45–52:sequentialEDvolumeKmeans4(6/39/20/35),silhouette/DB/CH; timealignment/shapeinputunderspecified.

### Q2c

pp52–62:end/baselineratio→binary,prevalence6rare,interactiontheory,CRITIC/PCAweights; noadjustedassociation/identification.

### Q2d

pp62–71:cooccurrence,baselinevolumes,endratios,tree/RFimportance,trainingfit; nolag.

### Q3a

pp72–92:clinicalHM/EDcorrelation/PCA,depth/leaf/pruningCV,decisiontree; PCAloadingsmislabeledmRSrelation; nominal/regressioncriteria mixed.

### Q3b

pp92–98:allfollowupwide+clinical,missingindicators,standardization,baselinefeature reuse,SVRkernelCV;nopredictioncutoff; finalMAE.8125>RMSE.7136 andMSE.6742 inconsistent.

### Q3c

pp98–116:literature+domainwise stepwiselinear,VIF/DW/ANOVA; causalcaveatspp76/78/80/84 coexistwithefficacypp113; mRSdirection/PCAimportanceerrors.

### Evidence caveats

- METRIC_INTERNAL_INCONSISTENCY，PDF pp.97。
- REFERENCE_LEAKAGE_RISK，PDF pp.20,93。Testlabelprovenance andfirst/allimagescopeunclear;nopredictioncutoff.
- PCA_IMPORTANCE_MISINTERPRETATION，PDF pp.80,81,82,83,84。
- REFERENCE_CAUSAL_CLAIM_WEAKNESS，PDF pp.53,63,113,114。
- Q1A_DIRECTIONAL_THRESHOLD_AMBIGUITY，PDF pp.12。

## P05 — E23104030073.pdf

[完整PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P05.pdf)

正文范围：2–50；附录抽查页：[]。

### Q1a

pp13–15:onsettime≤48h,baselineORthreshold butusesmaximumvolumeandmaxtime−firstscan,notfirstcrossingfromonset.

### Q1b

pp10–18:fullsampleMinMax/outliermeanreplacement,greyselection15/51,CNNonstaticvariables; splitclaimedbutfoldisolationunverified;RMSE.43109/MAE.34281 onprobability notfullclassmetrics.

### Q2a

pp19–21:explicitlydiscards>48hEDaswithoutvalue;fifthpolynomialR².4854,95%coefficientintervals; targetwindowdifferent,nogroupCV.

### Q2b

pp21–30:PCAclinical→age/systolic/diastolic,Kmeans5on160;staticnottrajectory; polynomial/Fouriercurves andfitmetrics.

### Q2c

pp30–32:entitymeanadjacentslope,seven-treatmentOLS,R².4316;dependenceaggregatedbutnoconfounder/timingchecks.

### Q2d

pp32–35:HM/EDmeanadjacentslopesandtreatmentSpearman;nojointlagmodel,causaltherapyinterpretation.

### Q3a

pp36–40:grey53→15,BPnet80first/20last,1000epochs;explicitmRSordered andclippedrounding,notformalordinalprobability.

### Q3b

pp40–42:ratio×volume for10regions,eachregionadjacentslopeaveraged;retainclinical+baselineimaging,72→20grey,BP;actualtemporalfeatureengineeringbutnocutoff or cleanablationmetrics.

### Q3c

pp42–49:72featuregreygradientranking,clinicaladvice;greyassociationclaimedcausal pp44;small-samplelimit.

### Evidence caveats

- Q1A_MAXIMUM_NOT_FIRST_CROSSING，PDF pp.14。
- Q2_WINDOW_CHANGED_TO_48H，PDF pp.19。
- PREPROCESSING_ISOLATION_UNVERIFIED，PDF pp.11,13,17。
- REFERENCE_LEAKAGE_RISK，PDF pp.40,41。No90daycutoff;actualpost90notreproduced.
- REFERENCE_CAUSAL_CLAIM_WEAKNESS，PDF pp.35,44。

## P06 — E23105330424.pdf

[完整PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P06.pdf)

正文范围：2–59 (result tables identified separately)；附录抽查页：[72, 74, 76, 77, 78, 82, 85, 88, 95, 97, 102, 103, 104, 106, 107, 112, 113]。

### Q1a

pp.11–12: body screens 48h after first scan, then adds onset offset; reports 32/160 rather than current23/100. Time origin/label population not equivalent.

### Q1b

pp.13–20: 74 features→RF top15, repeat oversampling, seven/three split + grid search; reports recall .4375/AUC .7031. Preprocessing/sampling before split risk; not every excellent paper reports near-perfect score.

### Q2a

pp.25–27: 435 (not450) points, large-time/volume removal based on maxima, polynomial degrees3/4/5; fourth chosen; signed residual sum per entity; no grouped OOF.

### Q2b

pp.27–35: explicitly nonuniform unequal-length sequences, per-entity x/y Z-score, DTW-distance KMeans5; rise/fall/turning-shape portraits, inverse normalization to residual scale. Uses full entity trajectory to scale/assign; descriptive, not new-entity prospective validation. Appendixpp84–86 confirms interpolation to8points, fastdtw between sequences, then ordinaryKMeans on rows of distance_matrix; not a DTW-barycenter KMeans objective.

### Q2c

pp.35–38: early/mid/late ordinal bins, Cochran-Armitage, treatment co-occurrence; several p>.05 marked significant, treatment timing/causal claims unsupported.

### Q2d

pp.38–40:130entities, per-person mean/max HM/ED, treatment prevalence, MWU/Spearman/Pearson; entity summaries but no adjusted confounding or lag model.

### Q3a

pp.44–48: repeat oversampling before seven/three split, Spearman74→55, XGBoost regression; ordered distance awareness and near-hit metric; metric standard deviation mislabel and hyperparameter inconsistency.

### Q3b

pp.49–51: explicitly rejects large sequence nets for ~100 independent patients; retains baseline and adds recency-weighted average, Integrated Slope, terminal/prior-maximum Hua ratio for short irregular series; table compares baseline versus added followup. No verified 90d cutoff; paper's MSE percentage arithmetic not accepted.

### Q3c

pp.51–53: Spearman factor portraits and clinical recommendations; correlations overinterpreted as therapy improvement.

### Evidence caveats

- REFERENCE_LEAKAGE_RISK，PDF pp.14,18,44,97,107。Full preprocessing/resampling precedes split; code different scaler fits for train/test; some CV in appendix commented.
- REFERENCE_LEAKAGE_RISK，PDF pp.49,50,51。No verifiable prediction cutoff; whole-trajectory summaries and normalizers are retrospective.
- REFERENCE_CAUSAL_CLAIM_WEAKNESS，PDF pp.37,38,52。
- P_VALUE_CLAIM_CONTRADICTION，PDF pp.37。
- DISTANCE_PROFILE_NOT_DTW_KMEANS，PDF pp.84,85,86。Valid as an explicitly named distance-profile embedding candidate, not direct DTW-centroid objective; normalization can erase amplitude/time scale.

## P07 — E23106730076.pdf

[完整PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P07.pdf)

正文范围：2–74; generic derivations skimmed；附录抽查页：[78]。

### Q1a

pp11–12: onset offset and chronological baseline threshold; text22 positives conflicts with24 table entries; label identity not assumed.

### Q1b

pp13–19: SMOTE and five families XGB/MLP/LGBM/SVC/LR, reports XGB AUC .85. Appendix p78 confirms fit_resample before train_test_split; comparison contaminated.

### Q2a

pp20–25: piecewise polynomial degrees2/3/4 and break counts5/10/20/40; degree4 with5 breaks by mean residual18.86; signed residuals, no entity-held-out evaluation.

### Q2b

pp28–33:15 static clinical/history/treatment fields, PCA then KMeans4 over160people, counts25/45/47/43. Not trajectory-shape grouping.

### Q2c

pp34–39: grey association and129entity deterioration summaries; volume decreases interpreted as efficacy without treatment timing or baseline adjustment.

### Q2d

pp40–46: entity mean HM/ED with7treatments in R lm; called Logistics in prose; R² HM .1789/ED .1088, ED overall p .144 acknowledged. No adjusted confounding.

### Q3a

pp47–58: variance+MI versus distance correlation+RFE,10features each,4models andgrid/randomsearch=16combinations,6model voting. Explicit input/model comparison but no nested-isolation evidence; .89 predicting first100 not established OOF.

### Q3b

p58: all followup input claimed, no clear representation or prediction cutoff; score provenance insufficient.

### Q3c

pp59–72: Fisher, Levene, correlation and formal cumulative ordinal logit via MASS::polr with parallelism check. pp62/67 regress aggregated mRS×location×category cells using mean volume as frequency weight; huge pseudo-sample uncertainty not patient-level ordinal prediction. Levene tests variance, not mean/prognostic effect. Advice and domain portraits extensive.

### Evidence caveats

- RESAMPLING_BEFORE_SPLIT_CONFIRMED，PDF pp.78。
- REFERENCE_LEAKAGE_RISK，PDF pp.58。Prediction cutoff absent; actual post90 usage not reproduced.
- PSEUDOREPLICATION_AND_WEIGHTING_ISSUE，PDF pp.62,67,68。
- REFERENCE_CAUSAL_CLAIM_WEAKNESS，PDF pp.34,39。

## P08 — E23106980022.pdf

[完整PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P08.pdf)

正文范围：2–50；附录抽查页：[51, 52, 53]。

### Q1a

pp9–11: prose specifies onset48h,baseline6mL OR33%. Visualp9 equation4.1 usesAND,4.2 omits time inequality. Confirmed document inconsistency; actual implementation not reconstructed.

### Q1b

pp12–20:clinical19→6RF,bilaterallocation10→4LightGBM,shape/intensity23→10;80/20,LogisticchosenoverRF/SVM;p20swapspositiveclassmetrics,F1tablecontradiction.

### Q2a

pp21–27: duplicate-time average, hours/mL, five stages polynomial/Gaussian, prediction bands. Visual p27 confirms prediction−observation then residual1/residual2 despite prose0/1; not common residual statistic; no groupedCV.

### Q2b

pp28–32:Kmeans4(6/35/34/25)claimedtrends,actualrepresentation/alignmentunspecified.

### Q2c

pp33–35:endpointrelativechange/time→5progressionlevels,RF/grey,efficacyoverreach.

### Q2d

pp36–38:endchanges+treatmentlinear,HM–EDquadratic; nolag.

### Q3a

pp39–42:104variables,sixselectionmethodsvote3/4threshold,RF;noformalordinalprediction.

### Q3b

pp43–44:visitcolumns≥40%coverage,multiple/KNNimputation,selectionRF,trainingaccuracy.45;nopredictioncutoff.

### Q3c

pp45–49:explicitorderedmRS,chi-square/Spearman,smallpoweracknowledged;adviceexceedsnonsignificance.

### Evidence caveats

- METRIC_DEFINITION_PROBLEM，PDF pp.20。
- REFERENCE_LEAKAGE_RISK，PDF pp.12,13,14,43,44。Preprocessisolationandcutoffunverified;actualpost90notreproduced.
- REFERENCE_CAUSAL_CLAIM_WEAKNESS，PDF pp.34,35,48。
- RESIDUAL_DEFINITION_INCONSISTENCY，PDF pp.27。

## P09 — E23107030070.pdf

[完整PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P09.pdf)

正文范围：2–67；附录抽查页：[71, 72, 73]。

### Q1a

pp11–13: onset offset, baseline6mL OR33%, chronological first hit; claimed serial correction not independently adopted; no in-window observation encoded0.

### Q1b

pp14–21:74clinical/imaging→18factor scores; LR/RF,80/20 plus5fold claim. RF evaluation table includes160(128/32) with unverified test labels. Appendix p71 instead LR90/10 and RF fitfirst100/predictfirst100; reads separate160label file.

### Q2a

pp22–27: onset hours; LOESS2kernels,degree7,doubleGaussian; discusses negative extrapolation and peak location. Reports fitRMSE6.90, not OOF; signed mean entity residual, no groupedCV.

### Q2b

pp28–37: DBSCAN/KMeans4 with100entity memberships, compares subgroupGaussian fit. Actual clustering representation/time alignment unreported; appendix p72 consumes preassigned group sheets, does not establish shape algorithm. Do not label pooled-row clustering as confirmed.

### Q2c

pp38–41: explicitly recognizes irregular repeat-measure dependence and proposes mixed effects. Actual random-effect unit/covariance not reported; table7-1 compares means of binary treatment/time/ED columns of incompatible units, not treatment×time coefficients. p40 notices severity-driven assignment; p41 still infers treatment efficacy.

### Q2d

pp42–44: baseline160entity HM/ED Pearson .659; claims longitudinal mixed effects asQ2c without random-effect details; no validated lag/joint model; causal therapy statements.

### Q3a

pp45–58:104→21 viagrey/RF/XGB top30 pairwise intersections union; BP/GBDT/XGB compare80/20 and5fold claims, XGB testaccuracy.867. Isolation not established; appendixp73 shows differentmodelsLR/tree/RF/SVM.

### Q3b

pp59–63: explicitly preservesQ3a21features, adds lastvisit105→126→28features; same3model comparison to assess added information; BPtestaccuracy.906. No90daycutoff; same model families not proof samefolds/nestedselection.

### Q3c

pp64–65: Pearson28features and domain explanation, correctmRSdirection, importance not causal; ratiointerpretation and therapyadvice unsupported.

### Evidence caveats

- TRAINING_EVALUATION_CONFIRMED，PDF pp.71。
- TEST_LABEL_PROVENANCE_UNVERIFIED，PDF pp.18,20,71。
- MIXED_EFFECT_IMPLEMENTATION_UNVERIFIED，PDF pp.38,41。
- NONCOMMENSURATE_MEAN_DIFFERENCES，PDF pp.41。
- REFERENCE_LEAKAGE_RISK，PDF pp.59,61。Last visit without cutoff; actualpost90notreproduced.
- REFERENCE_CAUSAL_CLAIM_WEAKNESS，PDF pp.41,43,44。
- BODY_APPENDIX_MODEL_MISMATCH，PDF pp.56,73。

## P10 — E23900310014.pdf

[完整PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P10.pdf)

正文范围：2–45；附录抽查页：[]。

### Q1a

pp11–13: dependence acknowledged. Visual p13 formula uses adjacent differences while prose says baseline; strict<48; threshold6×10^-3 inconsistent with raw10^-3mL units unless additional conversion, not evidenced. Formula defect not proof which code generated labels.

### Q1b

pp14–19:age/BPbins,71→40PCA99%,fillcomparison;LogisticKfoldvsRF/XGB80/20,76/85/90%notcommonprotocol.

### Q2a

pp20–23: logtime,RBFvs spline. Visual pp22–23 confirm perentity absolute residualmean followed by table spline−44.20, an internal inconsistency. No groupedOOF.

### Q2b

pp24–28:initial/middle/finalslopes→3D→MeanShift4rise/fall/stable/peakgroups;RBFfit20.15→13.24,insampleonly.

### Q2c

pp28–31:treatmenttreepredictsdiscoveredgroups,70/30accuracy46.7%;importance,recognizes6rare;nogroupdiscoveryisolation/baselineadjustment.

### Q2d

pp31–35:entitymean/endpointchangeSpearman,bars,.588/.53correlations; noticesindicationimbalancebutclaimsefficacy.

### Q3a

pp36–37:clinical+baselineimagingonehot/PCA,RF/XGBgridtest20/35%;callsmRSordinalbutnominalpredictors.

### Q3b

pp37–41:baseline+allimaging wideXGB vs3DRNN,zero-padding,104input64hidden7softmax5000epochs;50/98%claimed,testlearningcurve/splitunclear,nocutoff.

### Q3c

pp41–44:Spearmanradar,small-sampleanomaliesrecognized;therapyadviceexceedsidentification;interpretabilitylimitation.

### Evidence caveats

- NONCOMPARABLE_MODEL_PROTOCOLS，PDF pp.19。
- REFERENCE_LEAKAGE_RISK，PDF pp.38,39,40。Nocutoff,testcurve5000epochs,selectionindependenceunclear;actualtesttuningnotproven.
- REFERENCE_CAUSAL_CLAIM_WEAKNESS，PDF pp.33,43。
- ABSOLUTE_RESIDUAL_NEGATIVE_TABLE，PDF pp.22,23。
- Q1A_FORMULA_PROSE_MISMATCH，PDF pp.13。

## Visual verification

Poppler渲染并查看：P08 pp9/20/27；P10 pp13/22/23；P04 p97；P06 p51；P09 pp41/71/72/73。P09附录为截图，正文文本提取不能替代这些可视核查；其Q2代码读取已分组工作表，不能据此确定聚类输入表示。P06 pp84–86可读附录静态确认插值→DTW距离矩阵→普通KMeans；未执行。
