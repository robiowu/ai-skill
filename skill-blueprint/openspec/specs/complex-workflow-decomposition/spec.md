# Spec: 复杂流程分治 (Complex Workflow Decomposition)

> 对应原则 9：当被设计 skill 涉及大批量操作、强流程依赖、且不适合纯脚本固化时，
> 使用 subagent 拆解 + 本地 md 追踪进度的分治策略。
> 本 spec 同时服务于 Stage 1 设计审查（审查时判断是否需要分治）和 Stage 2 实现执行（实现时指导拆解）。

## ADDED Requirements

### Requirement: 分治必要性判断
系统 SHALL 在 Stage 1 设计审查阶段，根据被设计 skill 的特征判断是否需要启用复杂流程分治策略。触发条件：串行步骤 ≥ 5、单次执行需分析 ≥ 5 个文件且每个需深度分析、或中间数据量超出单次上下文承载能力（预估 > 4000 行）。

#### Scenario: 满足分治条件——多模块并行分析
- **WHEN** 被设计 skill 需要同时分析 5 个独立模块的代码变更，每个模块需深度追踪符号定义和使用方
- **THEN** 系统 SHALL 在 Stage 1 审查报告中标注"建议启用原则 9 复杂流程分治"，并推荐使用 subagent 并行拆解策略

#### Scenario: 不满足分治条件——简单流程
- **WHEN** 被设计 skill 只有 3 个串行步骤且每个步骤输出量在 500 行以内
- **THEN** 系统 SHALL 在 Stage 1 审查报告中标注"原则 9: N/A——该 skill 步骤数量少且中间数据量小，无需分治"

#### Scenario: 边界情况——步骤多但每步轻量
- **WHEN** 被设计 skill 有 8 个步骤但每步只做简单判断（如检查文件是否存在、读取配置）
- **THEN** 系统 SHALL 标注"原则 9: N/A——步骤虽多但每步轻量，上下文承载无压力"

### Requirement: Subagent 拆解策略
当启用分治策略时，系统 SHALL 指导将长流程拆解为"主线（轻量）+ 子线（重量）"架构：主线负责读取摘要 → 做决策 → 推进下一步，子线通过 subagent 执行重量级分析任务，只返回结构化摘要给主线。

#### Scenario: 并行子任务拆解
- **WHEN** 多个分析任务彼此独立、无数据依赖
- **THEN** 系统 SHALL 指导创建并行 subagent，每个 subagent 的 prompt 模板包含：目标、作用域（目录/文件范围）、深度（quick/deep）、已知信息、输出格式约束

#### Scenario: 串行子任务拆解
- **WHEN** 分析任务 B 依赖任务 A 的结果
- **THEN** 系统 SHALL 明确标注依赖关系："Step A 完成后，主线读取 A 的结果摘要，作为 Step B 的 known_info 输入，再启动 subagent B"

#### Scenario: 混合策略——部分并行 + 部分串行
- **WHEN** 任务 A 和 B 可并行，任务 C 依赖 A 和 B 的共同结果
- **THEN** 系统 SHALL 指导：先并行启动 subagent A + B → 主线读取 A 和 B 的结果摘要 → 检查一致性 → 启动 subagent C（输入 A 和 B 的摘要）

### Requirement: Subagent 契约规范
系统 SHALL 确保每个 subagent 的 prompt 包含明确的契约要素：独立输入/输出声明、无重叠探索区域、结果验证标准、最大执行时间（时间盒）。

#### Scenario: 缺少输出格式约束
- **WHEN** 用户描述的 subagent prompt 只说"分析模块 X"但未指定输出格式
- **THEN** 系统 SHALL 补充输出格式约束（如"输出：3-5 行变更摘要 + 编号 Bug 列表 + 风险提示 + 无需关注项"）

#### Scenario: 探索区域重叠
- **WHEN** subagent A 的作用域为 `src/auth/` 且 subagent B 的作用域为 `src/`（包含 auth）
- **THEN** 系统 SHALL 标记为 Error（设计缺陷），要求缩小 subagent B 的作用域以排除 auth 子目录

### Requirement: Progress.md 追踪机制
当启用分治策略时，系统 SHALL 要求在 skill 目录下创建 `progress.md`（或同类追踪文件）作为 SKILL.md 执行流程的补充，包含：执行清单（checklist）+ 进度标记（✅/🔄/⏳/❌）+ 关键决策记录 + 中间结果摘要。

#### Scenario: 创建 progress.md 模板
- **WHEN** 设计阶段确定启用分治策略
- **THEN** 系统 SHALL 输出 `progress.md` 模板骨架：执行清单（所有子任务列表）+ 进度标记占位符 + 决策记录区 + 中间结果摘要区

#### Scenario: 从 progress.md 恢复执行
- **WHEN** 子任务 C 执行超时或失败，需要恢复
- **THEN** 系统 SHALL 从 `progress.md` 读取已完成步骤的摘要，跳过已完成步骤，从失败点继续

#### Scenario: progress.md 模板不完整
- **WHEN** progress.md 只有执行清单但无决策记录区
- **THEN** 系统 SHALL 标记为 Warning（偏离最佳实践），提示"缺少决策记录区会导致恢复时不知道之前的判断依据"

### Requirement: 主线恢复流程
当启用分治策略时，系统 SHALL 确保 SKILL.md 中定义了从 progress.md 恢复主线的完整流程：读取 progress.md → 识别最后完成步骤 → 验证已完成步骤的摘要一致性 → 从下一未完成步骤继续。

#### Scenario: SKILL.md 中缺少恢复流程
- **WHEN** skill 使用了 subagent 拆解但 SKILL.md 中未定义"中断后如何从 progress.md 恢复"的流程
- **THEN** 系统 SHALL 标记为 Warning（偏离最佳实践），提示"缺少恢复流程会导致用户中断后无法继续"

#### Scenario: 恢复时发现摘要不一致
- **WHEN** 恢复执行时，progress.md 中记录的子任务摘要与当前文件系统状态不符（如文件已被修改）
- **THEN** 系统 SHALL 提示"摘要可能已过期，是否需要重新执行已完成步骤？"，由用户决定

### Requirement: 分治反模式检测
系统 SHALL 在设计审查（Stage 1）和评估审查（Stage 3）中检测复杂流程分治的常见反模式：子任务过细（每个子任务只做 1 个文件读写→subagent 开销大于收益）、虚假并行（声明为并行但子任务间有隐式数据依赖）、摘要丢失（子任务输出未经结构化摘要直接全量回传主线）。

#### Scenario: 检测子任务过细
- **WHEN** subagent 的任务描述为"读取 config.yaml 并返回内容"
- **THEN** 系统 SHALL 标记为 Info（🔵 优化建议），提示"读文件是主线可以直接完成的轻量操作，不需要启动 subagent"

#### Scenario: 检测虚假并行
- **WHEN** subagent A 声明为并行但其 prompt 中引用了"从 subagent B 的输出中获取 X"（隐式依赖）
- **THEN** 系统 SHALL 标记为 Error（设计缺陷），提示"并行子任务不能有数据依赖，需要串行化"

#### Scenario: 检测摘要丢失
- **WHEN** subagent 的输出格式声明为"返回完整分析内容"（10+ 页文本），无结构化摘要要求
- **THEN** 系统 SHALL 标记为 Warning（-0.5 分），提示"全量回传会淹没主线上下文，子任务应只返回结构化摘要"
