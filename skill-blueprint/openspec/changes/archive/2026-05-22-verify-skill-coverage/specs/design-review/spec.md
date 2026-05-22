# Delta Spec: 设计审查 (Design Review)

> 更新原则数量从 8 条到 9 条（v2 新增原则 9：复杂流程分治），
> 补充原则 9 的审查场景。

## MODIFIED Requirements

### Requirement: 按 9 条核心原则逐项审查
系统 SHALL 对 skill 设计按 9 条核心原则（步骤分离、功能独立、一致性校验、过程可量化、评估规则化、降级必有路、知识案例化、反模式自检、复杂流程分治）逐项审查，输出通过/未通过/不适用。

#### Scenario: 审查 Generator 型 skill 的一致性校验
- **WHEN** 用户提供了一个 Generator 型 skill 设计，其中输出步骤后没有校验步骤
- **THEN** 系统 SHALL 标记原则 3（一致性校验）为"未通过"，严重度标记为 Error，并建议添加复核步骤

#### Scenario: 审查无外部依赖的 skill 的降级路径
- **WHEN** 用户提供的 skill 设计不依赖任何外部工具或 MCP 服务
- **THEN** 系统 SHALL 标记原则 6（降级必有路）为"不适用（N/A）"，并在审查报告中显式注明原因

#### Scenario: 审查包含案例库的 skill
- **WHEN** 用户提供的 skill 包含 `cases/` 目录
- **THEN** 系统 SHALL 额外检查案例文件的触发模式是否可机械匹配、检查规则是否可操作

#### Scenario: 审查原则 9——满足分治条件的 skill
- **WHEN** 被设计 skill 涉及 ≥5 个串行步骤且每步中间数据量较大（预估单次上下文承载压力）
- **THEN** 系统 SHALL 标记原则 9（复杂流程分治）为"通过"或"未通过"——检查设计是否包含 subagent 拆解策略和 progress.md 追踪机制。若缺失则标记"未通过"，严重度 Warning，建议参考 `complex-workflow-guide.md`

#### Scenario: 审查原则 9——不满足分治条件的 skill
- **WHEN** 被设计 skill 步骤数 < 5 且无大量中间数据
- **THEN** 系统 SHALL 标记原则 9 为"不适用（N/A）"，注明"该 skill 流程简单无需分治"
