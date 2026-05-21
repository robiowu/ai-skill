# Spec: 设计审查 (Design Review)

## ADDED Requirements

### Requirement: 自动识别 Skill 类型
系统 SHALL 根据用户描述的 skill 意图，自动将其归类为以下类型之一：Generator、Reviewer、Pipeline、Tool Wrapper、Case-Driven，或标记为 Hybrid。

#### Scenario: 识别 Generator 型 skill
- **WHEN** 用户描述一个接收数据输入、经过处理、输出文件/报告的 skill（如"分析代码变更生成 QA 报告"）
- **THEN** 系统 SHALL 将其识别为 Generator 型，并提示该校验步骤不可省略

#### Scenario: 识别 Reviewer 型 skill
- **WHEN** 用户描述一个接收制品和规则、逐条检查、输出审查报告的 skill（如"审查 skill 的质量"）
- **THEN** 系统 SHALL 将其识别为 Reviewer 型，并提示检查清单需外置到 references/

#### Scenario: 无法确定类型
- **WHEN** 用户描述过于模糊，无法明确归类到单一类型
- **THEN** 系统 SHALL 标记为 "待确认"，列出可能的类型及其适用场景，请用户选择

### Requirement: 按 8 条核心原则逐项审查
系统 SHALL 对 skill 设计按 8 条核心原则（步骤分离、功能独立、一致性校验、过程可量化、评估规则化、降级必有路、知识案例化、反模式自检）逐项审查，输出通过/未通过/不适用。

#### Scenario: 审查 Generator 型 skill 的一致性校验
- **WHEN** 用户提供了一个 Generator 型 skill 设计，其中输出步骤后没有校验步骤
- **THEN** 系统 SHALL 标记原则 3（一致性校验）为"未通过"，严重度标记为 Error，并建议添加复核步骤

#### Scenario: 审查无外部依赖的 skill 的降级路径
- **WHEN** 用户提供的 skill 设计不依赖任何外部工具或 MCP 服务
- **THEN** 系统 SHALL 标记原则 6（降级必有路）为"不适用（N/A）"，并在审查报告中显式注明原因

#### Scenario: 审查包含案例库的 skill
- **WHEN** 用户提供的 skill 包含 `cases/` 目录
- **THEN** 系统 SHALL 额外检查案例文件的触发模式是否可机械匹配、检查规则是否可操作

### Requirement: 输出结构化审查报告
系统 SHALL 按统一模板输出审查报告，包含类型识别、维度评估表、严重度分级的问题汇总、设计评分和 Top-N 改进建议。

#### Scenario: 完整的审查报告
- **WHEN** 审查完成
- **THEN** 报告 SHALL 包含：类型识别 + 匹配度、5 个维度的逐项评估表、🔴/🟡/🔵 三级发现汇总、10 分制设计评分、Top 3 改进建议

#### Scenario: 标记无法评估的维度
- **WHEN** 某个维度的所有检查项均为 N/A
- **THEN** 该维度 SHALL 仍在报告中出现，但标注"不适用——该 skill 不涉及此维度关注的内容"
