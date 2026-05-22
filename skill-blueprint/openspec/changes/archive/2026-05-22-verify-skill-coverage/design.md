## Context

`skill-blueprint` 覆盖 skill 全生命周期三阶段：蓝图设计（Stage 1）→ 落地实现（Stage 2）→ 整体评估（Stage 3）。当前 4 个 spec 全部聚焦 Stage 1。Stage 2、Stage 3 以及 v2 新增原则 9（复杂流程分治）在 spec 层面空白，但 references/ 中已有详尽指南。

本次设计的关键输入：
- **skill-creator**（`C:\Users\wuweibin01\.codemaker\skills\skill-creator\SKILL.md`）：486 行，覆盖 capture intent → interview → write SKILL.md → test → iterate → package → description optimization 完整流程。使用 subagent parallel execution + assertions + benchmarking + viewer 机制。
- **skill-checker**（`C:\Users\wuweibin01\.codemaker\skills\skill-checker\SKILL.md`）：133 行，5 维度审查流程（结构/内容/目录/可测试性/安全），引用 5 个外部检查清单文件（实际文件不存在，逻辑内联在 SKILL.md 中），同样使用 10 分制评分。
- **skill-blueprint 自身**：`implementation-guide.md`（347 行）对应 Stage 2，`review-checklist.md`（218 行）对应 Stage 3，`complex-workflow-guide.md`（259 行）对应原则 9。

核心矛盾：skill-blueprint 宣称"三阶段全生命周期管理"，但正式 spec 只覆盖了 Stage 1，其余两阶段只是非正式的 references 指南。

## Goals / Non-Goals

**Goals:**
- 补齐 Stage 2 `implementation-execution` spec：将 `implementation-guide.md` 中的操作指南转化为可测试的场景规格，同时参考 skill-creator 的真实工作流（capture intent → draft → test → iterate → package）确保不遗漏
- 补齐 Stage 3 `evaluation-review` spec：将 `review-checklist.md` 的 6 维度 25 项检查清单转化为形式化 spec，同时对比 skill-checker 的 5 维度体系确保不重复、不冲突
- 补齐原则 9 `complex-workflow-decomposition` spec：将 `complex-workflow-guide.md` 中的 subagent 拆解 + progress.md 机制转化为正式 spec
- 修正 `quality-scoring` spec：使其同时覆盖 Stage 1 设计评分（5 维度）和 Stage 3 评估评分（6 维度），明确两者的公式差异、共享机制和边界
- 修正 `design-review` spec：将原则数量从 8 条更新为 9 条，补充原则 9 的审查场景

**Non-Goals:**
- 不修改 skill-blueprint 的 SKILL.md 主体内容（在 spec 写入后可能需要同步原则计数，但不在本次范围内）
- 不创建新的 references 文件——所有内容已在 references/ 中充分存在
- 不定义 skill-blueprint 自身的测试用例或 evals——这属于 Stage 2 实现阶段的产出
- 不修改 skill-creator 或 skill-checker 的任何内容——只参考它们的设计来确保 spec 完整性

## Decisions

### Decision 1: Spec 粒度——按阶段能力拆分，而非按 references 文件一对一映射

**选择**：新增 3 个 spec，每个对应一个能力缺口（`implementation-execution`、`evaluation-review`、`complex-workflow-decomposition`），而非按 references 文件拆出 5+ 个 spec。

**理由**：
- Stage 2 的 `implementation-guide.md` 覆盖 SKILL.md 编写、脚本规范、案例创建、测试验证、打包 5 个子专题——拆成 5 个 spec 过于碎片化，与现有 4 个 Stage 1 spec 的粒度严重不一致
- 每个 spec 对应一个"用户故事"级别的能力——用户角度 Stage 2 就是"我要把设计蓝图落地为可运行的 skill"，这是一个完整能力
- skill-creator 和 skill-checker 都是单一 SKILL.md 覆盖全部职责，skill-blueprint 已经比它们有更细粒度的 spec 拆分

