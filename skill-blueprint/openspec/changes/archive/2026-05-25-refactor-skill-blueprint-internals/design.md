## Context

skill-blueprint 是 skill 全生命周期管理的元 Skill，当前存在三个自指问题：

1. **SKILL.md 超 400 行**（~426 行）：自身违反 Phase 3.3 的行数建议
2. **硬编码 `openspec/specs/` 路径**：3 处引用假定 skill 永远位于特定项目结构内
3. **SKILL.md / README.md 重复**：三阶段描述和 9 条原则在两处维护

变更目标：使 skill-blueprint 自身成为其规范的正面范例（dogfooding 成功），同时可独立部署到无 openspec 结构的项目。

现有 `references/review-checklist.md` 已包含 Stage 3 完整 6 维度检查清单（270 行），无需新建文件，只需确保 SKILL.md 精简后引用正确。

## Goals / Non-Goals

**Goals:**
- SKILL.md 从 ~426 行精简至 400 行内（目标 ~350 行）
- 3 处 `openspec/specs/xxx` 路径改为可降级的定位方式
- README.md 不重复 SKILL.md 中的三阶段详情和原则列表
- skill-blueprint 自身通过 Stage 3 评估，获得 9+ 分

**Non-Goals:**
- 不改变 skill-blueprint 的三阶段核心工作流逻辑
- 不新增 files（所有内容移入已有的 references/ 文件）
- 不改变目录结构
- 不修改 `references/` 下除 `complex-workflow-guide.md` 和 `review-checklist.md` 外的其他文件

## Decisions

### D1: SKILL.md 精简——什么保留、什么外置

**方案**：两层精简

| 内容块 | 当前行数 | 处理 | 理由 |
|--------|:------:|------|------|
| 复杂流程分治设计速查（line 339-397） | ~57 行 | → 移至 `references/complex-workflow-guide.md` 末尾，原位改为一句话引用 | 该指南已有完整版，速查是副本；AI 需要时可通过已有索引读取完整指南 |
| Stage 3 Phase 检查项表格（line 241-305） | ~65 行 | → 改为框架大纲 + 引用 `references/review-checklist.md`；保留 Phase 名称/目标、评分公式、报告模板 | review-checklist.md 已有完整 6 维度检查表；SKILL.md 保留框架便于 AI 理解评估流程全貌 |
| 全局原则表（line 40-53） | ~14 行 | 保留 | 原则是 Stage 1/2/3 的共同根基，精简后不可损失 |
| 三阶段总览表（line 21-28） | ~8 行 | 保留 | 是最高层导航，AI 进入 skill 后第一眼需要看到 |

精简后行数估算：426 - 57 - 50（表格缩减为引用） ≈ 319 行。加上引用锚点文字约 +10 行，最终 ~330 行。

**替代方案考虑**：完全删除 Stage 3 检查表、全部依赖 references——被拒绝，因为 SKILL.md 作为 AI 入口需要看到 Stage 3 的框架（有哪些 Phase、严重度分级、评分公式），否则 AI 不知道"评估"包含什么维度、需要读哪个文件。

### D2: openspec/specs/ 路径——哨兵定位 + 降级

**方案**：基于 `openspec/config.yaml` 哨兵文件的相对定位

SKILL.md 中 3 处硬编码引用的修正：

| 原文 | 修正后 |
|------|--------|
| `openspec/specs/complex-workflow-decomposition/spec.md` | 从 skill 所在项目根目录查找 `openspec/specs/complex-workflow-decomposition/spec.md`；若项目无 openspec/ 目录（skill 被独立部署），此规范不可用，以 `references/complex-workflow-guide.md` 为准 |
| `openspec/specs/implementation-execution/spec.md` | 同上，降级时以 `references/implementation-guide.md` 为准 |
| `openspec/specs/evaluation-review/spec.md` | 同上，降级时以 `references/review-checklist.md` 为准 |

**实现方式**：AI 在解析引用时：
1. 从当前 skill 目录向上查找 `openspec/config.yaml`
2. 找到 → 以此为项目根，拼接 `openspec/specs/<name>/spec.md`
3. 未找到 → 使用 `references/` 中的对应文件作为降级

不引入环境变量或 Python 脚本——skill-blueprint 无 scripts/，所有定位逻辑由 AI 按指令执行。

