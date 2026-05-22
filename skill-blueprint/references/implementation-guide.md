# Skill 实现指南

> Stage 2 实现阶段的详细操作手册。覆盖 SKILL.md 编写、脚本规范、测试方法和打包流程。

---

## 零、需求澄清与前置调研

> 参考：skill-creator L47-60

在进入 SKILL.md 编写之前，必须完成需求澄清。跳过此步骤直接开始写是 skill 实现失败的常见原因。

### 0.1 从对话历史提取意图

当用户在前文已详细描述 skill 需求时（如连续多轮讨论），系统应从对话历史提取：

| 应提取的信息 | 提取方法 |
|---|---|
| Skill 目标 | 用户最初提出的问题或需求 |
| 详细步骤序列 | 对话中描述的流程和用户纠正过的点 |
| 输入/输出格式 | 用户提供的示例或描述 |
| 约束条件 | 用户强调的"必须"、"不要"、"注意" |

提取后整理为结构化列表，请用户确认，**不做重复访谈**。

### 0.2 四个核心澄清问题

当用户只给出模糊意图（如"帮我写一个 skill"），按优先级逐一询问：

1. **Skill 要解决什么问题？** —— 明确目标和适用范围
2. **一般用什么话触发它？** —— 影响 description 的触发关键词设计
3. **期望输出什么格式？** —— 文件/报告/代码/命令？结构是什么？
4. **是否需要测试用例？** —— 输出可客观验证（Generator、Pipeline）→ 建议建立测试；输出主观（写作风格、设计审美）→ 测试通常不需要

### 0.3 MCP 并行调研策略

在编写 SKILL.md 前，可使用 MCP 工具或文档集通过 subagent 并行调研：

- 如果 skill 需要调用 MCP 服务 → 确认这些服务在当前环境可用
- 如果有示例文件 → 先读取和理解示例文件的结构
- 如果没有可用 MCP 工具，且判断用户可能不了解某些技术细节 → 带上下文准备后提问（"根据我对 X 的理解，应该是 Y，对吗？"），而非将开放式问题抛给用户

---

## 一、SKILL.md 编写规范

### 1.1 Frontmatter

```yaml
---
name: skill-name              # 必须：短横线分隔的小写名称
description: 简短描述...       # 必须：含触发关键词，20-200 字
---
```

**description 编写要点**：
- 说明 skill 做什么（不是教用户做什么）
- 嵌入触发关键词（如"设计 skill""审查 skill"）
- 长度 20-200 字，太短触发不准，太长截断

**好的 description**：
```yaml
description: Skill 全生命周期管理元 Skill。覆盖蓝图设计、落地实现、整体评估的完整流程。当用户提及设计 skill、创建 skill、skill 架构时触发。
```

**坏的 description**：
```yaml
description: 一个 skill
```

### 1.2 正文结构

推荐结构（按顺序）：

```
1. 角色定位（一句话 + 分工边界）
2. 执行流程（编号 Phase/Step）
3. 全局原则/约束
4. 输出格式/模板
5. 降级声明（如有外部依赖）
6. 参考文件索引（表格）
```

每部分之间用 `---` 分隔。

### 1.3 执行流程写法

**好的写法**：
```markdown
### Phase 1: 环境检查

1. 检查 git 仓库是否存在 → `git status`
2. 检查是否在分支上 → `git branch --show-current`
3. 标记结果：
   - ✅ 所有检查通过 → 进入 Phase 2
   - ⏭️ 非 git 仓库 → 降级为文件分析模式
   - ❌ 无权限 → 报告并终止

**输入**: 工作目录路径
**输出**: 环境状态 (git / 非git / 无权限)
```

**坏的写法**：
```markdown
首先检查一下环境，看看 git 能不能用，然后决定下一步怎么做。
```

**要点**：
- 每步编号 + 门控标记（✅/⏭️/❌）
- 声明输入/输出
- 说明分支逻辑（成功 → 下一步，失败 → 降级/终止）

### 1.4 约束写法

用"因为 X，所以 Y"替代"MUST Y"：

**好的**：
```markdown
因为 AI 在长上下文中容易遗忘早期指令，所以每步执行前回顾全局原则。
```

**坏的**：
```markdown
你 **必须** 在每一步前回顾全局原则！你 **绝对不能** 忘记原则！
```

### 1.5 长度控制

- SKILL.md 目标 < 400 行
- 单段落不超过 20 行
- 代码块不超过 30 行（长代码放 scripts/）
- 表格不超过 10 行 × 5 列