**备选方案**：按 references 文件一对一映射出 5+ spec → 被否决，因为会导致 10+ spec 文件的过细粒度，维护成本高。

### Decision 2: 评分体系统一——扩展 `quality-scoring` 而非新建 stage3-scoring

**选择**：扩展现有 `quality-scoring` spec，增加 Stage 3 评估评分的场景，而非为 Stage 3 单独创建评分 spec。

**理由**：
- Stage 1 和 Stage 3 使用完全相同的评分公式（起始 10 分，Error -2，Warning -0.5，底线 1 分）
- 两者差异仅在分子分母（Stage 1 是 5 维度 16 项，Stage 3 是 6 维度 25 项），但公式逻辑完全一致
- 分开维护会导致公式同步不一致的风险

**备选方案**：新建 `evaluation-scoring` spec → 被否决，因为会导致两套评分 spec 中公式定义重复，一旦修改评分公式需要同步两处。

### Decision 3: 吸收 skill-creator 的渐进式加载模型到 SKILL.md 编写规范

**选择**：将 skill-creator 的 Progressive Disclosure（SKILL.md L86-108）——三层加载（元数据→正文→资源）——作为 Stage 2 SKILL.md 编写规范的核心约束之一，而非可选建议。

**理由**：
- 这是 skill-creator 中最具架构意义的设计思想——它直接决定了 SKILL.md 的粒度、长度和资源组织方式
- skill-blueprint 当前的 `implementation-guide.md` §1.5 只讨论了长度控制（<400 行），但没有解释为什么要控制长度的根本原因——三层加载模型
- Domain organization 模式（按 aws/gcp/azure 分 reference 文件）是降低 SKILL.md 复杂度的重要手段，当前完全缺失

**备选方案**：不吸收，保持长度控制的简单建议 → 被否决，因为缺少三层加载模型会导致用户不理解"为什么要拆分"，只知其然不知其所以然。

### Decision 4: 吸收 skill-checker 的 Gotchas 机制

**选择**：在 `evaluation-review` spec 和 `review-checklist.md` 中增加"关键陷阱（Gotchas）"部分，明确列出常见评估误判场景及规避方式。

**理由**：
- skill-checker 的 Gotchas（L118-124）列出了 4 个最常见的评估陷阱——N/A 不静默、不虚高分数、实际验证文件存在、short skill 特殊处理
- skill-blueprint 当前的 `review-checklist.md` 没有这个部分——这导致评估者可能在执行时重复踩坑
- 其中"short skill 特殊处理"（≤30 行的极简 skill 不应被审查过度工程化）在 skill-blueprint 中完全缺失

**备选方案**：不吸收，依赖评估者的经验和判断 → 被否决，因为这会导致同一 skill 被不同评估者得出不一致的评估结果。

### Decision 5: 与 skill-checker 的边界——审查维度不重复但可互补

**选择**：skill-blueprint 的 Stage 3 审查覆盖 6 个维度（结构/目录/内容/安全/完备性/复杂流程分治），与 skill-checker 的 5 个维度（结构/内容/目录/可测试性/安全）存在部分重叠但不重复。

**理由**：
- 两个 skill 的定位不同：skill-blueprint Stage 3 是"这个 skill 自身是否健全"，skill-checker 是"外部审查者视角是否符合规范"。前者是自评，后者是他评。
- 具体差异：
  - skill-checker 有 `可测试性` 维度（检查是否有 evals、assertions），skill-blueprint 没有这个维度——因为测试是 skill-creator 的职责
  - skill-blueprint 有 `完备性` 维度（检查降级路径、自校验机制），这是设计层面的完备性，skill-checker 不审设计只审执行
  - skill-blueprint 有 `复杂流程分治` 维度（条件），这是 v2 新增，skill-checker 没有
  - 两者共享 `结构/目录/内容/安全` 4 个维度，但检查项不同——示例：skill-checker 的结构审查检查 YAML frontmatter 格式，skill-blueprint 的结构审查检查步骤分离和门控标记
