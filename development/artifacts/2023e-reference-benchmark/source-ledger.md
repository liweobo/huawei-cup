# Source Ledger

POST_HOC REFERENCE；主集合为用户指定 GitHub E题目录。**reference_quality: HIGH** 指全文覆盖、可追踪来源与奖项核验，绝不代表所有模型或分数可靠。

目录按 commit `cd5be91735ebf11d5ee52eb170e86a6d07131977` 固定，共10个PDF、821页，全部取得。队号、学校、作者与官方最终名单匹配：10/10为一等奖；P01另为数模之星提名，P08另为季军。官方名单核验不保证转载PDF逐字等于提交原版。

FULL_TEXT_COVERAGE: 10/10。fully reviewed = 九小问相关正文方法、结果、验证与局限已审读；通用推导/背景略读，附录择项静态核查。没有执行论文代码，也没有逐行审计821页。页码均为物理PDF页码，含封面。

[目录与下载清单](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/inventory.json)；[官方逐队匹配](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/official-award-matches.json)；[逐篇逐问审读](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/source-notes.md)。

## Primary directory

- source_id: SET-E2023
- filename: directory-listing.json
- paper_title: 2023年优秀论文/E（集合，非论文）
- authors: zhanwen/MathModel 公开仓库维护者；非各论文作者
- institution: UNKNOWN
- url: https://github.com/zhanwen/MathModel/tree/master/国赛论文/2023年优秀论文/E
- source_type: EXCELLENT_SOLUTION_REFERENCE_SET
- claimed_award: 优秀论文目录
- award_verified: UNKNOWN（集合名称本身不认证奖项）
- award_level: UNKNOWN（逐篇见下文）
- verification_source: GitHub Contents API、固定commit、PDF元数据
- publication_status: 公开GitHub集合
- full_text_available: YES，10份PDF
- questions_covered: Q1a–Q3c
- confidence: HIGH（目录枚举）；奖项另查官方

## R-A01 Official final awards

- source_id: R-A01
- filename: R-A01-awards.xlsx
- paper_title: “华为杯”第二十届中国研究生数学建模竞赛获奖名单
- authors: 中国研究生数学建模竞赛发布机构；个人作者UNKNOWN
- institution: 竞赛官方
- url: https://cpipc.acge.org.cn/sysFile/downFile.do?fileId=8e7956d9a59d455ebd3866f46b155c60
- source_type: Level A，官方最终获奖名单
- claimed_award: 逐队正式奖项
- award_verified: YES
- award_level: 见E题sheet逐队记录
- verification_source: https://cpipc.acge.org.cn/cw/contestPrevious/detail/4/2c9080178e2ad878018e5605f45e156d?page=0
- publication_status: 官方发布（2023-12-17报道附件）
- full_text_available: YES，名单全文；不是方法论文
- questions_covered: NONE；用于题号/队伍/奖项核验
- confidence: HIGH
- sha256: 17060ea295068f33ad27407cd4db87dd5b802857539bea1f1f8edf8f9ca101d2

## P01

- source_id: P01
- filename: E23100650012.pdf
- paper_title: 出血性脑卒中临床智能诊疗建模
- authors: 邢雅媛、张庆薇、李祺
- institution: 天津师范大学
- url: https://github.com/zhanwen/MathModel/blob/cd5be91735ebf11d5ee52eb170e86a6d07131977/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2023%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E23100650012.pdf
- source_type: EXCELLENT_SOLUTION_REFERENCE；公开第三方论文集合内的完整参赛稿，队伍身份另由官方核验
- claimed_award: 目录称优秀论文；不以目录名证明奖项
- award_verified: YES
- award_level: 一等奖(数模之星提名奖)
- verification_source: R-A01 官方最终名单 E题 sheet 第3行，队号23100650012；PDF封面队号/学校/作者对应；作者次序按官方表记录
- publication_status: 公开参赛论文；未核实本稿另有正式期刊版本
- full_text_available: YES；59页完整PDF；正文九小问均审读
- questions_covered: Q1a, Q1b, Q2a, Q2b, Q2c, Q2d, Q3a, Q3b, Q3c
- confidence: HIGH：来源身份与方法内容；统计有效性逐项判断，非自动HIGH
- sha256: 8d1abbc798cc27e01322cb36adfe87c716f9425ad3b07d97c822a0c756fc41f3
- repository_commit: cd5be91735ebf11d5ee52eb170e86a6d07131977
- local_evidence: [PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P01.pdf)；[分页文本](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P01-pages.json)；[下载校验](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P01-meta.json)

## P02

