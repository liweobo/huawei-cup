# Mechanism Model Family

## Candidates

回归/参数估计、差分或 ODE、Markov/状态空间、守恒方程、机理+残差混合模型。

## Fit

状态变量、作用机制、边界/初值、单位和参数识别条件能够从题面、数据或可靠来源建立；外推边界可说明。

进入 Primary 或正式唯一数值求解前，必须建立并通过 [`../mechanism-closure.md`](../mechanism-closure.md)。Closure 只判断当前声明的模型是否在数学上闭合，不等于物理真实性或实验验证。缺少 essential input 时降级为 `PARAMETRIC`、`SCENARIO_ASSUMED`、`PARTIAL` 或 `UNVERIFIED`，不得静默补值。

## Baseline / Primary

简化增长/差分/持久性模型是 Baseline；有机理证据、量纲闭合和参数验证时 ODE、Markov 或状态空间可作 Primary。

## Data / Validation

检查残差、轨迹误差、守恒、参数区间、可识别性、初值敏感度和结构变化；不要用拟合掩盖错误机制。

## Common Misuse

为了显得数学而造方程；单位不闭合；把稳态当短期预测；未验证马尔可夫性或初值就外推。
