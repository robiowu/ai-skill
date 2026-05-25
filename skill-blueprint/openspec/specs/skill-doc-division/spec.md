# Spec: Skill/README 文档分工 (Skill-Doc Division)

> 定义 SKILL.md（AI 执行指令）与 README.md（人类可读文档）的职责边界，消除内容重复，建立单一真实来源。

## ADDED Requirements

### Requirement: SKILL.md 为执行流程唯一真实来源
SKILL.md SHALL 包含完整的执行工作流、阶段切换规则、设计原则及解析、参考文件索引。这些内容 SHALL 不在 README.md 中重复出现。

#### Scenario: 原则只在 SKILL.md 中维护
- **WHEN** skill 定义了设计原则（如 9 条核心原则）
- **THEN** 原则的完整列表和解析 SHALL 仅存在于 SKILL.md 中
- **AND** README.md SHALL 不包含原则列表副本

#### Scenario: 阶段详情只在 SKILL.md 中维护
- **WHEN** skill 包含多阶段工作流（如 Stage 1/2/3）
- **THEN** 各阶段的详细描述、检查项、评分公式 SHALL 仅存在于 SKILL.md 中
- **AND** README.md SHALL 不包含阶段详情副本

### Requirement: README.md 为人类可读概览
README.md SHALL 只包含概览层内容，不重复 SKILL.md 的执行工作流。必含内容：定位（一句话）、触发方式（关键词列表）、目录结构、设计溯源、快速开始。可含内容：背景动机、技术栈说明、FAQ。

#### Scenario: README.md 最小内容
- **WHEN** README.md 存在
- **THEN** 它 SHALL 至少包含：skill 定位、触发关键词、目录结构、快速开始步骤

#### Scenario: README.md 不得重复工作流
- **WHEN** README.md 包含与 SKILL.md 逐字重复的三阶段描述或原则列表
- **THEN** 系统 SHALL 标记为 Warning（-0.5 分），提示"内容与 SKILL.md 重复，一处修改两处同步易遗漏"

### Requirement: README.md 必须包含到 SKILL.md 的显式导航
README.md SHALL 在显著位置（文档顶部或快速开始之后）包含指向 SKILL.md 的导航，引导读者获取完整信息。

#### Scenario: 导航格式
- **WHEN** README.md 存在
- **THEN** 它 SHALL 包含类似 `> 完整执行流程、设计原则及参考文件索引见 [SKILL.md](./SKILL.md)` 的导航语句

#### Scenario: 导航缺失
- **WHEN** README.md 存在但无指向 SKILL.md 的导航
- **THEN** 系统 SHALL 标记为 Info（🔵），提示添加交叉引用
