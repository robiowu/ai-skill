## Why

skill-blueprint 作为 skill 全生命周期管理的元 Skill，自身存在三类违反其设计原则的问题：(1) SKILL.md 中 3 处硬编码 `openspec/specs/xxx/spec.md` 项目级路径，导致 skill 不可独立部署——其他项目引用时路径断裂；(2) SKILL.md（~426 行）与 README.md 大量内容重复（三阶段描述、9 条原则），维护需两处同步；(3) SKILL.md 自身超过 Phase 3.3 推荐的 400 行上限，复杂流程分治速查约 50 行可外置——dogfooding 失败。这是从 `AI自助分析工具` 项目的 `refactor-skill-paths-and-docs` 变更中提取的同构问题：硬编码外部路径、文档分散、架构描述与实现不一致。

## What Changes

### 1. SKILL.md 精简至 400 行内
- "复杂流程分治设计速查"整段（~50 行）外置至 `references/complex-workflow-guide.md` 末尾
- Stage 3 各 Phase 检查项表格精简为引用 `references/review-checklist.md`（该文件已含完整检查清单，SKILL.md 中为冗余副本）
- **BREAKING**: Stage 3 的直接检查表不再在 SKILL.md 中可见，AI 需读取 references

### 2. 消除 `openspec/specs/` 硬编码路径
- 3 处 `openspec/specs/xxx/spec.md` 引用改为哨兵定位：通过 `.codemaker/` 或 `openspec/` 目录向上查找 skill 根，再从根出发解析 `openspec/specs/` 路径
- 若 skill 被部署到无 openspec 结构的项目，降级为"形式化规范不可用，以 references/ 中的非规范版为准"
- **BREAKING**: 依赖 openspec 目录作为哨兵文件定位，纯独立 skill 目录（无 openspec/）降级

### 3. SKILL.md 与 README.md 去重分工
- SKILL.md：AI 执行指令，含完整工作流、阶段切换规则、参考文件索引
- README.md：人类可读概览，只保留定位、触发方式、设计溯源、快速开始，不重复三阶段细节和原则列表
- 原则列表从 README.md 移除（SKILL.md 为唯一源头）

### 4. 自指一致性修复
- 确保 skill-blueprint 自身通过 Stage 3 评估（目标分数 9+）
- 降级声明统一用 `{依赖} → {降级行为} → {标注}` 格式（当前存在笼统描述）

## Capabilities

### New Capabilities
- `skill-self-containment`: skill 自包含规范——定义 skill 如何解析内部与外部资源路径，消除对项目级目录结构的硬编码依赖。当 skill 引用 skill 外部资源时，需通过哨兵机制定位或声明降级路径，确保 skill 可独立部署到不同项目结构
- `skill-doc-division`: SKILL.md（AI 指令）与 README.md（人类文档）的职责分工规范——SKILL.md 为完整执行流程的唯一真实来源，README.md 为不重复工作流的可读概览

### Modified Capabilities
- `evaluation-review`: 内容审查维度新增"外部路径自包含性"检查项——SKILL.md 中是否存在对项目级路径（如 `openspec/`、`.codemaker/` 同级目录）的硬编码引用；存在则标记 Warning
- `implementation-execution`: SKILL.md 编写规范新增约束——禁止在 SKILL.md 中硬编码 `openspec/specs/` 等假定项目结构的路径；如需引用 spec 文件，使用哨兵定位或降级声明

## Impact

### 受影响文件
| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `SKILL.md` | 重构 | 精简至 400 行内；外置复杂流程分治速查；Stage 3 检查表改为引用；修正 3 处 openspec/specs/ 硬编码路径 |
| `README.md` | 精简 | 移除三阶段细节和 9 条原则重复内容，保留概览和快速开始 |
| `references/complex-workflow-guide.md` | 扩充 | 末尾追加 SKILL.md 外置的"复杂流程分治设计速查"内容 |
| `references/review-checklist.md` | 可能调整 | 确保 Stage 3 引用时检查清单内容完整、无遗漏 |

### 不兼容变更
- AI 在执行 Stage 3 时需额外读取 `references/review-checklist.md`（之前 SKILL.md 内嵌了检查表副本）——**BREAKING**（增加一次文件读取）
- 部署到无 `openspec/` 结构的项目时，`openspec/specs/` 引用降级为不可用——**BREAKING**（之前直接断裂，现在优雅降级）