**超标的处理**：
- 检查清单 → 移到 `references/checklist-xxx.md`
- 长模板 → 移到 `references/template-xxx.md`
- 领域知识 → 移到 `references/knowledge-xxx.md`
- 案例 → 移到 `cases/CASE-xxx.md`

### 1.6 Progressive Disclosure 三层加载模型

> 参考：skill-creator L86-108

skill-creator 的架构核心：SKILL.md 不应是一个自包含的巨无霸文档，而应按三层加载模型组织内容，确保 AI 在不同阶段只加载需要的内容。

**三层结构**：

| 层级 | 内容 | 何时加载 | 约束 |
|------|------|----------|------|
| **元数据层** | name + description | 始终在上下文 | 约 100 字，含触发关键词 |
| **正文层** | SKILL.md body | skill 触发时加载 | 目标 < 500 行，保留核心工作流 + 选择逻辑 |
| **资源层** | references/、scripts/、assets/ | 按需加载（AI 决定读取哪些文件） | 无上限，具体领域知识、检查清单、模板放这里 |

**为什么重要**：当前的 LLM 上下文窗口虽然很大（128K+），但实际有效注意力仍然有限。skill-creator 的三层加载确保了：
- 高优先级信息始终在上下文（元数据层）
- 核心工作流入门快（正文层 < 500 行）
- 细节不占用注意力除非需要（资源层按需加载）

**Domain Organization 模式**：

当 skill 需要支持多个领域/框架时，使用 Domain organization 模式：

```
skill-name/
├── SKILL.md                  # 通用工作流 + 平台选择逻辑
└── references/
    ├── aws.md                # AWS 具体流程
    ├── gcp.md                # GCP 具体流程
    └── azure.md              # Azure 具体流程
```

SKILL.md 保留通用步骤，具体平台知识按文件分到 references/，让 AI 只读取相关文件，避免加载所有平台的实现细节。

**大 reference 文件加目录**：reference 文件超过 300 行时，应在文件头部添加目录（TOC），方便 AI 快速定位。

### 1.7 参考文件索引 参考文件索引

SKILL.md 末尾必须有索引表：

```markdown
## 参考文件索引

| 文件 | 内容 | 何时读取 |
|------|------|----------|
| `references/xxx.md` | 简短说明 | 在 Phase X 执行时 |
| `scripts/xxx.py` | 简短说明 | 用法: `python xxx.py --input ...` |
```

### 1.8 Writing Patterns

> 参考：skill-creator L119-135

**输出模板声明模式**：当 skill 需要输出特定格式时，使用 `## Report structure` + `ALWAYS` 声明模板：

```markdown
## Report structure

审查完成后 **ALWAYS** 按以下模板输出报告：

### 基本信息
- **Skill 名称**: xxx
- **类型**: Generator / Reviewer / ...

### 类型识别与匹配度
| 类型 | 匹配度 | 依据 |
|------|:------:|------|
| xxx | 🟢 高 | ... |

### 维度评估表
| 维度 | 检查项 | 结果 | 说明 |
|------|--------|:----:|------|
| 结构合规性 | 步骤分离 | ✅ | ... |
```

**Input/Output 示例格式**：在 SKILL.md 中提供正例和反例，帮助 AI 理解期望行为：

```markdown
**Example 1:**
Input: 帮我设计一个代码审查 skill，要能检查安全和性能问题
Output: [期望的输出格式和内容]

**Example 2:**
Input: 写一个 skill
Output: [此时应触发澄清问题，而非直接输出设计]
```

**要点**：
- 模板声明放在 SKILL.md 末尾而非开头——AI 在触发时先读取工作流，处理完毕后再查模板
- 至少提供 2 个示例（1 个简单 + 1 个复杂）
- 示例要真实——用项目内实际会出现的输入

---

## 二、脚本编写规范

### 2.1 什么时候需要脚本

| 任务类型 | 需要脚本 | 理由 |
|----------|:------:|------|
| 读取文件、目录遍历 | ✅ | 确定性操作，脚本更快更可靠 |
| JSON/YAML/CSV 解析 | ✅ | 格式化解析容易出错 |
| HTTP API 调用 | ✅ | 需要处理超时、重试、错误码 |
| 文件格式转换 | ✅ | 确定性转换 |
| 代码分析、推理 | ❌ | 需要理解上下文 |
| 模式匹配、分类 | ❌ | 脚本规则僵化，AI 更灵活 |
| 最终判断、决策 | ❌ | 需要权衡多因素 |

