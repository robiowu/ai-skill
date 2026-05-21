## 1. 目录结构搭建

- [x] 1.1 创建 `skill-blueprint/` 顶级目录
- [x] 1.2 创建 `references/` 子目录（存放设计模式、类型模板、检查清单、反模式）
- [x] 1.3 确认 skill-blueprint 自身不含 `scripts/`、`cases/`、`assets/`（纯审查指导型）

## 2. 核心指令撰写（SKILL.md）

- [x] 2.1 编写 YAML frontmatter（name: `skill-blueprint`，description 含触发词和分工说明）
- [x] 2.2 编写 Phase 1（类型识别）：5 种类型的识别特征和判决逻辑
- [x] 2.3 编写 Phase 2（范式审查）：8 条原则的应用指引和偏离判定
- [x] 2.4 编写 Phase 3（设计评分）：5 维度评分表 + 10 分制公式 + 严重度分级
- [x] 2.5 编写 Phase 4（改进建议）：Top-N 排序规则 + 引导进入 skill-creator 的交接语
- [x] 2.6 控制 SKILL.md 行数在 300 行以内（160 行），详细内容指向 `references/`

## 3. 参考资料撰写（references/）

- [x] 3.1 编写 `references/skill-types.md`：5 种类型的完整模板（含正例和边界说明）
- [x] 3.2 编写 `references/design-patterns.md`：8 条原则的深入解析（每条含：原理、正例、反例、来源追溯）
- [x] 3.3 编写 `references/checklist-design.md`：设计审查可操作检查清单（16 项，逐项含判断标准）
- [x] 3.4 编写 `references/anti-patterns.md`：常见设计反模式（含触发条件 + 纠偏指引 + 案例引用）

## 4. 文档与自校验

- [x] 4.1 编写 `README.md`（人类可读，含与 skill-creator/skill-checker 的关系说明）
- [x] 4.2 用本 skill 自身的设计原则反审 SKILL.md：通过，4 项适用原则全部满足，4 项 N/A（Reviewer 型天然不涉及）
- [x] 4.3 用 skill-checker 对 skill-blueprint 进行执行层面审查：通过，YAML 完整、渐进式加载、目录规范、无安全问题

## 5. 验证与收尾

- [x] 5.1 端到端测试：用 skill-blueprint 审查 diffscope 的设计，评分 10/10，审查准确
- [x] 5.2 端到端测试：用 skill-blueprint 审查反例 skill，检出 9 Error + 3 Warning，评分 1/10，无漏报
- [x] 5.3 归档变更：执行 `openspec archive` 完成变更归档
