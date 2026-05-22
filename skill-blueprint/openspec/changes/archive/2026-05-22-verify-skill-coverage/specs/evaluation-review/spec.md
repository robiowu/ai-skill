# Spec: 整体评估审查 (Evaluation Review)

> 对应 Stage 3：对已实现的 skill 进行执行层面全面审查，输出评估报告。
> 核心参考：`skill-checker` SKILL.md（定位→审查→汇总→评分→Gotchas），
> 吸收其 Collect Input 流程和 Gotchas 陷阱规避机制。
>
> 与 skill-checker 的关系：skill-blueprint Stage 3 是生命周期内**自评**（侧重设计完备性和降级健壮性），
> skill-checker 是**他评**（侧重格式合规性和可测试性）。两者在结构/目录/内容/安全维度共享审查思路但检查项存在差异。
> 当前基于 skill-checker v1.0.0。

## ADDED Requirements

### Requirement: Skill 定位与确认
系统 SHALL 在执行评估前定位目标 skill：如用户提供 skill 名称而非路径，搜索常见 skill 位置（用户级 `.codemaker/skills/`、项目级、相对路径 `skills/`）；如未找到，请用户提供完整路径。定位后读取 SKILL.md 和完整目录树，简要确认（skill 名称、行数、目录结构），等待用户确认无误后再开始审查。

#### Scenario: 用户提供 skill 名称
- **WHEN** 用户说"审查一下 my-skill"
- **THEN** 系统 SHALL 依次搜索：`~/.codemaker/skills/my-skill/SKILL.md` → `skills/my-skill/SKILL.md`（当前目录）→ 如均未找到则请用户提供绝对路径

#### Scenario: Skill 定位后的确认
- **WHEN** 定位到 `my-skill/SKILL.md`，读取内容
- **THEN** 系统 SHALL 输出简短确认信息："目标 skill: `my-skill`，320 行，含 `references/` 和 `scripts/` 目录。开始审查。"等待用户确认（除非用户说"直接审"）

#### Scenario: SKILL.md 不存在
- **WHEN** 指定路径下找不到 SKILL.md
- **THEN** 系统 SHALL 报告错误并终止——不存在的东西无法评估

### Requirement: 6 维度评估审查
系统 SHALL 按 6 个维度对已实现的 skill 进行执行层面审查：结构审查（6 项）、目录审查（4 项）、内容审查（4 项）、安全审查（3 项）、完备性审查（4 项）、复杂流程分治评估（4 项，条件适用）。每项输出 Pass（✅）/ Fail（❌）/ N/A（➖）。

#### Scenario: 完整审查执行
- **WHEN** 用户确认后开始评估
- **THEN** 系统 SHALL 逐一读取 SKILL.md、目录结构、references/、scripts/、cases/，按 6 维度逐项审查并输出表格

#### Scenario: 纯对话型 skill 的目录审查
- **WHEN** skill 仅含 SKILL.md 和 README.md，无 scripts/、cases/、references/
- **THEN** 目录审查中涉及 scripts/ 和 cases/ 的项 SHALL 标记为 N/A（➖），备注"simple skill — no bundled resources"

#### Scenario: 审查中断——引用文件不存在
- **WHEN** SKILL.md 引用了 `references/checklist.md` 但实际文件不存在
- **THEN** 系统 SHALL 在目录审查中标记为 Fail（❌），严重度 Error，提示"死引用"

### Requirement: 结构审查
系统 SHALL 检查 skill 基础结构完整性：SKILL.md 存在且非空、frontmatter 完整（name + description）、description 有效（非占位符、含触发关键词、20-200 字）、有编号执行流程、有参考文件索引。

#### Scenario: 缺少 name 字段
- **WHEN** SKILL.md frontmatter 缺少 `name:`
- **THEN** 系统 SHALL 标记为 Error（-2 分）
#### Scenario: description 为占位符
- **WHEN** description 值为 "待补充"、"TODO" 或空字符串
- **THEN** 系统 SHALL 标记为 Warning（-0.5 分），提示需具体描述
#### Scenario: 无执行流程
- **WHEN** SKILL.md 没有编号 Phase/Step 划分
- **THEN** 系统 SHALL 标记为 Warning（-0.5 分）

### Requirement: 目录审查
系统 SHALL 检查目录结构是否匹配类型模板（见 `skill-types.md`）、references/ 死文件、scripts/ 依赖声明、README.md 存在。

#### Scenario: 目录结构与类型不匹配
- **WHEN** skill 声明为 Generator 型但缺少 `scripts/`
- **THEN** 系统 SHALL 标记为 Warning（-0.5 分）
#### Scenario: references/ 死文件
- **WHEN** references/ 有 .md 文件但 SKILL.md 未引用
- **THEN** 系统 SHALL 标记为 Info（🔵），文件可能永不加载
#### Scenario: 无 README.md
- **WHEN** 目录中无 README.md
- **THEN** 系统 SHALL 标记为 Info（🔵）

### Requirement: 内容审查
系统 SHALL 检查 SKILL.md 内容质量：行数 < 500、无内嵌大段代码（> 20 行）、降级声明具体（非"跳过"）、步骤输入/输出声明。

#### Scenario: SKILL.md 超 500 行
- **WHEN** SKILL.md ≥ 500 行
- **THEN** 系统 SHALL 标记为 Warning（-0.5 分），提示外置到 references/
#### Scenario: 降级声明笼统
- **WHEN** 降级描述为"如果不可用则跳过"未说明具体行为
- **THEN** 系统 SHALL 标记为 Error（-2 分），要求 `{依赖} → {降级行为} → {标注}` 格式
#### Scenario: 步骤无输入/输出声明
- **WHEN** 编号步骤未声明输入数据和输出格式
- **THEN** 系统 SHALL 标记为 Warning（-0.5 分）

