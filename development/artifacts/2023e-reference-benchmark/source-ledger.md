# Source Ledger

本次材料全部属于 POST_HOC REFERENCE。原 Skill 方案于首次外部检索前冻结，见 [冻结摘要](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/current-skill-solution.md)。

**reference_quality: MEDIUM**。公开发表身份或作者仓库可核验，不意味着统计方法正确。没有获得可核验一/二/三等奖的完整论文：**NO VERIFIED FULL AWARD PAPER AVAILABLE**。R-B03 的“成功参与奖”全文不作为优秀获奖论文；R-C01 的一等奖仅有封面。此结论限于本次可访问材料，不表示互联网不存在其他全文。

| ID | 类型 | 正文/方法证据 | 奖项状态 | 本轮角色 |
| --- | --- | --- | --- | --- |
| R-A01 | 官方 | 最终名单 XLSX | 直接核验 | 奖项来源 |
| R-A02 | 官方入口 | 登录限制 | UNKNOWN | 访问限制记录 |
| R-A04 | 高校官网 | 获奖新闻 | YES | 背景核验，无方法 |
| R-B01 / R-B04 | 期刊 | Q2及部分Q1 | UNKNOWN | 曲线/静态亚组参考 |
| R-B02 | 期刊 | Q1/Q2 | UNKNOWN | 方法与措辞反例 |
| R-B03 | 作者论文+代码 | 九小问 | 仅成功参与奖 | 可审查实现 |
| R-B05 | 作者代码 | 部分源码 | 自述三等奖未核验 | 辅助，不用于优劣 |
| R-B06 | 作者仓库 | 主要题面转录 | UNKNOWN | 排除出核心比较 |
| R-B07 | 作者论文+代码 | 九小问 | UNKNOWN | 特征比较与实现审查 |
| R-B08 | 作者原参赛PDF | 九小问，Q3合并 | 自述三等奖未核验 | 特征筛选、亚组、解释 |
| R-C01 | 第三方 | 仅封面 | 一等奖已核验 | 不推断正文方法 |

## R-A01

