# Spec: 落地实现执行 (Implementation Execution)

> 对应 Stage 2：将设计蓝图落地为可运行 skill 的完整实现规范。
> 核心参考：`skill-creator` SKILL.md（捕获意图→调研→撰写→测试→迭代→打包→优化），
> 三层加载模型、Writing Patterns、迭代改进哲学均吸收自 skill-creator。

## ADDED Requirements

### Requirement: 用户需求澄清与意图确认
系统 SHALL 在进入实现阶段前确认用户需求已充分澄清。若对话历史中已包含完整信息，提取整理后请用户确认；若只有模糊意图，主动询问核心问题：skill 要解决什么问题、何时触发、输出什么格式、是否需要测试用例。对于输出可客观验证的 skill（Generator、Pipeline），建议建立测试用例；对于输出主观的 skill（写作风格、设计审美），测试用例通常不需要。

#### Scenario: 从对话历史提取已有需求
- **WHEN** 用户前文已详细描述了 skill 的工作流（如连续多轮讨论了"分析代码变更生成 QA 报告"的流程）
- **THEN** 系统 SHALL 从对话历史提取：skill 目标、详细步骤序列、用户纠正过的点、观察到的输入/输出格式，整理为结构化列表请用户确认，不做重复访谈

#### Scenario: 用户只给出模糊意图
- **WHEN** 用户只说"帮我写一个 skill"但未提供任何具体细节
- **THEN** 系统 SHALL 逐一询问：这个 skill 要解决什么问题？用户一般用什么话触发它？期望输出什么格式的文件或内容？是否需要定量测试来验证效果？

#### Scenario: 从 Stage 1 设计蓝图直接进入
- **WHEN** 用户在 Stage 1 完成后说"继续实现"或"开始写"
- **THEN** 系统 SHALL 以 Stage 1 输出的设计审查报告为输入，跳过需求澄清，直接进入文件编写阶段

### Requirement: 前置调研与信息收集
系统 SHALL 在编写 SKILL.md 前主动了解边界情况、输入/输出格式、示例文件、成功标准、依赖项。可用的 MCP 工具或文档集应通过 subagent 并行调研以提高效率。

#### Scenario: 用户提供示例文件
- **WHEN** 用户说"类似这个文件的格式做输入"
- **THEN** 系统 SHALL 先读取和理解示例文件的结构，再开始编写 SKILL.md，确保流程设计与实际输入格式匹配

#### Scenario: 依赖外部 MCP 工具
- **WHEN** skill 需要调用 MCP 服务（如文档搜索、代码仓库访问）
- **THEN** 系统 SHALL 确认这些服务在当前环境中可用，并在 SKILL.md 中声明依赖（含降级路径）

#### Scenario: 无可用 MCP 工具时降低用户负担
- **WHEN** 没有可用于调研的 MCP 工具，且判断用户可能不了解某些技术细节
- **THEN** 系统 SHALL 带着上下文准备后提问（"根据我对 X 的理解，应该是 Y，对吗？"），而非将开放式问题抛给用户

### Requirement: SKILL.md 编写规范——三层加载模型
系统 SHALL 按 skill-creator 的 Progressive Disclosure 三层加载模型指导 SKILL.md 编写：
1. **元数据层**（name + description，始终在上下文，约 100 字）
2. **正文层**（SKILL.md body，触发时加载，目标 < 500 行）
3. **资源层**（references/、scripts/、assets/，按需加载，无上限）

当正文接近 500 行时，应增加层级——外置到 references/ 并在正文中留下清晰的导航指引。当 skill 支持多个领域/框架时，使用 Domain organization 模式：SKILL.md 保留工作流和选择逻辑，具体领域知识按文件分到 references/（如 `aws.md`、`gcp.md`、`azure.md`），让 AI 只读相关文件。

#### Scenario: SKILL.md 接近 500 行需拆分
- **WHEN** SKILL.md 正文超过 450 行且还有内容要添加
- **THEN** 系统 SHALL 建议：将检查清单/详细模板外置到 `references/`，在正文中保留工作流 + 指向 references 的索引表

#### Scenario: 多领域 skill 的组织
- **WHEN** skill 需要同时支持 AWS、GCP、Azure 三套部署流程
- **THEN** 系统 SHALL 建议 Domain organization 模式：SKILL.md 只保留通用工作流和平台选择逻辑，三套具体流程分别写到 `references/aws.md`、`references/gcp.md`、`references/azure.md`

