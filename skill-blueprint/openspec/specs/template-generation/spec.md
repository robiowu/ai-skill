# Spec: 模板生成 (Template Generation)

## ADDED Requirements

### Requirement: 按类型推荐目录结构
系统 SHALL 根据识别的 skill 类型，推荐对应的目录结构模板，明确哪些目录是必须的、哪些是可选的。

#### Scenario: Generator 型目录结构
- **WHEN** skill 被识别为 Generator 型
- **THEN** 推荐结构 SHALL 包含：`SKILL.md`（必须）、`scripts/`（必须）、`README.md`（必须）、`cases/`（可选）、`references/`（可选）

#### Scenario: Reviewer 型目录结构
- **WHEN** skill 被识别为 Reviewer 型
- **THEN** 推荐结构 SHALL 包含：`SKILL.md`（必须）、`references/`（必须，存放检查清单）、`README.md`（必须）

#### Scenario: Case-Driven 型目录结构
- **WHEN** skill 被识别为 Case-Driven 型
- **THEN** 推荐结构 SHALL 包含：`cases/`（必须，含 README.md 案例规范）、`SKILL.md`（必须）、`README.md`（必须）

### Requirement: 按类型推荐工作流模板
系统 SHALL 根据 skill 类型推荐对应的 Phase/Step 工作流骨架。

#### Scenario: Pipeline 型工作流
- **WHEN** skill 为 Pipeline 型
- **THEN** 推荐的工作流 SHALL 包含：每步编号、门控标记（✅/⏭️/❌）、步骤间数据传递声明、降级路径预留

#### Scenario: Generator 型工作流
- **WHEN** skill 为 Generator 型
- **THEN** 推荐的工作流 SHALL 包含：数据采集阶段（脚本）、数据分析阶段（AI）、结果校验阶段（AI 自检）、文件生成阶段（脚本）

### Requirement: 模板包含关键约束提示
系统 SHALL 在推荐模板时附带类型特定的关键约束。

#### Scenario: 为 Generator 型附加约束
- **WHEN** 推荐 Generator 型模板
- **THEN** 约束提示 SHALL 包含：数据采集必须脚本化、输出步骤后必须有校验步骤、校验日志必须可见

#### Scenario: 为 Reviewer 型附加约束
- **WHEN** 推荐 Reviewer 型模板
- **THEN** 约束提示 SHALL 包含：检查清单必须外置 references/、评分公式必须可复现、N/A 项目必须显式标记