- source_id: P02
- filename: E23102550019.pdf
- paper_title: 出血性脑卒中临床智能诊疗模型的建立
- authors: 靖执义、贺祖鹏、王素素
- institution: 东华大学
- url: https://github.com/zhanwen/MathModel/blob/cd5be91735ebf11d5ee52eb170e86a6d07131977/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2023%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E23102550019.pdf
- source_type: EXCELLENT_SOLUTION_REFERENCE；公开第三方论文集合内的完整参赛稿，队伍身份另由官方核验
- claimed_award: 目录称优秀论文；不以目录名证明奖项
- award_verified: YES
- award_level: 一等奖
- verification_source: R-A01 官方最终名单 E题 sheet 第8行，队号23102550019；PDF封面队号/学校/作者对应；作者次序按官方表记录
- publication_status: 公开参赛论文；未核实本稿另有正式期刊版本
- full_text_available: YES；68页完整PDF；正文九小问均审读
- questions_covered: Q1a, Q1b, Q2a, Q2b, Q2c, Q2d, Q3a, Q3b, Q3c
- confidence: HIGH：来源身份与方法内容；统计有效性逐项判断，非自动HIGH
- sha256: 7111ae76a0a000ae0667979809bb38eef9ce74f9a05dfbdfaae39cb50889d563
- repository_commit: cd5be91735ebf11d5ee52eb170e86a6d07131977
- local_evidence: [PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P02.pdf)；[分页文本](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P02-pages.json)；[下载校验](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P02-meta.json)

## P03

- source_id: P03
- filename: E23103530067.pdf
- paper_title: 出血性脑卒中患者预后预测与治疗智能模型构建
- authors: 王振宽、郭娜、潘苏
- institution: 浙江工商大学
- url: https://github.com/zhanwen/MathModel/blob/cd5be91735ebf11d5ee52eb170e86a6d07131977/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2023%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E23103530067.pdf
- source_type: EXCELLENT_SOLUTION_REFERENCE；公开第三方论文集合内的完整参赛稿，队伍身份另由官方核验
- claimed_award: 目录称优秀论文；不以目录名证明奖项
- award_verified: YES
- award_level: 一等奖
- verification_source: R-A01 官方最终名单 E题 sheet 第7行，队号23103530067；PDF封面队号/学校/作者对应；作者次序按官方表记录
- publication_status: 公开参赛论文；未核实本稿另有正式期刊版本
- full_text_available: YES；85页完整PDF；正文九小问均审读
- questions_covered: Q1a, Q1b, Q2a, Q2b, Q2c, Q2d, Q3a, Q3b, Q3c
- confidence: HIGH：来源身份与方法内容；统计有效性逐项判断，非自动HIGH
- sha256: 832ce085bf76e77e99333a3d0d1e291ea4d434340c819d6286471a5cabb94311
- repository_commit: cd5be91735ebf11d5ee52eb170e86a6d07131977
- local_evidence: [PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P03.pdf)；[分页文本](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P03-pages.json)；[下载校验](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P03-meta.json)

## P04

- source_id: P04
- filename: E23103570015.pdf
- paper_title: 出血性脑卒中临床智能诊疗建模
- authors: 李亚男、李嘉贝、赵雪倩
- institution: 安徽大学
- url: https://github.com/zhanwen/MathModel/blob/cd5be91735ebf11d5ee52eb170e86a6d07131977/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2023%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E23103570015.pdf
- source_type: EXCELLENT_SOLUTION_REFERENCE；公开第三方论文集合内的完整参赛稿，队伍身份另由官方核验
- claimed_award: 目录称优秀论文；不以目录名证明奖项
- award_verified: YES
- award_level: 一等奖
- verification_source: R-A01 官方最终名单 E题 sheet 第6行，队号23103570015；PDF封面队号/学校/作者对应；作者次序按官方表记录
- publication_status: 公开参赛论文；未核实本稿另有正式期刊版本
- full_text_available: YES；138页完整PDF；正文九小问均审读
- questions_covered: Q1a, Q1b, Q2a, Q2b, Q2c, Q2d, Q3a, Q3b, Q3c
- confidence: HIGH：来源身份与方法内容；统计有效性逐项判断，非自动HIGH
- sha256: 99a2b9a48592421914ec0a8f81e08bd96c8d4c1dab887b19df9efef2c260e718
- repository_commit: cd5be91735ebf11d5ee52eb170e86a6d07131977
- local_evidence: [PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P04.pdf)；[分页文本](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P04-pages.json)；[下载校验](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P04-meta.json)

## P05

