# Skill 类型模板

本文档提供 5 种 skill 类型的完整设计模板，每种类型包含：目录结构推荐、工作流骨架、强制要求、正例和边界说明。

---

## 1. Generator（生成器型）

### 识别特征
输入数据/文件 → 经过处理 → 输出新文件/报告。核心动作是"产出物"。

### 目录结构

```
skill-name/
├── SKILL.md                   # AI 执行指令
├── README.md                  # 人类可读文档
├── scripts/                   # 必须：数据采集和文件生成脚本
│   ├── requirements.txt       # 必须：Python 依赖声明
│   ├── collect_data.py        # 数据采集脚本
│   └── generate_output.py     # 文件生成脚本
├── references/                # 可选：领域知识
└── cases/                     # 可选：案例库（知识密集型推荐）
```

### 工作流骨架

```
Phase A: 数据采集（脚本 collect_data.py）
    ↓ 输出：结构化数据（JSON/YAML/文件）
Phase B: 数据分析（AI 推理）
    ↓ 输出：分析结论（Markdown 草稿）
Phase C: 结果校验（AI 自检）★ 不可省略
    ↓ 输出：复核日志 + 定稿
Phase D: 文件生成（脚本 generate_output.py）
    ↓ 输出：最终文件
```

### 强制要求

1. **数据采集和文件生成必须脚本化**：确定性操作不能用 AI 推理替代
2. **Phase C（结果校验）不可省略**：输出型 skill 必须有前后一致性验证
3. **校验日志必须可见**：不能静默修正，必须输出复核日志
4. **脚本可独立测试**：每个脚本有明确的 CLI 参数，可脱离 AI 运行

### 正例：diffscope

- 数据采集：`scripts/get_diff_and_content.py`（脚本）
- 文件生成：`scripts/generate_report.py`（脚本）
- 结果校验：Step 9.5 Bug/风险自我复核（AI 自检，有复核日志）
- 校验导向："找反证"——搜索该问题已被处理的证据

### 边界说明

- 如果"生成"只是聊天输出而非文件，不属于 Generator——属于普通对话
- 如果数据采集特别简单（如只读一个已知路径的文件），可以降级为内联命令，但必须在 SKILL.md 中说明降级条件

---

## 2. Reviewer（审查器型）

### 识别特征
输入制品 + 规则 → 逐条检查 → 输出审查报告。核心动作是"对照检查"。

### 目录结构

```
skill-name/
├── SKILL.md                   # AI 执行指令
├── README.md                  # 人类可读文档
├── references/                # 必须：检查清单
│   ├── checklist-structure.md # 结构检查清单
│   ├── checklist-content.md   # 内容检查清单
│   └── ...                    # 按维度拆分的检查清单
└── scripts/                   # 可选：自动检查脚本
```

### 工作流骨架

```
Phase A: 读取制品 + 加载检查清单（从 references/）
    ↓
Phase B: 逐维度评估
    - 每项输出 ✅/❌/➖，不能跳过
    - 机械可检查的项目优先用脚本
    ↓
Phase C: 汇总评分 + Top-N 建议
    ↓ 输出：结构化审查报告
```

### 强制要求

1. **检查清单必须外置 `references/`**：不能在 SKILL.md 中内联大量规则
2. **检查项可客观判定**：不是"写得好不好"这种主观题
3. **评分公式可复现**：另一个 AI 跑同一个 skill 应得相似分
4. **N/A 项目显式标记**：不能跳过，必须注明不适用原因

### 正例：skill-checker

- 检查清单拆分为 5 个文件（structure/content/directory/testability/security）
- 评分公式：10 分起点，Error -2，Warning -0.5，底线 1
- 严重度三级：Error/Warning/Info
- N/A 项用 ➖ 显式标记

### 边界说明

- 如果检查清单极短（≤5 项），可以不拆文件，但必须在 SKILL.md 中声明"因清单简短故未外置"
- Reviewer 型 skill 自身也可以有降级——如某个检查清单文件缺失，跳过该维度并标注

---

## 3. Pipeline（流水线型）

### 识别特征
多阶段串行执行，阶段间有数据依赖。核心动作是"有序流转"。

### 目录结构

```
skill-name/
├── SKILL.md                   # AI 执行指令（含完整步骤定义）
├── README.md                  # 人类可读文档
├── scripts/                   # 必须：各阶段的确定性脚本
│   ├── requirements.txt
│   ├── step1_prepare.py
│   ├── step3_process.py
│   └── step5_cleanup.py
└── references/                # 可选：阶段间的数据格式约定
    └── data-schemas.md
```

### 工作流骨架

```
Step 1: 准备 ── ✅/⏭️
    ↓ 输出：step1_output.json
Step 2: 获取 ── ✅/⏭️
    ↓ 输出：step2_output.json
Step 3: 处理 ── ✅/⏭️/❌
    ↓ 输出：step3_output.json
...
Step N: 清理 ── ✅/⏭️
```

### 强制要求

1. **每步有门控标记**：✅ 完成 / ⏭️ 跳过 / ❌ 失败
2. **依赖不可用时必须降级**：不得卡死流程
3. **时间盒约束**：每步声明最大执行时间
4. **阶段间输出格式规约化**：至少有字段约定，理想情况有 JSON schema

### 正例：diffscope

