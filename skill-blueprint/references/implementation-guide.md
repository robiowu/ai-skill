# Skill 实现指南

> Stage 2 实现阶段的详细操作手册。覆盖 SKILL.md 编写、脚本规范、测试方法和打包流程。

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

### 1.6 参考文件索引

SKILL.md 末尾必须有索引表：

```markdown
## 参考文件索引

| 文件 | 内容 | 何时读取 |
|------|------|----------|
| `references/xxx.md` | 简短说明 | 在 Phase X 执行时 |
| `scripts/xxx.py` | 简短说明 | 用法: `python xxx.py --input ...` |
```

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

### 4.4 迭代修正

发现问题后按优先级：
1. Error（阻塞性）→ 立即修复
2. Warning（偏离性）→ 评估后修复
3. Info（优化性）→ 记录后按需修复

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
3. 输出最终目录树
4. 提示用户进入 Stage 3 整体评估或直接使用

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
