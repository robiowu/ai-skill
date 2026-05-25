## 1. SKILL.md 精简至 400 行内

- [x] 1.1 将"复杂流程分治设计速查"（~57 行，约 line 339-397）整段从 SKILL.md 切除，追加至 `references/complex-workflow-guide.md` 末尾，原位改为一句话引用：`> 完整设计速查见 references/complex-workflow-guide.md §设计速查`
- [x] 1.2 将 Stage 3 Phase 3.1-3.6 检查项表格（~65 行，约 line 241-305）替换为框架大纲：保留 Phase 名称、目标、评分公式、报告模板（~35 行），具体检查项改为 `> 完整检查清单见 references/review-checklist.md`
- [x] 1.3 确认精简后 SKILL.md 总行数 < 400（目标 ~330 行），统计输出具体行数 → **332 行**
- [x] 1.4 逐一核对 `references/review-checklist.md` 覆盖 Stage 3 全部 6 维度（结构/目录/内容/安全/完备性/复杂流程分治）的所有检查项，如有遗漏则补充 → **全覆盖，无遗漏**

## 2. 消除 openspec/specs/ 硬编码路径

- [x] 2.1 修正 SKILL.md 中 `openspec/specs/complex-workflow-decomposition/spec.md` 引用（当前 ~line 53）：改为哨兵定位 + 降级 `→ 若 openspec/ 不存在，以 references/complex-workflow-guide.md 为准 → ⚠️ 缺失形式化规范`
- [x] 2.2 修正 SKILL.md 中 `openspec/specs/implementation-execution/spec.md` 引用（当前 ~line 131）：改为哨兵定位 + 降级 `→ 若 openspec/ 不存在，以 references/implementation-guide.md 为准 → ⚠️ 缺失形式化规范`
- [x] 2.3 修正 SKILL.md 中 `openspec/specs/evaluation-review/spec.md` 引用（当前 ~line 236）：改为哨兵定位 + 降级 `→ 若 openspec/ 不存在，以 references/review-checklist.md 为准 → ⚠️ 缺失形式化规范`
- [x] 2.4 为每处提及其他的外部依赖（如有 MCP 工具引用）统一补充降级声明，格式严格 `{依赖} → {降级行为} → {标注}` → **无其他外部运行时依赖，task/MCP 均为概念引用**

## 3. README.md 去重分工

- [x] 3.1 从 README.md 移除三阶段详情表及其描述（保留一句概述 + 指向 SKILL.md）
- [x] 3.2 从 README.md 移除 9 条原则列表（保留一句概述 + 指向 SKILL.md §全局原则）
- [x] 3.3 从 README.md 移除 Stage 1 审查维度详表和 Stage 3 评估维度详表
- [x] 3.4 在 README.md 顶部或快速开始之后添加显式导航：`> 完整执行流程、设计原则及参考文件索引见 [SKILL.md](./SKILL.md)`
- [x] 3.5 确认 README.md 保留内容完整：定位、触发方式、目录结构、设计溯源、快速开始

## 4. 降级声明标准化

- [x] 4.1 扫描 SKILL.md 中所有当前降级声明（如"若不可用则跳过"），统一改写为 `{依赖} → {降级行为} → {标注}` 格式 → **三处 openspec/specs/ 降级声明已标准化，无遗留非标准格式**
- [x] 4.2 确认所有外部依赖（references 外部文件、MCP 工具、openspec/specs/）均有明确降级声明，不存在"不可用时静默跳过" → **全部外部依赖均有降级声明**

## 5. references/ 文件调整

- [x] 5.1 将 task 1.1 切出的"复杂流程分治设计速查"内容追加到 `references/complex-workflow-guide.md` 末尾，添加 `## 设计速查` 章节标题
- [x] 5.2 验证 `references/review-checklist.md` 内容与 task 1.4 的核对结果一致——Stage 3 全部检查项覆盖无遗漏 → **6维度全覆盖**

## 6. 自检验证

- [x] 6.1 按 Stage 3 流程对修改后的 skill-blueprint 自身执行 6 维度评估审查 → **全部通过，0 Error 0 Warning**
- [x] 6.2 确认机械评分 ≥ 9 分（0 Error，≤ 2 Warning），定性调整后总评 ≥ 9 分 → **机械分 10/10，总评 10/10 🟢**
- [x] 6.3 对未通过的检查项逐条修复，重新评估至全部通过 → **无未通过项**
- [x] 6.4 验证 skill-blueprint 在新项目（无 openspec/ 目录的空目录）中降级可运行：所有外部引用均触发降级路径，无断裂 → **三处 openspec/specs/ 引用均降级至 references/，无断裂**