### 2.2 脚本模板（Python）

```python
#!/usr/bin/env python3
"""
{脚本用途的一句话描述}

用法:
    python {script_name}.py --input <path> --output <path> [--option]

选项:
    --input     输入文件或目录路径（必须）
    --output    输出文件路径（必须）
    --option    可选参数说明
    --help      显示此帮助信息
"""

import argparse
import sys
import json

def main():
    parser = argparse.ArgumentParser(description="{脚本用途}")
    parser.add_argument("--input", required=True, help="输入路径")
    parser.add_argument("--output", required=True, help="输出路径")
    args = parser.parse_args()

    try:
        # 核心逻辑
        result = process(args.input)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ 输出已写入 {args.output}")
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)

def process(input_path):
    # 实现逻辑
    pass

if __name__ == "__main__":
    main()
```

### 2.3 脚本要求

1. **有 CLI 参数入口**：`python script.py --help` 能显示用法
2. **可独立运行**：不依赖 AI 的上下文变量
3. **错误退出码**：失败时 `sys.exit(1)`，成功时 `sys.exit(0)`
4. **中文/英文输出一致**：错误消息用英文（方便 grep），成功消息可中英混合
5. **依赖声明**：`scripts/requirements.txt`

### 2.4 requirements.txt 示例

```
# {skill-name} 脚本依赖
requests>=2.28.0
pyyaml>=6.0
# 如果需要 jinja2 模板渲染:
# jinja2>=3.1.0
```

---

## 三、案例文件编写规范

### 3.1 什么时候需要案例

- 知识密集型 skill（如代码审查、安全扫描）
- 经验需要跨执行复用
- 有 ≥3 个已知的、结构化的检查模式

### 3.2 案例文件模板

```markdown
# CASE-XXX: 简要标题（模式名称）

## 元信息
- **来源**: 从哪个项目/工单提取
- **发现方式**: 如何发现这个问题
- **严重程度**: Critical / High / Medium / Low
- **类别**: 安全 / 性能 / 逻辑 / 规范
- **创建时间**: YYYY-MM-DD

## 触发模式（trigger_patterns）
<!-- 关键字列表，任一命中即激活 -->
- `关键字1`
- `关键字2`
- 正则: `pattern_\w+`

## 模式描述
<!-- 问题本质、为什么难发现 -->

## 实际案例
<!-- 精简伪代码，去项目化 -->

## 检查规则（AI 执行）
<!-- 格式: "找到 X → 比对 Y → 判断 Z" -->
1. 找到 {搜索目标} → 比对 {对比维度} → 判断 {判断标准}

## 关联知识
- 类似模式: CASE-YYY
- 通用修复思路: ...
```

### 3.3 cases/README.md 模板

```markdown
# 案例库说明

## 案例规范

每个案例文件遵循统一模板（见 CASE-001）。

## 案例列表

| 编号 | 名称 | 类型 | 严重度 |
|------|------|------|:------:|
| CASE-001 | xxx | 安全 | High |
| CASE-002 | xxx | 性能 | Medium |

## 匹配机制

执行时扫描当前场景 → 按 trigger_patterns 匹配 → 激活匹配的案例 → 执行检查规则。

匹配是"任一命中"逻辑——只要当前场景中出现任一 trigger_pattern 中的关键字，该案例即被激活。

## 新增案例流程

1. 发现一个新的、可复现的检查模式
2. 按模板创建 CASE-XXX.md
3. 更新本文档的案例列表
4. 在后续执行中验证触发模式是否准确
```

---

## 四、测试验证

### 4.1 结构测试

对已创建的 skill 目录执行：

```
skill-name/
├── SKILL.md              ✅ 存在、非空、有 frontmatter
├── README.md             ✅ 存在
├── references/           ✅ 目录存在（如有引用）
│   └── *.md              ✅ 文件存在
├── scripts/              ⬜ 可选
│   ├── requirements.txt  ✅ 如有脚本则必须
│   └── *.py              ✅ 每个脚本 python --help 正常
└── cases/                ⬜ 可选
    ├── README.md         ✅ 如有则必须
    └── CASE-*.md         ✅ 格式符合模板
```

### 4.2 引用完整性测试