- **关键**：spec 中需明确声明这两个 skill 的关系和边界，避免用户困惑

### Decision 4: Stage 2 spec 的覆盖率——以 skill-creator 的核心循环为参考基准

**选择**：`implementation-execution` spec 覆盖 skill-creator 全程的核心节点：需求澄清 → SKILL.md 撰写 → scripts/ references/ cases/ 创建 → 测试验证（含 evals）→ 迭代改进 → 打包交付 → description 优化。每个节点抽取 2-4 个关键场景。

**理由**：
- 不覆盖 skill-creator 的全部细节（如 benchmark aggregation、viewer launch、blind comparison），那些属于 skill-creator 自身的实现细节，不属于 skill-blueprint 的指导范围
- skill-blueprint Stage 2 的角色是"按蓝图指导实现"，不是"替代 skill-creator"。spec 应覆盖：用户应该做什么、产出物标准是什么、质量门控是什么
- 参考 skill-creator 的核心循环（draft → test → review → improve → repeat），但将其从"AI 如何执行测试"转换为"skill 设计者应该确保哪些测试步骤"

**备选方案**：完整覆盖 skill-creator 的 486 行全部流程 → 被否决，会导致 spec 过重且与 skill-creator 的 SKILL.md 大面积重复。

### Decision 5: 原则 9 spec 的定位——作为设计审查和实现执行的双重使用方

**选择**：`complex-workflow-decomposition` spec 同时服务于 Stage 1 设计审查（审查时判断是否需要分治）和 Stage 2 实现执行（实现时指导 subagent 拆解和 progress.md 创建）。

**理由**：
- 原则 9 的"复杂流程分治"本质上是一个**跨阶段**的能力——设计阶段要判断"这个 skill 是否需要分治"，实现阶段要执行"如何做 subagent 拆解和创建 progress.md"
- 这使它区别于其他 spec：`design-review` 只在 Stage 1 使用，`implementation-execution` 只在 Stage 2 使用，但 `complex-workflow-decomposition` 在两阶段都使用
- spec 需要包含两种场景：(a) 设计审查时评估分治必要性 (b) 实现时指导拆解的具体规范

## Risks / Trade-offs

- **[风险]** 新增 3 个 spec + 修改 2 个 spec 后，spec 总数从 4 变成 7。维护成本增加——spec 之间的交叉引用（如 `quality-scoring` 被 `design-review` 和 `evaluation-review` 都依赖）可能过时。
  - **缓解**：在每个 spec 的依赖声明中显式列出它所依赖的其他 spec，形成明确引用链。

- **[风险]** Stage 3 `evaluation-review` 的 spec 与 skill-checker SKILL.md 存在维度重叠，如果 skill-checker 未来更新其检查维度（如新增第 6 维度），skill-blueprint 的 spec 可能变得不一致。
  - **缓解**：在 spec 的文档注释中声明"当前基于 skill-checker v1.0.0”，并标注"如 skill-checker 维度变更，需人工审查"。不建立硬性同步依赖。

- **[取舍]** `implementation-execution` spec 不覆盖 skill-creator 的 assertion drafting、benchmark aggregation、viewer 等高级功能。这意味着 skill-blueprint 对"如何定量测试 skill"的指导是不完整的——用户需要去 skill-creator 获取这部分。
  - **理由**：这是有意为之。skill-blueprint 提供设计蓝图和实现规范，skill-creator 提供测试工具链。两者的边界在 proposal 中已经明确。

- **[取舍]** 不新增 `testability` spec。skill-checker 有的可测试性维度，skill-blueprint 目前没有——因为测试工具链在 skill-creator 中。如果未来需要，可以作为独立 spec 补充。
  - **理由**：避免与 skill-creator 的职责重叠。但需在 `evaluation-review` spec 的 N/A 场景中明确说明。