- source_id: P05
- filename: E23104030073.pdf
- paper_title: 出血性脑卒中临床智能诊疗建模分析
- authors: 于梓涵、陈昊、周滢
- institution: 南昌大学
- url: https://github.com/zhanwen/MathModel/blob/cd5be91735ebf11d5ee52eb170e86a6d07131977/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2023%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E23104030073.pdf
- source_type: EXCELLENT_SOLUTION_REFERENCE；公开第三方论文集合内的完整参赛稿，队伍身份另由官方核验
- claimed_award: 目录称优秀论文；不以目录名证明奖项
- award_verified: YES
- award_level: 一等奖
- verification_source: R-A01 官方最终名单 E题 sheet 第10行，队号23104030073；PDF封面队号/学校/作者对应；作者次序按官方表记录
- publication_status: 公开参赛论文；未核实本稿另有正式期刊版本
- full_text_available: YES；60页完整PDF；正文九小问均审读
- questions_covered: Q1a, Q1b, Q2a, Q2b, Q2c, Q2d, Q3a, Q3b, Q3c
- confidence: HIGH：来源身份与方法内容；统计有效性逐项判断，非自动HIGH
- sha256: 66de2190ed124bc167b6f408ffd5e8be3202754d32a11784bbc049ccc60f2cfe
- repository_commit: cd5be91735ebf11d5ee52eb170e86a6d07131977
- local_evidence: [PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P05.pdf)；[分页文本](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P05-pages.json)；[下载校验](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P05-meta.json)

## P06

- source_id: P06
- filename: E23105330424.pdf
- paper_title: 出血性脑卒中临床智能诊疗建模
- authors: 史代双、梁时清、华明清
- institution: 中南大学
- url: https://github.com/zhanwen/MathModel/blob/cd5be91735ebf11d5ee52eb170e86a6d07131977/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2023%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E23105330424.pdf
- source_type: EXCELLENT_SOLUTION_REFERENCE；公开第三方论文集合内的完整参赛稿，队伍身份另由官方核验
- claimed_award: 目录称优秀论文；不以目录名证明奖项
- award_verified: YES
- award_level: 一等奖
- verification_source: R-A01 官方最终名单 E题 sheet 第4行，队号23105330424；PDF封面队号/学校/作者对应；作者次序按官方表记录
- publication_status: 公开参赛论文；未核实本稿另有正式期刊版本
- full_text_available: YES；115页完整PDF；正文九小问均审读
- questions_covered: Q1a, Q1b, Q2a, Q2b, Q2c, Q2d, Q3a, Q3b, Q3c
- confidence: HIGH：来源身份与方法内容；统计有效性逐项判断，非自动HIGH
- sha256: f9cacb683377d24ebc45ff1d0ab853156fe6c787c0406d7275202b91e4f6505a
- repository_commit: cd5be91735ebf11d5ee52eb170e86a6d07131977
- local_evidence: [PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P06.pdf)；[分页文本](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P06-pages.json)；[下载校验](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P06-meta.json)

## P07

- source_id: P07
- filename: E23106730076.pdf
- paper_title: 出血性脑卒中临床智能诊疗建模
- authors: 杨双萍、郑润泽、黄照煜
- institution: 云南大学
- url: https://github.com/zhanwen/MathModel/blob/cd5be91735ebf11d5ee52eb170e86a6d07131977/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2023%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E23106730076.pdf
- source_type: EXCELLENT_SOLUTION_REFERENCE；公开第三方论文集合内的完整参赛稿，队伍身份另由官方核验
- claimed_award: 目录称优秀论文；不以目录名证明奖项
- award_verified: YES
- award_level: 一等奖
- verification_source: R-A01 官方最终名单 E题 sheet 第9行，队号23106730076；PDF封面队号/学校/作者对应；作者次序按官方表记录
- publication_status: 公开参赛论文；未核实本稿另有正式期刊版本
- full_text_available: YES；109页完整PDF；正文九小问均审读
- questions_covered: Q1a, Q1b, Q2a, Q2b, Q2c, Q2d, Q3a, Q3b, Q3c
- confidence: HIGH：来源身份与方法内容；统计有效性逐项判断，非自动HIGH
- sha256: e4aa59bc348d6f5024845eac75be973e12ab911e8566198f8a405bf2896fcc15
- repository_commit: cd5be91735ebf11d5ee52eb170e86a6d07131977
- local_evidence: [PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P07.pdf)；[分页文本](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P07-pages.json)；[下载校验](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P07-meta.json)

## P08

