# Spec: 质量评分 (Quality Scoring)

## ADDED Requirements

### Requirement: 5 维度评分体系
系统 SHALL 按 5 个设计维度对 skill 进行评分：结构合规性、脚本分离度、自校验机制、降级健壮性、知识可沉淀性。每维度包含 3-4 个检查项。

#### Scenario: 结构合规性评分
- **WHEN** 评估结构合规性维度
- **THEN** 系统 SHALL 检查：步骤是否分离（2 项）、是否有门控标记（1 项）、步骤粒度是否适中（1 项），每项输出 ✅/❌/➖

#### Scenario: 所有维度均不适用
- **WHEN** skill 极其简单（如纯 Tool Wrapper，只有参数转发无业务逻辑）
- **THEN** 系统 SHALL 仍输出所有 5 个维度，不适用的维度标注 N/A 并说明原因

### Requirement: 10 分制设计评分
系统 SHALL 按机械公式（起始 10 分，Error -2，Warning -0.5，底线 1 分）计算设计评分，并结合定性判断进行 ±1 分的调整。

#### Scenario: 有多个 Error 的 skill
- **WHEN** 审查发现 2 个 Error 和 3 个 Warning
- **THEN** 机械评分 SHALL 为 10 - 2×2 - 3×0.5 = 4.5 分，定性调整不超过 ±1

#### Scenario: 无可扣分项但设计特别精妙
- **WHEN** 审查发现 0 个 Error、0 个 Warning，且设计中有创新的自校验机制或案例驱动方案
- **THEN** 机械评分 SHALL 为 10 分，可 +1 定性调整为 10 分（上限 10）

### Requirement: 严重度三级分类
系统 SHALL 对每个发现的问题标注严重度：🔴 设计缺陷（必须修复）、🟡 设计偏离（建议修复）、🔵 设计优化（可以改进）。

#### Scenario: 步骤混在一个段落中
- **WHEN** skill 的工作流描述将所有步骤堆在连续段落中，无编号无门控
- **THEN** 系统 SHALL 标记为 🔴 设计缺陷（必须修复），因为步骤分离是基础结构要求

#### Scenario: 缺少反模式机制
- **WHEN** skill 没有反模式自检机制
- **THEN** 系统 SHALL 标记为 🔵 设计优化（可以改进），因为反模式机制是加分项而非强制要求

### Requirement: Top-N 改进建议
系统 SHALL 按影响程度排序，输出至少 3 条、最多 5 条的改进建议。

#### Scenario: 建议排序
- **WHEN** 存在 5 个以上的发现项
- **THEN** Top-N 建议 SHALL 优先包含 Error 级别发现，其次 Warning，Info 不进入 Top-N（除非总发现数不足 3 条）
