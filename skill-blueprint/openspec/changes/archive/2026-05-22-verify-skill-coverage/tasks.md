## 1. 新增 Spec 迁移到主 Specs 目录

- [x] 1.1 复制 `specs/implementation-execution/spec.md` → `openspec/specs/implementation-execution/spec.md`（新建）
- [x] 1.2 复制 `specs/evaluation-review/spec.md` → `openspec/specs/evaluation-review/spec.md`（新建）
- [x] 1.3 复制 `specs/complex-workflow-decomposition/spec.md` → `openspec/specs/complex-workflow-decomposition/spec.md`（新建）

## 2. 修改 Spec Delta 合并到主 Specs

- [x] 2.1 合并 `specs/quality-scoring/spec.md` 的 MODIFIED 内容到 `openspec/specs/quality-scoring/spec.md`——新增 Stage 3 6 维度评分体系，保留 Stage 1 5 维度内容，标题区分两阶段
- [x] 2.2 合并 `specs/design-review/spec.md` 的 MODIFIED 内容到 `openspec/specs/design-review/spec.md`——8 条原则 → 9 条原则，新增原则 9 两个审查场景

## 3. `implementation-guide.md` 补充缺失节点

skill-creator 对照发现的 4 个缺失节点 + 1 个不完整节点，需充实：

- [x] 3.1 在 §一 之前新增"需求澄清与前置调研"章节：从对话历史提取意图 → 4 个核心澄清问题 → 是否需要测试用例的判断 → MCP 并行调研策略（参考 skill-creator L47-60）
- [x] 3.2 在 §一 SKILL.md 编写规范中补充 Progressive Disclosure 三层加载模型（参考 skill-creator L86-108）：元数据→正文→资源、Domain organization 模式、大 reference 加目录
- [x] 3.3 在 §一 SKILL.md 编写规范中补充 Writing Patterns：输出模板声明模式（## Report structure + ALWAYS）、Input/Output 示例格式（参考 skill-creator L119-135）
- [x] 3.4 在 §四 测试验证中补充 skill-creator 的并行测试执行模型：with-skill + baseline 并行 subagent、evals.json + assertions、timing.json 捕获、grading → aggregation → viewer 展示流程（参考 skill-creator L163-289）
- [x] 3.5 在 §四 迭代修正中充实 skill-creator 的四条改进哲学（参考 skill-creator L292-321）：generalize from feedback、keep prompt lean、explain the why、detect repeated work；补充"改进后重新跑全部测试 + --previous-workspace 对比"流程
- [x] 3.6 在 §五 打包交付中引用 skill-creator 的 `package_skill.py` 具体调用方法（参考 skill-creator L408-416）
- [x] 3.7 新增 §六 Description 优化：20 条评估查询设计（8-10 should-trigger + 8-10 should-not-trigger，含 tricky 近距误触）→ 用户审核 → 60/40 分集 → run_loop.py 优化循环（参考 skill-creator L332-404）

## 4. `review-checklist.md` 补充缺失环节

skill-checker 对照发现的 2 个缺失环节：

- [x] 4.1 在文档开头新增"评估前置：Skill 定位"章节：按名称搜索常见 skill 路径 → 读取 SKILL.md + 目录树 → 简短确认信息（参考 skill-checker L22-32）
- [x] 4.2 在文档末尾（§评分规则 之后）新增"关键陷阱（Gotchas）"章节（参考 skill-checker L118-124）：N/A 不静默、不虚高分数、实际验证文件存在、≤30 行极简 skill 的过度工程化处理、机械评分需定性补充

## 5. SKILL.md 同步更新

- [x] 5.1 更新原则总览表：8 条 → 9 条，表头计数和全文引用同步更新
- [x] 5.2 Stage 2 部分添加 spec 引用：`openspec/specs/implementation-execution/spec.md`
- [x] 5.3 Stage 3 部分添加 spec 引用：`openspec/specs/evaluation-review/spec.md`
- [x] 5.4 原则 9 部分添加 spec 引用：`openspec/specs/complex-workflow-decomposition/spec.md`

## 6. README.md 同步

- [x] 6.1 验证原则计数（"9 条核心设计原则"）一致
- [x] 6.2 设计溯源表中补充新 spec 的覆盖说明

## 7. 交叉引用验证

- [x] 7.1 验证 `quality-scoring/spec.md` 中 Stage 1 和 Stage 3 评分公式一致无矛盾
- [x] 7.2 验证 `evaluation-review/spec.md` 6 维度与 `review-checklist.md` 6 维度一一对应
- [x] 7.3 验证 `implementation-execution/spec.md` 的 Requirement 覆盖 skill-creator 核心循环全部 9 个节点：capture → interview → progressive disclosure → write → writing patterns → scripts/cases → test → iterate → package → description optimize
- [x] 7.4 验证 `complex-workflow-decomposition/spec.md` 覆盖 `complex-workflow-guide.md` 策略 A（subagent）和策略 B（progress.md）
- [x] 7.5 验证 `evaluation-review/spec.md` 包含 skill-checker 的 Gotchas 4 项全部（N/A 不静默、不虚高分数、文件存在验证、极简 skill 处理）且补充了第 5 项（定性补充）

## 8. 最终审查

- [ ] 8.1 用 skill-checker 对更新后的 skill-blueprint 执行审查，确认评分不降级
- [ ] 8.2 用 skill-blueprint 自身 Stage 1 反审 SKILL.md，确认自洽性
- [x] 8.3 确认所有 spec 文件 Scenario 格式正确（`#### Scenario:`，WHEN/THEN 大写）