#### Scenario: 大 reference 文件需要目录
- **WHEN** reference 文件超过 300 行
- **THEN** 系统 SHALL 建议在该文件头部添加目录，方便 AI 快速定位

### Requirement: SKILL.md 编写规范——结构要求
系统 SHALL 确保 SKILL.md 包含：YAML frontmatter（name + description，description 需含触发关键词且 20-200 字）、编号执行流程（含门控标记 + 输入/输出声明）、全局原则/约束（用"因为 X 所以 Y"替代 "MUST Y"）、输出格式/模板（如需特定格式）、降级声明（如有外部依赖）、参考文件索引表。

#### Scenario: description 过于简短
- **WHEN** description 字数 < 20 字（如 "一个 skill"）
- **THEN** 系统 SHALL 标记为 Error，提示"description 需 ≥20 字，说明 skill 做什么并嵌入触发关键词。skill-creator 建议 description 偏'主动'——描述要 pushy，引导 AI 在用户提及相关场景时即使没明确说出 skill 名也触发"

#### Scenario: 约束用 "因为 X 所以 Y" 替代 "MUST Y"
- **WHEN** SKILL.md 出现大量 ALL CAPS 的 MUST/ALWAYS/NEVER
- **THEN** 系统 SHALL 标记为 Warning，建议改为解释原因式表达。skill-creator 的指导原则："今天的 LLM 很聪明，有良好的心理模型——解释为什么重要比刚性约束更有效"

#### Scenario: 输出格式模板
- **WHEN** skill 需要输出特定格式（如审查报告、提交信息、发布说明）
- **THEN** 系统 SHALL 在 SKILL.md 中使用 `## Report structure` 声明模板，并用 `**Example 1:** Input: xxx / Output: xxx` 格式提供正例

### Requirement: 脚本编写与分离规范
系统 SHALL 确保确定性任务脚本化到 `scripts/` 目录。规则：能用 if-else 精确描述的操作放脚本，需要权衡判断的放 AI 提示词。脚本需满足：CLI 入口可独立测试、`requirements.txt` 依赖声明、不在 SKILL.md 中内嵌 > 20 行的代码块。

#### Scenario: 识别需要脚本化的确定性任务
- **WHEN** Stage 1 设计蓝图中标明了数据采集和文件生成步骤
- **THEN** 系统 SHALL 指示创建对应脚本（CLI + argparse + 错误退出码），并在 SKILL.md 流程步骤中引用脚本执行

#### Scenario: 提示词中内嵌代码
- **WHEN** 用户 SKILL.md 草稿包含 > 20 行的 Python 代码块
- **THEN** 系统 SHALL 标记为 Warning，建议将代码抽取到 `scripts/` 并在 SKILL.md 中改为引用。理由（来自 skill-creator）：代码在提示词中无法独立测试，参数变化时需 AI 重写

#### Scenario: 脚本目录缺少依赖声明
- **WHEN** `scripts/` 存在 Python 脚本但无 `requirements.txt`
- **THEN** 系统 SHALL 提醒创建 `requirements.txt`，含所有第三方依赖及版本约束

### Requirement: 案例文件创建规范
系统 SHALL 指导用户为 Case-Driven 或知识密集型 skill 创建案例文件，使用统一模板：元信息 → 触发模式（可机械匹配的关键词列表）→ 模式描述 → 检查规则（"找到 X → 比对 Y → 判断 Z"）→ 关联知识。案例目录必须含 `cases/README.md`。

#### Scenario: 创建第一个案例文件
- **WHEN** Stage 1 已识别 skill 为 Case-Driven 或 Reviewer 型且适合案例积累
- **THEN** 系统 SHALL 输出完整案例模板 + `cases/README.md`，说明案例列表和匹配机制

#### Scenario: 案例触发模式不可机械匹配
- **WHEN** trigger_patterns 为语义描述（如"代码中存在性能问题"）
- **THEN** 系统 SHALL 标记为 Error，要求改为可机械匹配的关键词列表。核心测试："另一个 AI 只靠 grep 能找到吗？"

#### Scenario: 案例检查规则不可操作
- **WHEN** 检查规则为笼统建议（如"注意缓存键的正确性"）
- **THEN** 系统 SHALL 标记为 Error，要求改为 "找到 X → 比对 Y → 判断 Z" 格式

### Requirement: 测试验证——执行体系
系统 SHALL 指导用户按 skill-creator 的测试执行模型建立测试。使用 subagent 并行执行测试和基线（with-skill + without-skill），包含：evals.json 定义 → assertions 起草 → 子任务执行 → timing.json 捕获 → grading → aggregation → viewer 展示。

