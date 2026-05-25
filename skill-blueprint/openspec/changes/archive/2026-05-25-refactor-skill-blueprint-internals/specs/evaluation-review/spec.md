# Delta Spec: 评估审查 — 外部路径自包含性检查

> 在 `evaluation-review` spec 的内容审查维度中新增"外部路径自包含性"检查项。

## ADDED Requirements

### Requirement: 外部路径自包含性检查
系统 SHALL 在内容审查（维度 3）中检查 SKILL.md 是否包含对项目级目录结构的硬编码路径引用。若存在未声明降级路径的项目级引用，标记为 Warning。

#### Scenario: 检测到硬编码 openspec/ 路径且无降级声明
- **WHEN** SKILL.md 包含形如 `openspec/specs/`、`.codemaker/skills/` 或 `../../other-skill/` 的路径引用
- **AND** 该引用未附带降级声明（无"若不可用则以 X 为准"）
- **THEN** 系统 SHALL 标记为 Warning（-0.5 分），提示"路径 `{path}` 假定特定项目结构，skill 独立部署时将断裂。声明降级路径或改用 skill 内部 `references/` 文件"

#### Scenario: 硬编码路径但已有降级声明
- **WHEN** SKILL.md 包含项目级路径引用
- **AND** 该引用附带完整降级声明（`{路径} → 若不可用，{替代} → ⚠️ 标注`）
- **THEN** 系统 SHALL 标记为 Pass（✅），降级声明符合自包含要求

#### Scenario: 无外部路径引用
- **WHEN** SKILL.md 所有路径引用均为 skill 内部文件（`references/`、`scripts/`、`cases/`）
- **THEN** 系统 SHALL 标记为 Pass（✅），无需额外检查