- 12 步串行工作流，每步有 ✅/⏭️ 标记
- 降级处理：local-code-mcp 不可用时 Step 8 跳过
- 时间盒：Step 8.1 分支切换 3 分钟、Step 8.4 单符号搜索 2 分钟
- 阶段间数据持久化到 `~/.diff_cache/`

### 边界说明

- Pipeline 和 Generator 的区别：Pipeline 强调步骤流转，Generator 强调产出物。diffscope 同时是两者
- 如果步骤 ≤3 且步骤间无复杂数据传递，降级为 Generator 或 Reviewer

---

## 4. Tool Wrapper（工具封装型）

### 识别特征
封装外部工具/MCP 的调用，附加参数校验和错误处理。核心动作是"适配外部"。

### 目录结构

```
skill-name/
├── SKILL.md                   # AI 执行指令
├── README.md                  # 人类可读文档
├── scripts/                   # 可选：参数校验/结果解析脚本
│   └── validate_params.py
└── references/                # 可选：外部工具的 API 文档
    └── tool-api.md
```

### 工作流骨架

```
参数校验 → 调用外部工具 → 结果结构化 → 错误处理/降级
```

### 强制要求

1. **工具不可用时的降级行为必须显式定义**
2. **参数 schema 在 SKILL.md 中声明**
3. **外部工具调用集中管理**：一个脚本或一个明确标记的函数，不分散到多处
4. **错误信息必须透传**：不能吞掉外部工具的错误

### 正例

一个封装 git diff 的 skill：
- 参数校验：确认仓库路径存在、分支名合法
- 降级行为：`git` 命令不可用时提示安装，不卡死
- 调用集中：所有 git 命令通过一个 `git_ops.py` 脚本

### 边界说明

- 如果"封装"变成了大量的业务逻辑判断（超过参数校验 + 错误处理的范围），应重新归类为 Generator 或 Pipeline
- Tool Wrapper 通常最轻量，SKILL.md 可能只有几十行

---

## 5. Case-Driven（案例驱动型）

### 识别特征
知识密集型，通过历史案例的模式匹配来增强分析准确性。核心动作是"经验复用"。

### 目录结构

```
skill-name/
├── SKILL.md                   # AI 执行指令
├── README.md                  # 人类可读文档
├── cases/                     # 必须：案例库
│   ├── README.md              # 必须：案例规范和模板
│   ├── CASE-001-xxx.md        # 统一模板的案例文件
│   └── CASE-002-xxx.md
└── scripts/                   # 可选：案例匹配辅助脚本
```

### 工作流骨架

```
当前场景 → 特征提取 → 案例匹配（trigger_patterns） → 激活检查规则 → 执行检查
```

### 案例文件统一模板

```markdown
# CASE-XXX: 简要标题

## 元信息
- 来源、发现方式、严重程度、类别、创建时间

## 触发模式（trigger_patterns）
- 可机械匹配的关键词/正则/结构模式列表
- 支持组合触发（多条件同时命中优先级更高）

## 模式描述
- 问题本质、典型表现、为什么难发现

## 实际案例
- 精简伪代码片段（去项目化）+ 触发场景 + 修复方式

## 检查规则（AI 分析时使用）
- 每条格式："找到 X → 比对 Y → 判断 Z"
- 必须可操作，不能是笼统建议

## 关联知识
- 类似模式、通用修复思路、测试要点
```

### 强制要求

1. **触发模式必须可机械匹配**：基于关键词/正则/代码结构，不能依赖语义理解
2. **检查规则必须可操作**："找到 X → 比对 Y → 判断 Z"，不能是"注意 xxx"
3. **案例去项目化**：去除特定变量名、路径、工单号，保留通用模式
4. **`cases/README.md` 必须存在**：定义案例规范和模板

### 正例：diffscope 案例库

- CASE-001：触发模式 = "diff 中出现 `Cache`/`cache`/`CacheKey`"（可机械匹配）
- CASE-002：触发模式 = "对已有 table 字段的 in-place 赋值"（可机械匹配）
- CASE-003：触发模式 = "条件判断从 `not Cfg.X` 改为其他条件"（可机械匹配）
- 检查规则格式："找到 X → 比对 Y → 判断 Z"

### 边界说明

- Case-Driven 通常叠加在其他类型之上（如 diffscope = Pipeline + Case-Driven）
- 如果案例 ≤2 个，可以暂不独立 cases/ 目录，在 SKILL.md 中内联，但应注明"建议拆分为独立案例文件"
- 案例数量增长后应及时迁移到独立 cases/ 目录

---

## 类型判定流程

```
用户描述 skill 意图
        │
        ▼
┌─ 有输出文件 + 有校验步骤？ ──→ Generator
│  无
├─ 有检查清单 + 有评分公式？ ──→ Reviewer
│  无
├─ 有 ≥5 个串行步骤 + 阶段间数据传递？ ──→ Pipeline
│  无
├─ 主要逻辑是调用外部工具？ ──→ Tool Wrapper
│  无
├─ 有 cases/ 目录 + 触发模式匹配？ ──→ Case-Driven
│  无
└─ 无法确定 → 标记 "待确认"，列出可能类型
```

当一个 skill 同时满足多个类型特征时（如 diffscope = Pipeline + Case-Driven + Generator），标记为 **Hybrid**，并列出各类型的占比。