- source_id: R-A01
- title: “华为杯”第二十届中国研究生数学建模竞赛获奖名单
- authors: 中国研究生数学建模竞赛（发布机构；个人作者未署名）
- url: [原始来源](https://cpipc.acge.org.cn/sysFile/downFile.do?fileId=8e7956d9a59d455ebd3866f46b155c60)
- source_type: Level A — 官方最终获奖名单，XLSX
- claimed_award: 官方逐队奖项登记；不是建模论文
- award_verified: YES
- verification_source: https://cpipc.acge.org.cn/cw/contestPrevious/detail/4/2c9080178e2ad878018e5605f45e156d?page=0 （2023-12-17 官方报道中的获奖名单附件）
- publication_status: 官方发布
- full_text_available: YES — 获奖名单全文；不包含论文正文
- questions_covered: NONE — 仅核验题号、队号和奖项
- confidence: HIGH — 官方来源与附件链可核验
- notes: E题 sheet 第10行：23104030073，南昌大学，于梓涵/陈昊/周滢，一等奖。第5043行：23118450049，广东工业大学，成功参与奖。后者不是一/二/三等奖。
- local_evidence: [sources/R-A01-awards.xlsx](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-A01-awards.xlsx)；[sources/R-A01-awards-matches.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-A01-awards-matches.json)；[sources/R-A01.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-A01.txt)

## R-A02

- source_id: R-A02
- title: 中国研究生数学建模竞赛官网链接的优秀作品展示
- authors: UNKNOWN；链接发布机构为竞赛官网
- url: [原始来源](https://www.kdocs.cn/l/cv3j79fp8mZY)
- source_type: Level A — 官方导航链接指向 WPS 集合
- claimed_award: 优秀作品集合，具体作品/年份/奖项无法读取
- award_verified: UNKNOWN
- verification_source: https://cpipc.acge.org.cn/cw/hp/4
- publication_status: 官方链接存在；目标页面需登录
- full_text_available: NO
- questions_covered: UNKNOWN
- confidence: HIGH — 官方链接存在；LOW — 对具体方案没有正文证据
- notes: 记录访问限制，不绕过登录、不凭集合名称推断方法。
- local_evidence: [sources/R-A00-math-meta.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-A00-math-meta.json)；[sources/R-A02-meta.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-A02-meta.json)

## R-A04

- source_id: R-A04
- title: 西安交大在第二十届中国研究生数学建模竞赛中再获佳绩
- authors: 研究生院、数学学院、研究生数学建模竞赛工作室（文字署名）
- url: [原始来源](https://news.xjtu.edu.cn/info/1033/203406.htm)
- source_type: Level A — 高校官网获奖介绍
- claimed_award: 该校获一等奖3队，并有数模之星提名
- award_verified: YES
- verification_source: 该高校原文；最终奖项以 R-A01 为准
- publication_status: 高校官网，2023-11-15
- full_text_available: YES — 新闻全文；不是论文全文
- questions_covered: NONE — 无具体 E 题建模方法
- confidence: HIGH — 获奖新闻；不支持算法或数值比较
- notes: 不能把学校的获奖情况绑定到未具名的 GitHub 论文。
- local_evidence: [sources/R-A04.html](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-A04.html)；[sources/R-A04.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-A04.txt)

## R-B01

- source_id: R-B01
- title: 出血性脑卒中智能诊疗建模
- authors: 姚宇朕
- url: [原始来源](https://www.hanspub.org/journal/paperinformation?paperid=95749)
- source_type: Level B — 正式期刊论文
- claimed_award: NONE — 原文未声明竞赛奖项
- award_verified: UNKNOWN
- verification_source: https://doi.org/10.12677/mos.2024.135465 （核验发表信息，不核验获奖）
- publication_status: 建模与仿真，2024，13(5):5144–5153；2024-09-04 发表
- full_text_available: YES — 10页 PDF
- questions_covered: Q2a、Q2b、Q2c、Q2d；同题结构高度一致，未见明确2023E数据版本声明
- confidence: MEDIUM — 发表身份可核验；同题数据关联与方法有效性有限
- notes: 二次/三次/高斯曲线，静态临床特征 K-means 四组，拟合参数 ANOVA/Spearman。不是完整轨迹形态聚类证据。PDF: https://pdf.hanspub.org/mos2024135_132571869.pdf
- local_evidence: [sources/R-B01.pdf](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B01.pdf)；[sources/R-B01.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B01.txt)

## R-B02

- source_id: R-B02
- title: 机器学习驱动的出血性脑卒中智能诊疗建模研究
- authors: 张志成
- url: [原始来源](https://www.hanspub.org/journal/paperinformation?paperid=106419)
- source_type: Level B — 正式期刊论文
- claimed_award: NONE
- award_verified: UNKNOWN
- verification_source: https://doi.org/10.12677/aam.2025.141027 （仅发表核验）
- publication_status: 应用数学进展，2025，14(1):247–262；2025-01-29 发表
- full_text_available: YES — 16页 PDF
- questions_covered: 正文 Q1a、Q1b、Q2a–Q2d；摘要提到 mRS，但没有 Q3 方法/结果章节
- confidence: MEDIUM — 题目字段与患者ID明确；LOW — 方法比较可信度
- notes: 不能把摘要中的 XGBoost/LightGBM/mRS 当作正文已实现内容。规则遗漏6mL、时间基准异常、无独立验证证据。主要用于参考质量反例。PDF: https://pdf.hanspub.org/aam2025141_272624261.pdf
- local_evidence: [sources/R-B02.pdf](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B02.pdf)；[sources/R-B02.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B02.txt)

## R-B03

- source_id: R-B03
- title: 出血性脑卒中预后预测：集成静态模型和时序模型
- authors: spiritysdx（公开仓库维护者）；论文可视封面隐去队员姓名，不补全作者
- url: [原始来源](https://github.com/spiritysdx/CPGMCM_2023)
- source_type: Level B — 作者公开参赛论文、LaTeX 与代码
- claimed_award: 仓库未声称高等级奖；PDF文字层队号23118450049可与官方表匹配
- award_verified: YES
- verification_source: R-A01，E题 sheet 第5043行；仅核实“成功参与奖”
- publication_status: 公开参赛稿；论文 commit ed69e0673d04785c3d52f253d34cb94bccb4bac4；代码 commit bad0cec453e53c2e3eb02bd7dcd1950b17368c53
- full_text_available: YES — 44页 PDF、可读 LaTeX；选读相关公开源码
- questions_covered: Q1a、Q1b、Q2a、Q2b、Q2c、Q2d、Q3a、Q3b、Q3c
- confidence: MEDIUM — 可追溯全文/代码；不是优秀奖项基准
- notes: PDF中文文字层编码异常，以作者LaTeX核对正文。代码 https://github.com/spiritysdx/CPGMCM_2023_Code 。源码确认全量缩放、SMOTE先于切分；论文Q3亦写先SMOTE后切分，见 source-notes。
- local_evidence: [sources/R-B03.pdf](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B03.pdf)；[sources/R-B03-tex-read-only.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B03-tex-read-only.txt)；[sources/R-B03-q12-code-read-only.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B03-q12-code-read-only.txt)；[sources/R-B03-q22-search-code-read-only.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B03-q22-search-code-read-only.txt)

## R-B04

- source_id: R-B04
- title: 基于ISSA-BP的出血性脑卒中临床智能诊疗模型
- authors: 程依儿
- url: [原始来源](https://doi.org/10.12677/mos.2025.143212)
- source_type: Level B — 正式期刊论文
- claimed_award: NONE
- award_verified: UNKNOWN
- verification_source: 出版方PDF首页，仅核验发表信息
- publication_status: 建模与仿真，2025，14(3):168–178；2025-03-13 发表
- full_text_available: YES — 11页 PDF
- questions_covered: Q1b、Q2a–Q2d；同题结构高度一致，数据版本未核实；无Q3
- confidence: MEDIUM — 来源可核验；测试标签和验证设计不透明
- notes: 72维输入的ISSA-BP；双高斯总体曲线；静态临床/治疗特征FCM五组；ANOVA。PDF: https://pdf.hanspub.org/mos2025143_162572242.pdf
- local_evidence: [sources/R-B04.pdf](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B04.pdf)；[sources/R-B04.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B04.txt)

## R-B05

- source_id: R-B05
- title: Question E of the 20th China Graduate Mathematical Contest in Modeling
- authors: KUST-Qin（仓库维护者）；团队姓名UNKNOWN
- url: [原始来源](https://github.com/KUST-Qin/Question-E-of-the-20th-China-Graduate-Mathematical-Contest-in-Modeling)
- source_type: Level B — 公开 MATLAB 实现
- claimed_award: 国家三等奖（作者自述）
- award_verified: UNKNOWN
- verification_source: 缺少队号/可核验作者对应；不从昵称推断身份
- publication_status: 公开代码，commit b0ca41e34700b08e7263e78853de033fdb9275ca
- full_text_available: NO — 未找到完整论文；部分源码可读
- questions_covered: 选读Q2a/Q2b及Q3相关代码；不能据文件名断言全部子题已完成
- confidence: MEDIUM — 已读源码；LOW — 奖项/完整方案证据
- notes: 高阶log/有理函数、绝对残差均值；未见分组生成机制和独立验证。只作辅助差异，不作优越性证据。
- local_evidence: [sources/R-B05-page.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B05-page.txt)；[sources/R-B05-Q2_1_2-read-only.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B05-Q2_1_2-read-only.txt)；[sources/R-B05-Q2_2_2-read-only.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B05-Q2_2_2-read-only.txt)

## R-B06

- source_id: R-B06
- title: AI_CDM_for_ICH
- authors: artdillon（仓库维护者）
- url: [原始来源](https://github.com/artdillon/AI_CDM_for_ICH)
- source_type: Level B — 公开项目/题目转录
- claimed_award: NONE
- award_verified: UNKNOWN
- verification_source: UNKNOWN
- publication_status: 公开仓库，commit 1a12c26c7a0059059c76b9c7211078df2129239e
- full_text_available: NO — 已读README主要转录题目，不是完整方案
- questions_covered: 题面覆盖Q1–Q3；方案覆盖未核验
- confidence: LOW — 不纳入建模优劣结论
- notes: 仅发现线索，排除出核心对照；不把题目要求当成作者已实现方法。
- local_evidence: [sources/R-B06-page.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B06-page.txt)

## R-B07

- source_id: R-B07
- title: 脑出血患者预测模型的构建与评估
- authors: ydchen0806（仓库维护者）；论文团队作者/队号未披露
- url: [原始来源](https://github.com/ydchen0806/23yansaiE)
- source_type: Level B — 作者公开完整参赛稿、LaTeX、代码
- claimed_award: UNKNOWN — 仓库README未声明奖级
- award_verified: UNKNOWN
- verification_source: 无可与官方名单匹配的队号；作者知乎链接返回403
- publication_status: 作者公开参赛稿；commit 92d7c4f74f57209acc00e9aaa130dc480f5574ec
- full_text_available: YES — 57页PDF、Article.tex及相关源码
- questions_covered: Q1a、Q1b、Q2a、Q2b、Q2c、Q2d、Q3a、Q3b、Q3c
- confidence: MEDIUM — 全文/代码可读；高分不能直接比较
- notes: 混合效应/BiLSTM、特征重要性选择后K-means、DeepForest/LSTM、特征组比较。PCA先于split、训练拟合指标和论文/代码不一致须单独审查。
- local_evidence: [sources/R-B07.pdf](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B07.pdf)；[sources/R-B07-tex-read-only.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B07-tex-read-only.txt)；[sources/R-B07-q2_b-code-read-only.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B07-q2_b-code-read-only.txt)；[sources/R-B07-q3_b-code-read-only.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B07-q3_b-code-read-only.txt)

## R-B08

- source_id: R-B08
- title: 出血性脑卒中临床智能诊疗建模
- authors: TCPtcp（仓库维护者）；提交论文作者/队号UNKNOWN
- url: [原始来源](https://github.com/TCPtcp/Prediction-of-Hemorrhagic-Stroke-Risk)
- source_type: Level B — 作者公开原参赛PDF与后续复盘仓库
- claimed_award: 国三（作者自述）
- award_verified: UNKNOWN
- verification_source: 完整PDF没有可匹配队号/作者；不能仅凭README认定
- publication_status: 41页原参赛稿；仓库为2025年复盘；commit 5622d0b8b35667c72103e03a90eff0c3ae6f4b59
- full_text_available: YES — PDF；代码已被作者后续改进，本轮不用于重建原参赛成绩
- questions_covered: Q1a、Q1b、Q2a–Q2d、Q3a/Q3b合并叙述、Q3c；Q3a与Q3b指标归属不完全分明
- confidence: MEDIUM — 原文可读；奖级/协议不充分
- notes: 73→7特征筛选、混合类型两步聚类、曲线比较、mRS特征缩减/岭回归。明确知道治疗时间未知，却仍将体积下降当作疗效；将48.90h手动改成48.00h。
- local_evidence: [sources/R-B08.pdf](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B08.pdf)；[sources/R-B08.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B08.txt)；[sources/R-B08-page.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B08-page.txt)

## R-C01

- source_id: R-C01
- title: 出血性脑卒中临床智能诊疗建模_南昌大学.pdf
- authors: 于梓涵、陈昊、周滢（公开封面）
- url: [原始来源](https://max.book118.com/html/2024/1018/8066026121006135.shtm)
- source_type: Level C — 第三方文档站封面预览
- claimed_award: 队号23104030073（封面）；一等奖由官方名单核验，而非标题认定
- award_verified: YES
- verification_source: R-A01，E题 sheet 第10行，队号、学校、三人姓名均匹配
- publication_status: 第三方上传，页面显示2024-10-19；非作者原始发布
- full_text_available: NO — 页面标60页，本次可读文本只有封面
- questions_covered: UNKNOWN — 正文未获得
- confidence: HIGH — 团队奖项匹配；LOW — 正文真实性/完整性及方法信息
- notes: 没有读取/推断其模型或指标。此源只能核验一等奖线索，不能支撑G1建模差距。
- local_evidence: [sources/R-C01.html](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-C01.html)；[sources/R-C01.txt](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-C01.txt)

## Retrieval boundary

检索覆盖官方竞赛入口/最终名单、高校官网、DuckDuckGo与GitHub公开仓库搜索、出版方PDF和作者源码。查询和响应时间保存在 [retrieval-index.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/retrieval-index.json)，原始搜索响应及失败记录位于同目录。CAPTCHA、403、登录限制均按不可用处理；Bing返回的无关结果不作证据。源码仅静态阅读，未安装其依赖、运行 notebook、训练模型或复算其成绩。

R-B01/R-B04 的样本规模、字段与题意高度吻合，但没有数据哈希等价证明；R-B02明确出现本赛题、sub001–sub160和原始表名。作者参赛仓库明确关联2023E，依然不能据此认定处理后的数据版本/标签/协议相同。所有跨方案数值均按 NOT DIRECTLY COMPARABLE 处理，除非另有明确协议等价证据；本轮没有这样的数值排名。
