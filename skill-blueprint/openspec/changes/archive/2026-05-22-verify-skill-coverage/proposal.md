## Why

`skill-blueprint` 经过 v2 迭代后，已从纯设计审查元 Skill 演化为覆盖三阶段（设计→实现→评估）的全生命周期管理工具。然而现有的 4 个 spec（`design-review`、`knowledge-codification`、`quality-scoring`、`template-generation`）全部聚焦 Stage 1 设计层面，Stage 2 落地实现、Stage 3 整体评估以及原则 9 在 spec 层面完全空白。

更关键的问题是：即使是非正式的 references/ 指南文件，与系统内置的 `skill-creator`（486 行）和 `skill-checker`（133 行）逐项对比后，也存在实质性的思想和细节缺失。

### Stage 2 vs skill-creator 逐项差距

| skill-creator 核心节点 | implementation-guide.md 覆盖 | 缺失内容 |
|---|---|---|
| Capture Intent（需求澄清） | ❌ 无 | 从对话历史提取意图、4 个澄清问题、是否需要测试用例判断 |
| Interview and Research（调研） | ❌ 无 | MCP 并行调研、边界情况提问、减轻用户负担 |
| Progressive Disclosure（三层加载） | ❌ 无 | 元数据→正文→资源的三级加载机制、Domain organization 模式 |
| Writing Patterns（示例模式） | ⚠️ 只有约束写法 | Input/Output 示例格式、输出模板声明模式 |
| Test Cases（创建 evals） | ⚠️ 只有结构测试 | evals.json 格式、assertions 机制、定量 vs 定性判断 |
| Running tests（并行跑测） | ❌ 无 | with-skill + baseline 并行 subagent、timing.json 捕获、grader grading、aggregation、viewer |
| Improving（迭代改进） | ⚠️ 只有 3 行 | generalize from feedback、keep prompt lean、explain the why、repeated work 检测 |
| Package（打包） | ⚠️ 无脚本引用 | package_skill.py 具体调用方法 |
| Description Optimization | ❌ 无 | 20 条触发 eval、60/40 分集、run_loop.py 优化循环 |

### Stage 3 vs skill-checker 逐项差距

| skill-checker 核心节点 | review-checklist.md 覆盖 | 缺失内容 |
|---|---|---|
| Collect Input（定位 skill） | ❌ 无 | 按名称搜索 skill 路径、确认步骤 |
| Gotchas（关键陷阱） | ❌ 无 | N/A 不静默、不虚高分数、short skill 特殊处理、机械评分需定性补充 |
| 5/6 维度审查 | ✅ 充分 | — |
| 评分 + 报告 | ✅ 充分 | — |

本次变更不仅补齐 spec 空白，更重要的是将这些缺失的**实现思想和执行细节**充实到对应的 spec 和 references 中。

## What Changes

- 将 `skill-creator` 的 4 个缺失核心节点（需求澄清与调研、渐进式加载、并行测试执行、描述优化）系统性地纳入 Stage 2 的实现指导
- 将 `skill-creator` 的迭代改进哲学（generalize / keep lean / explain why / repeated work detection）充实到 Stage 2 的改进循环中
- 将 `skill-checker` 的定位流程（搜索 skill 路径 + 确认）和 Gotchas（关键陷阱）纳入 Stage 3 评估
- 新增 Stage 2 落地实现的 spec，覆盖 9 个核心场景（含 skill-creator 缺失的 4 个节点）
- 新增 Stage 3 整体评估的 spec，覆盖 6 维度审查及 2 个新流程节点
- 新增原则 9 复杂流程分治的 spec
- 扩展 `quality-scoring` spec 为统一评分体系
- 更新 `design-review` spec 原则计数 8→9
- **BREAKING**: 无

## Capabilities

### New Capabilities
- `implementation-execution`: Stage 2 落地实现的形式化规范。覆盖需求澄清（从意图到确认）→ SKILL.md 编写（含渐进式加载模型）→ 脚本/案例创建 → 测试验证（含 evals.json + assertions + 并行跑测流程）→ 迭代改进（generalize / lean / explain why / repeated work）→ 打包交付 → 描述优化
- `evaluation-review`: Stage 3 整体评估的形式化规范。覆盖 skill 定位与确认 → 6 维度审查 → 评分计算 → Gotchas 规避 → 结构化报告输出
- `complex-workflow-decomposition`: 原则 9 复杂流程分治的形式化规范——subagent 拆解、progress.md 追踪、混合策略、反模式警示

### Modified Capabilities
- `quality-scoring`: 从仅 Stage 1 5 维度扩展为 Stage 1 + Stage 3 统一评分体系，明确两阶段差异
- `design-review`: 原则数量 8→9，补充原则 9 审查场景

## Impact

- 新增 3 个 spec 文件
- 修改 2 个现有 spec
- `implementation-guide.md` 需补充 4 个缺失节点（需求澄清、渐进式加载、并行测试、描述优化）
- `review-checklist.md` 需补充定位流程和 Gotchas 部分
- SKILL.md 原则计数需同步更新
