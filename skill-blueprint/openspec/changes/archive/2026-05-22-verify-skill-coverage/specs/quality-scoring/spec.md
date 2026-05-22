# Delta Spec: 质量评分 (Quality Scoring)

> 扩展为同时覆盖 Stage 1 设计评分（5 维度）和 Stage 3 评估评分（6 维度）。
> 两者共用相同的评分公式和严重度体系，差异仅在检查维度数量和检查项内容。

## MODIFIED Requirements

### Requirement: 5 维度设计评分体系（Stage 1）
系统 SHALL 按 5 个设计维度对 skill 进行评分：结构合规性、脚本分离度、自校验机制、降级健壮性、知识可沉淀性。每维度包含 3-4 个检查项。本评分体系用于 Stage 1 蓝图设计审查。

#### Scenario: 结构合规性评分
- **WHEN** 评估结构合规性维度
- **THEN** 系统 SHALL 检查：步骤是否分离（2 项）、是否有门控标记（1 项）、步骤粒度是否适中（1 项），每项输出 ✅/❌/➖

#### Scenario: 所有维度均不适用
- **WHEN** skill 极其简单（如纯 Tool Wrapper，只有参数转发无业务逻辑）
- **THEN** 系统 SHALL 仍输出所有 5 个维度，不适用的维度标注 N/A 并说明原因

### Requirement: 6 维度评估评分体系（Stage 3）
系统 SHALL 按 6 个评估维度对已实现 skill 进行质量评分：结构审查、目录审查、内容审查、安全审查、完备性审查、复杂流程分治评估（条件适用）。每维度包含 3-6 个检查项。本评分体系用于 Stage 3 整体评估审查。评分公式与 Stage 1 完全一致，但检查维度不同。

#### Scenario: Stage 3 评估评分——含条件维度
- **WHEN** 被评估 skill 启用了复杂流程分治策略，且评估发现 1 Error（降级声明不具体）和 3 Warning
- **THEN** 机械评分 SHALL 为 10 - 1×2 - 3×0.5 = 6.5 分

#### Scenario: Stage 3 评估评分——无分治策略
- **WHEN** 被评估 skill 未启用复杂流程分治，维度 6 全部 N/A 不记入分母，发现 0 Error 2 Warning
- **THEN** 机械评分 SHALL 为 10 - 0×2 - 2×0.5 = 9 分

### Requirement: 10 分制统一评分公式
系统 SHALL 对 Stage 1 设计评分和 Stage 3 评估评分使用统一的评分公式：起始 10 分，每 Error -2，每 Warning -0.5，Info 不扣分，N/A 项不计入分母，底线 1 分。在此基础上允许 ±1 分的定性调整（上限 10）。

#### Scenario: 有多个 Error 的 skill
- **WHEN** 审查发现 2 个 Error 和 3 个 Warning
- **THEN** 机械评分 SHALL 为 10 - 2×2 - 3×0.5 = 4.5 分，定性调整不超过 ±1

#### Scenario: 无可扣分项但设计特别精妙
- **WHEN** 审查发现 0 个 Error、0 个 Warning，且设计中有创新的自校验机制或案例驱动方案
- **THEN** 机械评分 SHALL 为 10 分，可 +1 定性调整为 10 分（上限 10）

#### Scenario: 评分底线保护
- **WHEN** 多项 Error 导致机械评分 < 1（如 5 Error = 10 - 5×2 = 0）
- **THEN** 评分 SHALL 为底线 1 分，不可为 0 或负数

### Requirement: 严重度三级分类
系统 SHALL 对每个发现的问题标注严重度：🔴 设计缺陷/阻塞性错误（必须修复，-2 分）、🟡 设计偏离/最佳实践违规（建议修复，-0.5 分）、🔵 设计优化/锦上添花（可以改进，不扣分）。此分类在 Stage 1 和 Stage 3 中统一使用。

#### Scenario: 步骤混在一个段落中
- **WHEN** skill 的工作流描述将所有步骤堆在连续段落中，无编号无门控
- **THEN** 系统 SHALL 标记为 🔴 设计缺陷（必须修复），因为步骤分离是基础结构要求，-2 分

#### Scenario: 缺少反模式机制
- **WHEN** skill 没有反模式自检机制
- **THEN** 系统 SHALL 标记为 🔵 设计优化（可以改进），因为反模式机制是加分项而非强制要求，不扣分

#### Scenario: Stage 3 安全严重度——硬编码密钥
- **WHEN** Stage 3 评估发现 SKILL.md 或脚本中包含硬编码 API Key
- **THEN** 系统 SHALL 标记为 🔴 Error（必须修复），-2 分，因为涉及安全风险

### Requirement: Top-N 改进建议
系统 SHALL 按影响程度排序，输出至少 3 条、最多 5 条的改进建议。适用 Stage 1 和 Stage 3。

#### Scenario: 建议排序
- **WHEN** 存在 5 个以上的发现项
- **THEN** Top-N 建议 SHALL 优先包含 Error 级别发现，其次 Warning，Info 不进入 Top-N（除非总发现数不足 3 条）

#### Scenario: Stage 3 建议包含回退指引
- **WHEN** Stage 3 评估发现 Error 级别问题
- **THEN** Top-N 建议末尾 SHALL 包含"建议回到 Stage 2 修复后重新评估"的提示