#### Scenario: 为 Generator 型 skill 建立定量测试
- **WHEN** skill 输出可客观验证（文件内容、数据结构），用户同意建立测试
- **THEN** 系统 SHALL 指导：创建 `evals/evals.json`（2-3 个真实 prompt + expected_output + assertions），说明测试执行模型（with-skill + baseline 并行 subagent，timing.json 捕获 token 和耗时，grader 评估 assertions，aggregate_benchmark 汇总统计量，generate_review.py 启动可视化 viewer）。强调：这需要使用 skill-creator 的 scripts 和 agents 体系

#### Scenario: 为 Reviewer 型 skill 建立定性测试
- **WHEN** skill 输出为主观判断（审查报告、设计反馈）
- **THEN** 系统 SHALL 建议：创建 2-3 个测试 prompt（包含反例——带已知问题的 skill），用人工评审替代定量 assertions

#### Scenario: 测试结果不通过
- **WHEN** assertions 失败或人工评估不满意
- **THEN** 系统 SHALL 进入迭代改进循环：分析根因 → 修改 SKILL.md → 重新运行全部测试（含 baseline）→ 用 `--previous-workspace` 对比迭代变化

### Requirement: 迭代改进循环
系统 SHALL 支持"编写 → 测试 → 评审 → 改进"的迭代循环。改进时遵循 skill-creator 的四条准则：(1) 从反馈中抽象通用模式，避免针对单个测试用例的过拟合修改；(2) 保持 prompt 精瘦——删除不产生实际效果的冗余指令；(3) 解释为什么——用原理性语言替代刚性 MUST；(4) 检测重复劳动——如果所有测试用例中 AI 都独立写了相同脚本，将其固化到 `scripts/` 中。

#### Scenario: 基于测试反馈的通用化改进
- **WHEN** 用户反馈"所有 3 个测试用例生成的报告都缺少摘要部分"
- **THEN** 系统 SHALL 在 SKILL.md 中增加摘要要求（而非修改单个测试用例的 prompt），确保改进对所有用例生效

#### Scenario: 检测重复劳动
- **WHEN** 读取 3 个测试用例的执行记录，发现 AI 在每次执行中都独立创建了类似的 `create_docx.py` 辅助脚本
- **THEN** 系统 SHALL 提示将其固化到 `scripts/` 中，并在 SKILL.md 中引用，后续执行不再重复造轮子

#### Scenario: 多轮迭代后无改进
- **WHEN** 连续 2 轮后测试结果无显著改善
- **THEN** 系统 SHALL 提示可能的设计问题（职责边界过宽、核心流程设计有误），建议回到 Stage 1 重新审视设计

### Requirement: 打包交付
系统 SHALL 在交付前执行最终质量检查：SKILL.md 行数 < 500、frontmatter 完整、无硬编码密钥、目录结构匹配类型模板。通过后提示使用 skill-creator 的 `package_skill.py` 打包。

#### Scenario: 打包前质量检查通过
- **WHEN** 最终检查全部通过
- **THEN** 系统 SHALL 提示运行 `python -m scripts.package_skill <skill-path>`（来自 skill-creator），产出 `.skill` 安装包路径

#### Scenario: 打包前质量检查不通过
- **WHEN** SKILL.md 超 500 行或目录结构与类型模板不符
- **THEN** 系统 SHALL 列出问题项，阻止直接打包，要求修复后重新检查

### Requirement: Description 优化（条件执行）
若用户需提升 skill 触发准确率，系统 SHALL 指导按 skill-creator 的 description optimization 流程：生成 20 条评估查询（8-10 should-trigger + 8-10 should-not-trigger，含近距误触的 tricky 负例）→ 用户审核 → 60/40 训练/测试分集 → `run_loop.py` 5 轮迭代优化 → 应用最佳 description。

#### Scenario: 用户要求优化触发
- **WHEN** 用户说"优化 skill 的触发"或"提高触发准确率"
- **THEN** 系统 SHALL 说明优化流程并等待确认。重点是评估查询的设计：正例要覆盖不同措辞和罕见用法，负例要构造共享关键词但实际不触发的情况（近距误触测试）

#### Scenario: 评估查询设计——构造 tricky 负例
- **WHEN** 生成 should-not-trigger 评估查询
- **THEN** 系统 SHALL 确保约半数为近距误触——共享 skill 关键词但属于不同场景的查询。示例：skill 是"PDF 处理"，负例应为"帮我分析 PDF 中的财务数据趋势"（应是数据分析 skill 的工作，不是 PDF 处理）
