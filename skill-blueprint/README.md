# Skill Blueprint — Skill 全生命周期管理

一个覆盖 skill **设计 → 实现 → 评估** 三阶段的元 Skill。提取自 `skill-creator`、`skill-checker`、`diffscope` 等成熟 skill 的设计实践。

## 定位

```
skill-blueprint（本 skill）覆盖全流程:
① 蓝图设计 → 架构是否合理？类型归属？范式对齐？
② 落地实现 → 文件编写、测试迭代、打包发布
③ 整体评估 → 执行层面审查、质量评分、改进建议
```

三阶段可灵活切换——根据用户输入和当前进度智能判断所处阶段，支持评估不通过后回到实现阶段修复。

## 触发方式

在 AI 助手中提及以下关键词时自动激活：
- "设计一个 skill"、"创建 skill"、"skill 架构"
- "skill 最佳实践"、"skill 规范"、"skill 范式"
- "审查 skill 设计"、"skill 设计是否合理"
- "帮我规范化这个 skill"
- "实现 skill"、"编写 skill"、"打包 skill"
- "评估 skill"、"审查 skill 质量"

> 完整执行流程、设计原则及参考文件索引见 [SKILL.md](./SKILL.md)

三阶段覆盖设计→实现→评估全生命周期，9 条核心原则贯穿始终，两阶段 10 分制评分把关。

## 目录结构

```
skill-blueprint/
├── SKILL.md                              # AI 执行指令（全生命周期）
├── README.md                             # 本文档
└── references/                           # 参考资料
    ├── design-patterns.md                # 9 条原则深入解析
    ├── skill-types.md                    # 6 种类型完整模板
    ├── checklist-design.md               # 16 项设计审查检查清单
    ├── anti-patterns.md                  # 8 条常见反模式 + 纠偏
    ├── implementation-guide.md           # 实现阶段详细手册 ★v2 新增
    ├── review-checklist.md               # 评估阶段完整检查清单 ★v2 新增
    └── complex-workflow-guide.md         # 复杂流程分治设计指南 ★v2 新增
```

## 设计溯源

| 源头 | 提取的范式 |
|------|-----------|
| **skill-creator** | 渐进式加载、核心循环（草稿→测试→评审→改进）、可量化评估、描述优化 |
| **skill-checker** | 5 维度检查清单、严重度分级（Error/Warning/Info）、10 分制评分 |
| **diffscope** | 12 步工作流门控、降级处理、案例库驱动、自我复核、时间盒约束 |
| **diffscope 案例库** | 触发模式匹配（可机械匹配）、可操作检查规则（找到 X → 比对 Y → 判断 Z） |
| **上下文膨胀经验** | subagent 拆解 + progress.md 追踪（v2 新增原则 9） |
| **spec 覆盖** | 7 个 spec 覆盖全生命周期：`design-review`（Stage 1 设计审查）、`quality-scoring`（两阶段统一评分）、`knowledge-codification`（知识沉淀）、`template-generation`（模板生成）、`implementation-execution`（Stage 2 实现规范）、`evaluation-review`（Stage 3 评估规范）、`complex-workflow-decomposition`（原则 9 分治规范） |

## 快速开始

1. 在 AI 助手中描述你的 skill 想法 → skill-blueprint 自动激活
2. Stage 1：识别 skill 类型，审查架构设计，输出评分
3. Stage 2：按推荐模板创建文件，编写 SKILL.md，测试迭代
4. Stage 3：执行层面审查，输出评估报告
5. 根据评估结果修复 → 重新评估 → 交付使用