**替代方案考虑**：
- 环境变量 `SKILL_ROOT`：引入新的配置入口，违反最小依赖原则；且 skill-blueprint 是纯指令型 skill，不应增加环境要求
- 完全删除 openspec 引用、只保留 references：丢失 spec 的 formality 优势——spec 文件是 OpenSpec 工作流的标准制品，其价值和 references 不同
- 相对路径 `../../openspec/specs/`：等同于硬编码深度依赖（proposal 中问题 2），已明确否决

### D3: README.md 分工——不再重复 SKILL.md

**方案**：README.md 只保留"概览层"内容

| 保留 | 移除 |
|------|------|
| 定位（一句话） | 三阶段详情表（→ "详见 SKILL.md Stage 1-3"） |
| 触发方式 | 9 条原则列表（→ "完整原则及解析见 SKILL.md §全局原则"） |
| 目录结构 | Stage 1 审查维度详表 |
| 设计溯源 | Stage 3 评估维度详表 |
| 快速开始 | — |

新增一句导航："> 完整执行流程、阶段切换规则、参考文件索引见 [SKILL.md](./SKILL.md)。"

**理由**：原则 4（过程可量化）和原则 5（评估规则化）强调"单一真实来源"。当原则列表在两处出现时，一处修改另一处遗漏 = 不一致。SKILL.md 是 AI 执行的唯一入口，自然应成为唯一真实来源。

### D4: 降级声明标准化

当前 skill-blueprint 的降级声明存在笼统描述（如"若不可用则跳过"），需统一为 `{依赖} → {降级行为} → {标注}` 格式。需要修正的点：

| 当前位置 | 当前描述 | 修正为 |
|----------|----------|--------|
| SKILL.md Phase 1.3 引用外部文件时 | 隐式"不存在则跳过" | `references/design-patterns.md` → 如该文件不存在，使用 SKILL.md 内嵌的 9 条原则概要（已包含） → ⚠️ 缺少详细正反例 |
| SKILL.md openspec 引用 | 无降级声明 | `openspec/specs/` → 如 openspec/ 目录不存在，降级使用 references/ 对应文件 → ⚠️ 缺失形式化规范 |

## Risks / Trade-offs

| 风险 | 影响 | 缓解 |
|------|------|------|
| AI 执行 Stage 3 时多一次文件读取（review-checklist.md） | 增加约 1 次 tool call 延迟 | SKILL.md 参考文件索引表已列出该文件，AI 通常会在进入 Stage 3 时预读；读取 270 行文件耗时可忽略 |
| 哨兵定位依赖 `openspec/config.yaml` 存在 | 部分旧项目使用 openspec 但无 config.yaml | 降级路径覆盖此场景——找不到哨兵即降级为 references |
| README.md 精简后人类读者可能找不到完整信息 | 新用户不知去哪看原则细节 | README.md 顶部加显式导航指向 SKILL.md 对应章节 |
| SKILL.md 精简后 AI 可能遗漏 Stage 3 检查项 | 评估不完整 | review-checklist.md 是 Stage 3 的唯一权威来源，AI 被明确指示"评估时读取此文件"；SKILL.md 保留框架确保 AI 知道要读什么 |

## Migration Plan

1. **一次性重构**：4 个文件在同一次变更中修改（无分阶段部署）
2. **验证**：修改完成后，用 `skill-checker` 或手动按 Stage 3 评估 skill-blueprint 自身，目标 9+ 分
3. **回滚**：所有变更在 git 中可逆，无数据库迁移或外部依赖

## Open Questions

- ~~`review-checklist.md` 中内容审查（维度 3）的行数阈值是 400 行（line 69），但 `evaluation-review` spec 中定义为 500 行（spec.md line 73）。是否应统一？~~ → 决定：本次变更不动 spec 阈值，留待后续一致性对齐。review-checklist.md 的 400 行是本 skill 的实践建议，spec 的 500 行是规范上限，两者不冲突（建议比规范更严格）。
- SKILL.md 中 Stage 3 保留的框架粒度——是保留 Phase 名称 + 目标（~6 行/Phase × 6 = 36 行），还是更精简？→ 按 D1 方案执行，保留 Phase 名称、目标、评分公式、报告模板，约 35 行；具体检查项全部引用 review-checklist.md。