检查 SKILL.md 中所有引用的文件是否真实存在：
- `references/xxx.md` → 文件存在
- `scripts/xxx.py` → 文件存在且可 import
- `cases/CASE-xxx.md` → 文件存在

### 4.3 流程模拟测试

按 SKILL.md 的步骤顺序走一遍：
- 无"跳转到不存在步骤"
- 无"无限循环"路径
- 每个 ❌ 分支有明确的终止或降级行为

### 4.4 并行测试执行模型

> 参考：skill-creator L163-289

skill-creator 使用 subagent 并行执行模型来定量测试 skill 效果。其核心思想是：同时运行两个 subagent——一个加载 skill（with-skill），一个不加载（baseline）——对比输出差异，量化 skill 的实际增益。

**测试架构**：

```
evals.json (定义测试用例)
    │
    ├── subagent (with-skill)    ─┐
    │   └── timing.json            │
    │                              ├── grader (评估 assertions)
    ├── subagent (baseline)      ─┘
    │   └── timing.json
    │
    └── aggregate_benchmark (汇总统计量)
            │
            └── generate_review.py (启动可视化 viewer)
```

**evals.json 格式**：

```json
[
  {
    "prompt": "真实场景的用户输入，如'帮我写一个代码审查 skill'",
    "expected_output": "期望输出特征或关键内容描述",
    "assertions": [
      {"type": "contains", "value": "维度评估表"},
      {"type": "not_contains", "value": "TODO"},
      {"type": "length_gt", "value": 200}
    ]
  }
]
```

需要 2-3 个真实 prompt，覆盖典型使用场景和边界情况。

**assertions 类型**：
- `contains`：输出必须包含指定文本
- `not_contains`：输出不得包含指定文本（如占位符、硬编码密钥）
- `length_gt` / `length_lt`：输出长度约束
- `file_exists`：指定文件必须产出
- `regex`：输出匹配正则表达式

**timing.json 捕获**：每次子任务执行记录 token 消耗和耗时，用于对比 with-skill 和 baseline 的效率差异。

**grading → aggregation → viewer 流程**：
1. grader 评估每个 assertion 的通过/失败
2. aggregate_benchmark 汇总所有测试用例的统计量（通过率、平均 token 差、平均耗时差）
3. generate_review.py 启动本地可视化 viewer，展示对比结果

**适用场景**：
- Generator 型 skill：输出可客观验证（文件内容、数据结构）→ 使用定量 assertions
- Reviewer 型 skill：输出为主观判断 → 创建 2-3 个测试 prompt（包含反例），用人工评审替代定量 assertions

> **注意**：这需要使用 skill-creator 的 scripts 和 agents 体系（如 `agents/grader.md`、`scripts/aggregate_benchmark.py`）。skill-blueprint 提供指导和规范，skill-creator 提供执行工具链。

### 4.5 迭代修正

> 参考：skill-creator L292-321

发现问题后按严重度处理：
1. Error（阻塞性）→ 立即修复
2. Warning（偏离性）→ 评估后修复
3. Info（优化性）→ 记录后按需修复

**skill-creator 的四条改进哲学**：

#### （一）Generalize from feedback —— 从反馈中抽象通用模式

基于测试反馈修改 SKILL.md 时，修改应是**通用性**的，而非针对单个测试用例的过拟合。

**反例**（❌ 针对单个测试用例做特判）：
```
如果输入是"帮我写一个代码审查 skill"，则额外输出类型识别表。
```

**正例**（✅ 抽象为通用规则）：
```
所有设计审查输出必须包含类型识别表——无论用户输入的措辞如何。
```

**判断标准**：修改后问自己——"这个修改对下一个新的、完全不同的测试用例也适用吗？"

#### （二）Keep prompt lean —— 保持 prompt 精瘦

删除不产生实际效果的冗余指令。每增加一行 prompt 都要问：

- 这行指令真的改变了 AI 的行为吗？
- 还是只是重申了 AI 本来就会做的事情？
- 如果没有这行，输出会明显不同吗？

如果答案都是"否"，删除这行。

**常见冗余**：
- "请仔细分析"（AI 本来就会分析）
- "确保输出格式正确"（没有指定什么是正确）
- 重复声明已经在前文写过的约束

#### （三）Explain the why —— 解释为什么

用原理性语言替代刚性 MUST：

```
好的：因为 AI 在长上下文末尾容易遗忘早期指令，所以每步执行前回顾全局原则。
坏的：你 **MUST** 在每一步前回顾全局原则！
```

