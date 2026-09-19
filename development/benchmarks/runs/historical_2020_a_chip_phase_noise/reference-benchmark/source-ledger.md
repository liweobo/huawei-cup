# Source Ledger

Primary listing: [2020 excellent papers, A](https://github.com/zhanwen/MathModel/tree/master/国赛论文/2020年优秀论文/A)

The directory name establishes membership in the repository's excellent-paper collection. It does not establish an official prize level; all award levels below are `UNKNOWN`.

| reference_id | filename | title | authors / institution | URL | Git blob SHA | SHA256 | pages | extraction | visual check | award / verified | Q1-Q4 |
|---|---|---|---|---|---|---|---:|---|---|---|---|
| R1 | A20102460127.pdf | ASIC 芯片上的载波恢复 DSP 算法设计与实现 | Xu Jin, Xiao Hanwei, Song Fengli / Fudan University | [raw PDF](https://github.com/zhanwen/MathModel/raw/refs/heads/master/国赛论文/2020年优秀论文/A/A20102460127.pdf) | `feb658a66c0c05f033bcaa7ab26750c0a640a5d2` | `8de4a237ed275cbc550cf64f7b6921423155f92c8fca7426fbe8f1268e8f40fa` | 40 | full, 40/40 non-empty, no errors | title, model, ASIC pages rendered | UNKNOWN / false | yes |
| R2 | A20102480161.pdf | ASIC 芯片上的载波恢复 DSP 算法设计与实现 | Ding Gengfa, Wang Zelong, Xu Jiyong / Shanghai Jiao Tong University | [raw PDF](https://github.com/zhanwen/MathModel/raw/refs/heads/master/国赛论文/2020年优秀论文/A/A20102480161.pdf) | `b6749049535e0b00fa15e1c812473713d43b93b2` | `f1e02781f2fc0d3b7f2ee46076a1be5758e9579a5d34acec760beb79cb9cb269` | 35 | full, 35/35 non-empty, no errors | title, model, resource pages rendered | UNKNOWN / false | yes |
| R3 | A20104870015.pdf | 载波恢复算法设计及实现 | Li Zhi, Pi Jianyuan, Ji Qiuhan / Huazhong University of Science and Technology | [raw PDF](https://github.com/zhanwen/MathModel/raw/refs/heads/master/国赛论文/2020年优秀论文/A/A20104870015.pdf) | `56f4e7e2eb528e331a6af171df8260750a275998` | `66b8d39d1e4fea23ad522b2306b3ded86fb19adc847ac6a045dc6e0318e2ceeb` | 40 | full, 40/40 non-empty, no errors | title, model, results pages rendered | UNKNOWN / false | yes |
| R4 | A20106110086.pdf | 基于通信仿真的载波恢复算法设计与 ASIC 实现 | Wen Fushan, Zhang Honglong, Peng Haoqi / Chongqing University | [raw PDF](https://github.com/zhanwen/MathModel/raw/refs/heads/master/国赛论文/2020年优秀论文/A/A20106110086.pdf) | `038efadc9c1291baefb85ea22d13a30dcd984889` | `fcd0c70f9d7c97fa1ceaec699d85f000b9401f220791695f7de2468468e1659c` | 40 | full, 40/40 non-empty, no errors | title, formula, resource pages rendered | UNKNOWN / false | yes |
| R5 | A20910040037.pdf | ASIC 芯片上的载波恢复 DSP 算法设计与实现 | Cui Zhichao, Liao Chengjian, Yang Yaoqi / Army Engineering University | [raw PDF](https://github.com/zhanwen/MathModel/raw/refs/heads/master/国赛论文/2020年优秀论文/A/A20910040037.pdf) | `dd5b5e7c02a7e28b21f9878337f61a1d1a64a07e` | `83be5a44b5fa122bcd2c73e5d4eaa7c885334f425091b93acf2eea1cb2465b4d` | 43 | full, 43/43 non-empty, no errors | title, model, Q4 pages rendered | UNKNOWN / false | yes |

## Structured extraction fields

The following fields are intentionally concise; detailed evidence is in the comparison files.

| reference | main algorithm family | signal model | phase-noise model | dispersion model | BER protocol | resource model | reported result | confidence |
|---|---|---|---|---|---|---|---|---|
| R1 | pilot phase de-spiking + linear interpolation; LUT fixed point | 16QAM, baud-rate samples | discrete random walk | quadratic FFT phase + conjugate inverse | BER `0.02`, RSNR cost `<0.3 dB` | operation/LUT/buffer proxy | gap 2900; overhead `~3.45e-4`; 10-bit fixed point | medium |
| R2 | pilot averaging + LS/MAP-style estimation | 16QAM, OSR=8, matched filter/downsample | Wiener process | quadratic FFT phase + conjugate inverse | BER `0.02`, impaired/AWGN SNR difference | pipeline and operation-count proxy | abstract overhead `3.13%`; variable pilot/width search | medium |
| R3 | pilot block averaging + interpolation | 16QAM, discrete symbol model | cumulative variance / random walk | quadratic FFT phase + inverse | BER `0.02`, analytic/Monte Carlo baseline | quantization-noise and resource function | 9/826, `1.09%`; width regimes by linewidth | medium |
| R4 | endpoint pilots + FFT window + linear interpolation + decoupling | 16QAM, windowed frames | Wiener increments | quadratic phase plus frequency-shift decoupling | BER `0.02`, window/RSNR sweeps | operation table and clock proxy | `2/256`; 4- or 7-fraction-bit options | medium-high |
| R5 | CRAP1 pilot enumeration; Taylor/LUT fixed point | 16QAM, `nfft=512`/OSR=8 in appendix | discrete random walk | quadratic FFT phase + conjugate inverse | BER `0.02`, error-count stopping | analytic U/clock proxy | abstract `1/1024`; automatic width feedback | medium |

Raw URL pattern: `https://github.com/zhanwen/MathModel/raw/refs/heads/master/国赛论文/2020年优秀论文/A/<filename>`.

Extraction used `pdfplumber`; representative page PNGs were rendered with bundled Poppler. PDFs and rendered intermediates remain untracked and are intentionally excluded from the commit.
