# Delta Spec: 落地实现 — 禁止硬编码项目级路径

> 在 `implementation-execution` spec 的 SKILL.md 编写规范中新增"禁止硬编码项目级路径"约束。

## ADDED Requirements

### Requirement: SKILL.md 编写规范——路径自包含
系统 SHALL 在指导 SKILL.md 编写时确保不包含对项目级目录结构的硬编码路径引用。所有对 skill 外部资源的引用 SHALL 使用哨兵定位 + 降级声明模式，或改用 skill 内部 `references/` 路径。

#### Scenario: 检测到硬编码路径
- **WHEN** 用户编写 SKILL.md 包含假定特定项目结构的路径（如 `openspec/specs/`、`.codemaker/skills/`、`../../other-skill/scripts/`）
- **THEN** 系统 SHALL 标记为 Warning，提示改为以下两种方式之一：
  - **方案 A（推荐）**：哨兵定位 + 降级声明——`从项目根查找 openspec/specs/{name}/spec.md；若 openspec/ 不存在，以 references/{name}.md 为准`
  - **方案 B**：直接使用 skill 内部 `references/` 路径，不依赖外部结构

#### Scenario: spec 引用的正确写法
- **WHEN** skill 需要引用 OpenSpec 形式化规范文件
- **THEN** 系统 SHALL 建议格式：`形式化规范：从项目根查找 openspec/specs/{name}/spec.md；若 openspec/ 目录不存在（skill 被独立部署），此规范不可用，以 references/{name}.md 为准`

#### Scenario: 纯内部引用无需变更
- **WHEN** SKILL.md 引用 `references/`、`scripts/`、`cases/` 等 skill 内部路径
- **THEN** 系统 SHALL 不做路径相关提示——内部路径天然自包含