### Requirement: 安全审查
系统 SHALL 扫描所有文件中的硬编码密钥、任意命令执行（`eval`/`exec`/`os.system(user_input)`）、破坏性操作（`rm -rf`/`DROP TABLE`/`force push`）的前置确认。硬编码密钥判断标准：grep 命中具体值（如 `sk-xxx`）为 Error，命中占位符（如 `YOUR_API_KEY`）为 Pass。

#### Scenario: 检测到硬编码 API Key
- **WHEN** grep `token` `password` `secret` `api_key` `-----BEGIN` 命中具体值
- **THEN** 系统 SHALL 标记为 Error（-2 分），提示改用环境变量
#### Scenario: 脚本中存在危险执行
- **WHEN** scripts/ 含 `eval(user_input)` 或 `os.system(user_input)` 未校验输入
- **THEN** 系统 SHALL 标记为 Error（-2 分）
#### Scenario: 无安全问题
- **WHEN** 安全扫描全部 Pass
- **THEN** 安全维度 SHALL 全部标记 ✅

### Requirement: 完备性审查
系统 SHALL 检查降级健壮性和类型特定要求：每外部依赖有 fallback、Generator 型有自校验、Reviewer 型评分公式可复现、Case-Driven 有 `cases/README.md`。

#### Scenario: 外部依赖无降级路径
- **WHEN** skill 依赖 MCP 服务但未声明 fallback
- **THEN** 系统 SHALL 标记为 Error（-2 分）
#### Scenario: Generator 型缺少自校验
- **WHEN** Generator 型输出步骤后无独立复核步骤
- **THEN** 系统 SHALL 标记为 Error（-2 分）
#### Scenario: Reviewer 型评分公式不可复现
- **WHEN** Reviewer 型评分依赖 AI 主观判断无量化公式
- **THEN** 系统 SHALL 标记为 Warning（-0.5 分）

### Requirement: 复杂流程分治评估（条件适用）
仅当 skill 启用 subagent/progress.md 时执行。检查：subagent 拆解合理性、progress.md 完整性、依赖清晰性、恢复流程定义。

#### Scenario: 不适用——skill 未分治
- **WHEN** skill 不涉及 ≥5 串行步骤或大量中间数据
- **THEN** 本维度 4 项全部 N/A（➖），不计入总评分
#### Scenario: subagent 探索区域重叠
- **WHEN** 两个并行 subagent 作用域存在重叠目录
- **THEN** 系统 SHALL 标记为 Warning（-0.5 分）
#### Scenario: progress.md 模板不完整
- **WHEN** progress.md 缺少执行清单或中间结果摘要
- **THEN** 系统 SHALL 标记为 Warning（-0.5 分）

### Requirement: 评估评分计算
系统 SHALL 按统一评分公式计算总分：起始 10 分，每 Error -2，每 Warning -0.5，Info 不扣分，N/A 不计分母，底线 1 分，±1 定性调整。分数段：🟢 8-10 / 🟡 5-7 / 🔴 1-4。定性调整必须给出理由——"设计特别精妙"需阐述具体创新点，"整体混乱"需指出系统性缺陷。

#### Scenario: 评分计算示例
- **WHEN** 1 Error + 3 Warning
- **THEN** 机械评分 10 - 2 - 1.5 = 6.5，🟡
#### Scenario: 定性调整需有理由
- **WHEN** 机械评分 9 分，评估者认为应 +1
- **THEN** 必须在总评中写明定性调整的具体理由（如"skill 的三层加载模型设计和 Domain organization 实现特别精妙，skill-creator 级水准"）
#### Scenario: 无 SKILL.md
- **WHEN** 根本找不到 SKILL.md
- **THEN** 直接评分 1 分，不执行后续维度

### Requirement: 关键陷阱规避（Gotchas）
系统 SHALL 在评估过程中规避以下常见陷阱：(1) N/A 项必须在表格中显式标记为 ➖，不能静默跳过；(2) 严格遵循扣分公式，不可虚高或虚低；(3) 验证文件存在性时调用工具实际检查，不可凭猜测；(4) 对 ≤30 行的极简 skill，涉及拆分/外置的检查项应标记为 N/A（过度工程化比简单更糟）；(5) 机械评分后必须附加定性说明——0 Error 但思路混乱的 skill 不应得到 10 分。

#### Scenario: 极简 skill 被过度审查
- **WHEN** skill 仅 25 行，是一个简单的参数转发 Tool Wrapper，不涉及渐进式加载或案例积累
- **THEN** 涉及"代码是否外置"、"是否有索引表"等拆分相关检查项应标记为 N/A（➖），备注"极简 skill——过度工程化没有必要"
#### Scenario: 机械评分需定性补充
- **WHEN** 机械评分 10 分（0 Error + 0 Warning），但 skill 核心流程设计存在根本性缺陷（如 AI 和脚本的职责边界完全倒置），只是恰好未被检查项覆盖
- **THEN** 评比分母为 10 但定性调整 -0（不扣分——Gotchas 不改变分数，只在总评中说明"虽然机械评分 10 分，但核心流程设计有隐患：<具体问题>"）
#### Scenario: N/A 不静默
- **WHEN** 检查项为 N/A
- **THEN** 必须在表格中该行显式标记 ➖ 并附简短备注（如"无外部依赖"、"纯对话型 skill 不涉及脚本"），不能直接省略该行
