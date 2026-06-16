# Agent 分析 data.md + 按需截图指南

## 1. 分析流程

对每个 sheet，**仅阅读 data.md**（不读截图）：
1. 语义分析 → 提取 `🤖[AI]` 标注供 Step 3 使用
2. 提取截图需求信号 → 规划截图区域 → 调用截图工具
3. 截图文件输出到 `images/sheet_NN/`，由 Step 3 读取和分析

### 截图决策信号

| 信号 | 决策 |
|------|------|
| `📷 *嵌入图片*` 标记 | **MUST 截图** |
| `⚠️ 中置信` / `🟡 疑似` 表格 | **SHOULD 截图** |
| 🎨 `dataBar` / `colorScale` / `iconSet` | **SHOULD 截图** |
| ✅ 高置信表格 / 💬 批注 / 颜色标注 / 纯文本 | **不截图** |

无任何信号 → 跳过截图，直接进 Step 3。

### 语义分析（`🤖[AI]` 标注）

MUST 逐一分析以下维度：

#### 1.1 颜色语义

- 扫描所有 `<font color>` / `<span style="background-color">` 标签
- **先观察规律再下结论**：同色多处出现时，对比周围文本推断语义
- 能推断 → `🤖[AI] 红色标记表示已废弃的配置`
- 不能推断 → `🤖[AI] {颜色}标记，含义待确认`
- 同色 ≥3 次且语义一致 → Sheet 概览中增加 `🤖[AI] 本表颜色约定：红色=废弃, 黄底=待定`

#### 1.2 嵌入图片

- 记录 📷 数量、行位置、推测图片类型
- 此阶段仅**规划截图**，详尽转录在 Step 3 执行（见 `markdown_format.md` "截图视觉分析"）

#### 1.3 格式语义

- `<del>` → `🤖[AI] 此内容已废弃/已移除`
- 合并单元格 → 判断是模块标题还是分组标记
- 💬 批注 → 原样保留，暗示需求变更/待办时补充标注
- 🎨 条件格式 → 说明业务含义

#### 1.4 超链接

- `[文本](链接)` 和 `🔗 超链接` 摘要节 MUST NOT 忽略
- 外部链接 → 标注类型：`🤖[AI] 指向 Figma 交互稿 / PM 需求单 / KM 文档`
- 内部引用 `#Sheet!Cell` → 标注跨表关系

#### 1.5 策划意图信号

| 信号 | 常见表现 | 标注 |
|------|----------|------|
| 待定 | "待定"/"TBD"/"暂定"/"待确认" | `🤖[AI] ⏳ 待定内容，需与策划确认` |
| 废弃 | 删除线/"废弃"/"旧版"/灰底 | `🤖[AI] 🗑️ 已废弃，无需实现` |
| 新增 | "新增"/"V2"/"改为"/"调整" | `🤖[AI] ✨ 新增/变更内容` |
| 约束 | "必须"/"不能"/"上限"/"最多" | `🤖[AI] ⚠️ 关键约束` |
| 引用 | "详见XX表"/"参考XX" | `🤖[AI] 🔗 引用其他表/模块` |

策划文档无统一用词规范，结合上下文灵活判断，**宁可多标注不遗漏**。

#### 1.6 模块边界

- 空行段落、合并标题行、编号模式（"一、"/"1."）→ 识别功能模块分界
- 每个独立模块 SHOULD 成为 Step 3 的一个 H2
- 无额外信息时不补充

---

## 2. 截图区域规划

- 间隔 ≤20 行 → 合并为一个 zone
- 每 zone 上下扩 2-3 行上下文
- 每 sheet ≤5 zone；单 zone >50 行则拆分

---

## 3. 截图工具

截图输出到 `images/sheet_NN/`，`ranges.json` 保存到 `sheet_NN_data/`。

**单次**：
```bash
python scripts/excel_range_screenshot.py "<excel_path>" "<sheet_name>" <start_row> <end_row> "<output_dir>/images/sheet_NN/" --filename "detail_N.png"
```

**批量（推荐）**：
```bash
# ranges.json 格式: [{"start_row": 82, "end_row": 98, "filename": "detail_1.png"}, ...]
python scripts/excel_range_screenshot.py "<excel_path>" "<sheet_name>" --batch "<output_dir>/sheet_NN_data/sheet_NN_ranges.json" --output-dir "<output_dir>/images/sheet_NN/"
```