- source_id: P08
- filename: E23106980022.pdf
- paper_title: 出血性脑卒中临床智能诊疗建模
- authors: 钟朝彬、李程子、林宏伟
- institution: 西安交通大学
- url: https://github.com/zhanwen/MathModel/blob/cd5be91735ebf11d5ee52eb170e86a6d07131977/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2023%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E23106980022.pdf
- source_type: EXCELLENT_SOLUTION_REFERENCE；公开第三方论文集合内的完整参赛稿，队伍身份另由官方核验
- claimed_award: 目录称优秀论文；不以目录名证明奖项
- award_verified: YES
- award_level: 一等奖(“数模之星”季军)
- verification_source: R-A01 官方最终名单 E题 sheet 第2行，队号23106980022；PDF封面队号/学校/作者对应；作者次序按官方表记录
- publication_status: 公开参赛论文；未核实本稿另有正式期刊版本
- full_text_available: YES；53页完整PDF；正文九小问均审读
- questions_covered: Q1a, Q1b, Q2a, Q2b, Q2c, Q2d, Q3a, Q3b, Q3c
- confidence: HIGH：来源身份与方法内容；统计有效性逐项判断，非自动HIGH
- sha256: 99b5b15c57778b8b82b5763759c0ba25adcbc232af0487c8e83e4b0e9498df71
- repository_commit: cd5be91735ebf11d5ee52eb170e86a6d07131977
- local_evidence: [PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P08.pdf)；[分页文本](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P08-pages.json)；[下载校验](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P08-meta.json)

## P09

- source_id: P09
- filename: E23107030070.pdf
- paper_title: 出血性脑卒中临床智能诊疗建模
- authors: 郭歌、张倩文、毕菲菲
- institution: 西安建筑科技大学
- url: https://github.com/zhanwen/MathModel/blob/cd5be91735ebf11d5ee52eb170e86a6d07131977/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2023%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E23107030070.pdf
- source_type: EXCELLENT_SOLUTION_REFERENCE；公开第三方论文集合内的完整参赛稿，队伍身份另由官方核验
- claimed_award: 目录称优秀论文；不以目录名证明奖项
- award_verified: YES
- award_level: 一等奖
- verification_source: R-A01 官方最终名单 E题 sheet 第11行，队号23107030070；PDF封面队号/学校/作者对应；作者次序按官方表记录
- publication_status: 公开参赛论文；未核实本稿另有正式期刊版本
- full_text_available: YES；73页完整PDF；正文九小问均审读
- questions_covered: Q1a, Q1b, Q2a, Q2b, Q2c, Q2d, Q3a, Q3b, Q3c
- confidence: HIGH：来源身份与方法内容；统计有效性逐项判断，非自动HIGH
- sha256: d99c0cb9b31c99f936581611e05b388bd686a629c56343ec3ed8a3f3317918ee
- repository_commit: cd5be91735ebf11d5ee52eb170e86a6d07131977
- local_evidence: [PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P09.pdf)；[分页文本](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P09-pages.json)；[下载校验](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P09-meta.json)

## P10

- source_id: P10
- filename: E23900310014.pdf
- paper_title: 出血性脑卒中临床智能诊疗建模
- authors: 范柯雨、陈炳杰、张婉婷
- institution: 清华大学深圳国际研究生院；清华大学
- url: https://github.com/zhanwen/MathModel/blob/cd5be91735ebf11d5ee52eb170e86a6d07131977/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2023%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/E/E23900310014.pdf
- source_type: EXCELLENT_SOLUTION_REFERENCE；公开第三方论文集合内的完整参赛稿，队伍身份另由官方核验
- claimed_award: 目录称优秀论文；不以目录名证明奖项
- award_verified: YES
- award_level: 一等奖
- verification_source: R-A01 官方最终名单 E题 sheet 第5行，队号23900310014；PDF封面队号/学校/作者对应；作者次序按官方表记录
- publication_status: 公开参赛论文；未核实本稿另有正式期刊版本
- full_text_available: YES；61页完整PDF；正文九小问均审读
- questions_covered: Q1a, Q1b, Q2a, Q2b, Q2c, Q2d, Q3a, Q3b, Q3c
- confidence: HIGH：来源身份与方法内容；统计有效性逐项判断，非自动HIGH
- sha256: 0914108a57671c543943fbf922a5b49908fe24673790609a1012e1165f83e2b5
- repository_commit: cd5be91735ebf11d5ee52eb170e86a6d07131977
- local_evidence: [PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P10.pdf)；[分页文本](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P10-pages.json)；[下载校验](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/primary-set/P10-meta.json)

## Prior search record

上一轮官方入口、高校新闻、正式发表文章、作者仓库及第三方搜索记录原样保存在 [旧source-ledger](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/prior-pass-6e5d1b6/source-ledger.md) 和受保护的sources中。本轮不把旧材料重复计入10篇共识分母，不把旧版“未获得可核验获奖全文”的检索结论当作当前结论。当前摘要冻结前已披露上轮参考阅读，不宣称再次盲跑。
