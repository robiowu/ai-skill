---
name: excel-to-markdown
description: '将 Excel 策划表转为 Agent 友好的结构化 Markdown。 触发场景： (1) 用户说"把 Excel 转成 Markdown"或"导出策划表" (2) 用户提供 Excel 文件路径并要求分析策划需求 (3) 用户说"运行 excel-to-markdown"'
metadata:
  version: 1.0.0
---
# Excel to Markdown Skill

## 核心约束⚠️

1. **原始内容零修改**：MUST NOT 增删改原始策划内容
2. **🤖[AI] 标注**：Agent 补充内容 MUST 以 `🤖[AI]` 前缀标注
3. 不做 OCR，文本来自 openpyxl
4. 文本树转 Markdown 表格是格式转换，不算修改
5. 发现疑似错误可用 `🤖[AI]` 提问，MUST NOT 改原值

## 运行模式

| 模式 | 说明 | 流程 |
|------|------|------|
| **完整模式** | 截图 + 读图分析，输出最丰富 | Step 0 → 1 → 2 → 3 |
| **轻量模式** | 仅基于 data.md 格式化，速度快 | Step 0 → 1 → 3（跳过 Step 2） |

轻量模式差异：
- **跳过 Step 2**：不执行精细截图和读图分析
- **Step 3 正常执行**：但 Markdown 中不包含截图引用（`![...](images/...)` 不生成），`📷 *嵌入图片*` 标记仅输出文本占位，不附带 `🤖[AI]` 图片描述

## 并行处理⚠️

Step 2/3 中多 sheet **无依赖关系**，**MUST 并行 subagent 处理**：
- Step 2（仅完整模式）：每 sheet 一个 `explore` subagent（分析 data.md + 按需截图）
- Step 3：每 sheet 一个 `general` subagent（组装 .md）

每个 subagent prompt MUST 包含：该 sheet 的 data.md 路径、参考文档路径（`references/enrichment_guidelines.md`、`references/markdown_format.md`）、输出要求、**当前运行模式（完整/轻量）**。

## 工作流程

### Step 0: 准备

1. 获取 sheet 列表：
   ```bash
   python scripts/excel_range_screenshot.py "<excel_path>" dummy --list-sheets
   ```
2. **AskUserQuestion** 多选 sheet
3. **AskUserQuestion** 获取 ASCII tag（如 `children_day_2026`）
4. **AskUserQuestion** 选择运行模式：
   - **完整模式（推荐）**：包含精细截图 + 读图分析，输出最丰富
   - **轻量模式**：跳过截图，仅基于文本数据格式化，速度更快
5. 输出目录：`{excel所在目录}/{tag}_export/`

### Step 1: 结构化数据提取（不截图）

```bash
python scripts/excel_export.py "<excel_path>" --tag "<tag>" --sheets "sheet名1" "sheet名2"
```

多通道提取（**不截图**）：
- **openpyxl**：文本 + 边界 + 校验值 + 批注 + 条件格式 + 超链接
- **HTML**：COM 导出 → CSS 解析 → 富文本格式（加粗/斜体/删除线/颜色/边框等）

内置增量机制（`.export_manifest.json` 校验值），重复运行自动跳过未变化 sheet。HTML 通道失败自动降级。

> ⚠️ 文件名/目录名 MUST ASCII。数据目录: `sheet_01_data`, `sheet_02_data`, ...。`sheet_mapping.json` 记录映射。

每个 sheet 生成 `sheet_NN_data/data.md`，包含：
- 表格检测（✅高/⚠️中/🟡疑似）+ 高置信区域已转 Markdown 表格
- 富文本 HTML 标签 + 💬批注 + 🎨条件格式 + 🔗超链接
- 非表格区域缩进文本树 + 📷 嵌入图片标记
- 超链接以 `[显示文本](链接目标)` 内联保留，`🔗 超链接` 摘要节列出所有链接

> ✅ 通行条件：每个选中 sheet 都有 data.md

### Step 2: 分析 data.md + 按需截图（仅完整模式）

> ⚠️ **轻量模式跳过此步骤**，直接进入 Step 3。

读 data.md → 分析截图需求 → 按需截图。**只读 data.md 规划截图，不分析截图内容。**

⚠️ subagent MUST 先读取 `references/enrichment_guidelines.md`。

**截图决策信号**：

| 信号 | 截图决策 |
|------|----------|
| `📷 *嵌入图片*` | **MUST 截图** |
| `⚠️ 低置信` / `🟡 疑似` 表格 | **SHOULD 截图** |
| 🎨 dataBar / colorScale / iconSet | **SHOULD 截图** |
| 💬 批注 / 颜色标注 / 高置信表格 / 纯文本 | 不需要截图 |

**区域规划**：间隔 ≤20 行合并 zone → 上下扩 2-3 行 → 每 sheet ≤5 zone → 单 zone >50 行则拆分。

截图工具用法见 `references/enrichment_guidelines.md`。

> ✅ 通行条件：需截图区域已完成，文件在 `images/sheet_NN/`

### Step 3: 读截图 + Markdown 组装

⚠️ subagent MUST 先读取 `references/markdown_format.md`。

**完整模式**：
1. 截图已在 `images/sheet_NN/`
2. **读取每张截图**，按 `references/markdown_format.md` 中的"截图视觉分析"要求进行详尽转录（文字逐字、数值精确、布局结构）
3. 按 `references/markdown_format.md` 组装：原始文本 + `🤖[AI]` 补充（含截图分析结果）+ 表格转换 + 图片引用
4. 清理临时目录

**轻量模式**：
1. 无截图文件，`images/` 目录不创建
2. 按 `references/markdown_format.md` 组装：原始文本 + `🤖[AI]` 补充 + 表格转换
3. `📷 *嵌入图片*` 标记 → 仅输出文本占位行 `📷 *嵌入图片 (行范围/尺寸)*`，**不附带** `![...](images/...)` 引用和 `🤖[AI]` 图片描述
4. `🤖[AI]` 语义分析（颜色/格式等非截图相关）正常输出
5. 清理临时目录

> ✅ 通行条件：每 sheet 有 .md，目录结构正确

## 容错

| 场景 | 处理 |
|------|------|
| HTML 通道失败 | 降级单通道 |
| 截图失败 | Markdown 中注明 |
| Excel 打开失败 | 报错终止 |

## 输出结构

**完整模式**：
```
{tag}_export/
├── sheet_mapping.json
├── sheet_NN_data/
│   ├── data.md                 # Step 1 生成
│   └── sheet_NN_ranges.json    # Step 2 截图区域规划
├── images/sheet_NN/
│   └── detail_N.png            # Step 2 按需截图
└── sheet_NN.md                 # Step 3 最终 Markdown
```

**轻量模式**（无 images 目录和 ranges.json）：
```
{tag}_export/
├── sheet_mapping.json
├── sheet_NN_data/
│   └── data.md                 # Step 1 生成
└── sheet_NN.md                 # Step 3 最终 Markdown
```