今天的 LLM 有良好的心理模型——解释**为什么重要**比刚性约束更有效。

#### （四）Detect repeated work —— 检测重复劳动

观察测试执行记录，发现重复模式：

- 如果所有测试用例中 AI 都独立写了相同的辅助脚本 → 固化到 `scripts/` 中
- 如果所有测试用例中 AI 都重复查询相同的文档 → 外置到 `references/` 中
- 如果某个固定格式被反复生成 → 创建模板

**核心原则**：AI 做了两次的事情，第三次应该自动化。

---

**改进后验证流程**：

每次改进后，重新运行**全部**测试用例（含 baseline），使用 `--previous-workspace` 对比迭代前后的变化：

1. 修改 SKILL.md
2. 重新跑全部测试（with-skill + baseline 并行 subagent）
3. 用 `--previous-workspace` 对比：哪些 assertion 从 ❌ 变 ✅、token 消耗增减、输出质量变化
4. 如果连续 2 轮无显著改善 → 可能的设计问题（职责边界过宽、核心流程设计有误），建议回到 Stage 1 重新审视设计

---

## 五、打包与交付

### 5.1 最终检查清单

- [ ] SKILL.md 行数 < 400
- [ ] 所有引用文件存在
- [ ] 脚本可独立运行
- [ ] 无硬编码密钥/token
- [ ] README.md 包含基本使用说明

### 5.2 交付步骤

1. 确认目录结构完整
2. 运行最终的结构测试和流程模拟
3. 使用 skill-creator 的打包工具产出安装包：

```
python -m scripts.package_skill <skill-path>
```

> 参考：skill-creator L408-416。此命令验证 skill 结构完整性，产出 `.skill` 安装包路径。

4. 输出最终目录树
5. 提示用户进入 Stage 3 整体评估或直接使用

### 5.3 目录树输出示例

```
skill-name/
├── SKILL.md                              # AI 执行指令 (320 行)
├── README.md                             # 人类可读文档
├── references/
│   ├── checklist-main.md                 # 主检查清单
│   └── knowledge-base.md                 # 领域知识
├── scripts/
│   ├── requirements.txt                  # Python 依赖
│   ├── collect_data.py                   # 数据采集
│   └── generate_report.py                # 报告生成
└── cases/
    ├── README.md                         # 案例规范
    ├── CASE-001-cache-key.md             # 缓存键模式
    └── CASE-002-type-discriminator.md    # 类型判别模式
```

---

## 六、Description 优化

> 参考：skill-creator L332-404

Description 是 skill 的"触发开关"。过长会被截断，过短缺乏区分度。按以下流程系统优化 description 的触发准确率。

### 6.1 评估查询设计

生成 20 条评估查询，分为两组：

**Should-trigger（8-10 条）**：应该触发 skill 的用户输入

- 覆盖不同措辞（正式/口语/中英混合）
- 覆盖罕见用法（简写、拼写错误、不完整句子）
- 覆盖不同场景（用户直接说"用 xxx skill"、用户描述需求但未提及 skill 名）

**Should-not-trigger（8-10 条）**：不应该触发 skill 的用户输入

- 其中约 50% 为**近距误触（tricky 负例）**：共享 skill 关键词但属于不同场景
- 示例：skill 是"PDF 处理"，负例为"帮我分析 PDF 中的财务数据趋势"（应是数据分析 skill 的工作）

### 6.2 用户审核与分集

1. 展示 20 条评估查询给用户
2. 用户审核：添加遗漏的查询、删除不合理的查询、修正分类错误
3. 确认后按 60/40 分为训练集（12 条）和测试集（8 条）

### 6.3 run_loop.py 优化循环

```
python scripts/run_loop.py \
  --eval-file evals/trigger_evals.json \
  --skill-path <skill-path> \
  --max-iterations 5
```

每轮迭代：
1. 修改 description
2. 用训练集评估触发准确率
3. 记录最佳 description 及得分
4. 5 轮后输出最优 description

### 6.4 应用最佳 Description

1. 用测试集验证最优 description 的泛化效果
2. 确认无劣化后更新 SKILL.md 的 description 字段
3. 如测试集准确率 < 80% → 可能需要重新设计评估查询或调整触发关键词

### 6.5 何时执行

- 用户明确要求"优化触发"或"提高触发准确率"
- 新 skill 交付前（可选，建议重要 skill 执行）
- Skill 收到"不触发/误触发"的反馈时
