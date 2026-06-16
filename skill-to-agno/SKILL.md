---
name: skill-to-agno
description: 将 codemaker skill 转换为独立 agno Agent 项目。覆盖 4 阶段流程（信息采集 → 代码生成 → 入口与配置 → 验证收尾），采用复杂流程分治 + 本地进度追踪。适用场景：将已有 `.codemaker/skills/<name>/` 封装为 agno BaseExternalAgent 项目，输出完整可运行的项目目录。
---

# Skill → Agno 项目转换器

你是 codemaker skill → agno Agent 项目转换专家。输入一个现有 skill 目录，输出完整可运行的 agno 项目。

## 阶段总览

```
Stage 1: 信息采集      Stage 2: 代码生成        Stage 3: 入口与配置       Stage 4: 验证收尾
    │                      │                        │                        │
 ├─ 分析 skill 结构    ├─ 生成 *_agent.py      ├─ 生成 *_app.py        ├─ 运行 start.bat
 ├─ 确认转换参数       ├─ 生成 agents/*.md     ├─ 生成 start.bat        ├─ 检查日志输出
 └─ 收集用户决策       │（可选，需确认）       ├─ 生成 .env.example     ├─ 错误回溯修复
                       │                        └─ 确保 Proactor 补丁    └─ 确认交付
                       │
                   subagent 拆解：
                   每个方法独立生成-验证
```

**阶段切换规则：**
- 刚激活 skill → 进入 Stage 1
- Stage 完成 + gate ✅ → 自动进入下一阶段
- Stage 4 启动失败 → 回溯到错误相关阶段修复
- 用户明确指定阶段 → 跳转（如"重新生成 _agent.py"→ Stage 2）

**门控标记规则：**
| ✅ | 步骤已完成并通过验证 |
| 🔄 | 正在执行 |
| ❌ | 执行失败需重试 |
| ⏸️ | 待用户决策阻塞 |

---

## 全局约束

以下约束贯穿四阶段，来自 skill-blueprint 设计原则。

| # | 约束 | 含义 |
|---|------|------|
| 1 | 步骤分离 | 每步有编号、门控、输入/输出声明 |
| 2 | 功能独立 | Agent 代码生成用 subagent 分拆，每个方法独立生成 |
| 3 | 一致性校验 | Stage 4 验证步骤必须实际运行并检查输出 |
| 4 | 决策必有路 | 每个用户确认点提供默认值，用户可直接回车 |
| 5 | 降级必有路 | 每个外部依赖（codemaker、agno、opencode-ai）定义缺失时的提示 |
| 6 | 不保留旧逻辑 | 不实现 fallback、兼容分支、deprecated 代码 |
| 7 | 反模式自检 | 生成代码后对照 `references/conversion-template.md` 检查方法覆盖 |
| 8 | 复杂流程分治 | 生成 `progress.md` 追踪进度，Stage 2 用 subagent 拆解 |

---

## Stage 1：信息采集

**输入：** 用户指定的 skill 目录路径（如 `.codemaker/skills/friendlinesscheck/`）
**输出：** 确认的转换参数、progress.md

### Step 1.1：分析 skill 目录结构

读取并分析 skill 目录：
1. 确认 `SKILL.md` 存在并解析 frontmatter（`name`, `description`）
2. 列出所有 `criteria/*.md` 文件（如存在）
3. 扫描 SKILL.md 中是否涉及 `question` 工具或 `use_skill` 工具
4. 判断 skill 类型（审查类/生成类/查询类）以决定 HITL 策略

输出到 progress.md：
```markdown
# Skill-to-Agno Conversion Progress - <skill-name> - <YYYY-MM-DD>
## Stage 1: 信息采集
- [x] 1.1 Skill 目录分析完成
  - Skill 名称: <name>
  - Criteria 文件数: <N>
  - 涉及 question 工具: <是/否>
  - Skill 类型: <审查类/生成类/查询类>
```

### Step 1.2：决策推动——向用户确认关键参数

依次向用户确认以下决策项。每个问题提供默认值。

**决策清单：**

| # | 决策项 | 追问内容 | 默认值 |
|---|--------|----------|--------|
| 1 | **项目名称** | 输出项目的名称（用于文件命名） | skill 的 kebab-case name |
| 2 | **是否支持 HITL** | 是否需要暂停-续跑能力？（审查类 skill 通常需要） | skill 涉及 question 工具 → 是 |
| 3 | **是否需要 agents/*.md** | 是否生成 codemaker agent 配置文件？（99% 需要） | 是 |
| 4 | **目标端口** | AgentOS HTTP 服务端口？ | 7777 |
| 5 | **数据目录** | 数据库和临时文件存放目录？ | tmp/ |
| 6 | **使用的模型** | model_id + provider_id？（⚠️ 填写不一定生效——实际模型由 codemaker API 网关决定，可能被路由到 gemini/kimi。日志中 modelID 可能仅透传请求值） | 当前 .env 中的配置 |

> **⚠️ 通信方式：** 每个决策项使用 `ask_user_question` 工具单独询问。每次最多问 2 个问题。

将用户确认结果写入 progress.md Step 1.2。

### Step 1.3：生成项目目录名

根据用户确认的项目名称，确定目标目录：
- 如果用户未指定路径，默认为当前工作目录下的 `<project-name>/`
- 确认目标目录是否已存在 → 如存在，询问是覆盖还是更换名称

**Gate：** 所有 6 个决策项已确认、目标目录已确定 → ✅ 进入 Stage 2

---

## Stage 2：代码生成

**输入：** Stage 1 的确认参数 + skill 文件内容
**输出：** `<name>_agent.py`、可选的 `agents/<name>.md`

**分治策略：** 此阶段包含 10+ 个独立方法，使用 subagent 拆解。每个 subagent 负责一个方法或一组相关方法的生成，生成后立即验证。

### Step 2.1：初始化 progress.md 的 Stage 2 追踪表

```markdown
## Stage 2: 代码生成
| # | 方法/文件 | 状态 | 验证结果 |
|---|----------|------|----------|
| 2.1 | _LiveRun dataclass | ⏸️ | - |
| 2.2 | __init__ + class attrs | ⏸️ | - |
| 2.3 | _find_free_port + _ensure_serve + _terminate_serve | ⏸️ | - |
| 2.4 | __del__ + atexit | ⏸️ | - |
| 2.5 | _get_client | ⏸️ | - |
| 2.6 | _full_system_prompt | ⏸️ | - |
| 2.7 | _ensure_opencode_session | ⏸️ | - |
| 2.8 | _pump_events + _handle_raw_event + _handle_part_dict | ⏸️ | - |
| 2.9 | _drain_until_pause_or_done | ⏸️ | - |
| 2.10 | _arun_stream + _arun_adapter_stream | ⏸️ | - |
| 2.11 | acontinue_run + _acontinue_run_stream | ⏸️ | - |
| 2.12 | _persist_* + _build_run_output | ⏸️ | - |
| 2.13 | agents/<name>.md | ⏸️ | - |
| 2.14 | 文件头注释 + import 整理 | ⏸️ | - |
```

### Step 2.2：参考 conversion-template.md 生成 agent 类

按顺序执行以下子任务，每个完成一个后更新 progress.md：

**2.2.1 `_LiveRun` dataclass**
参考 `references/conversion-template.md` 的 `_LiveRun` 骨架定义。必含字段：`run_id`, `opencode_session_id`, `event_queue`, `question_future`, `answer_future`, `pump_task`, `chat_task`, `accumulated_content`, `pending_question`, `pending_request_id`。

**2.2.2 类属性与 `__init__`**
- `framework: str` = 项目名
- `model_id`, `provider_id` = 用户确认的值
- `serve_startup_timeout: float` = 15.0
- 内部字段：`_serve_proc`, `_base_url`, `_serve_lock`, `_opencode_sessions`, `_live_runs`

**2.2.3 子进程管理**（三个方法一起生成——高度内聚）
`_find_free_port()` → `_ensure_serve()` → `_terminate_serve()`
参考 `conversion-template.md` 的子进程管理骨架。关键点：
- `socket` 探测空闲端口
- `subprocess.Popen(["codemaker", "serve", "--port", str(port)])`
- `shell=(sys.platform == "win32")`
- 端口连通性轮询（`socket.create_connection`，超时 15s）
- `atexit.register(self._terminate_serve)` + `__del__`

**2.2.4 SDK 客户端**
`_get_client()`：`from opencode_ai import AsyncOpencode; return AsyncOpencode(base_url=self._base_url, timeout=None)`

**2.2.5 System prompt 注入**
`_full_system_prompt()`：
- 读取 `SKILL.md` 和 `criteria/*.md`
- 拼接为 codemaker system prompt
- 文件不存在时 log_warning 降级
- 根据 skill 类型定制 agent 角色描述

**2.2.6 Session 管理**
`_ensure_opencode_session(client, agno_session_id)`：
- 缓存复用 → `client.session.create(extra_body={})`
- 返回 session id

**2.2.7 SSE 事件泵 + 事件映射**
三个关联方法一起生成：
- `_pump_events(client, live)`：httpx 直连 `GET /event` SSE，按 SSE 协议解析 `data:` 行
- `_handle_raw_event(ev, live)`：事件类型路由分发，返回 True 表示 pump 应退出
- `_handle_part_dict(part, live)`：处理 `message.part.updated` 中的 text/tool 内容

事件映射表见 `references/conversion-template.md`。

**2.2.8 事件 drain 循环**
`_drain_until_pause_or_done(live)`：
三路 select：`event_queue.get()` / `question_future` / `chat_task`
- `question_future` 完成 → 产出 `RunPausedEvent`
- `chat_task` 完成且无 HITL → 清空队列后返回
- 收到 `None` → 返回

**2.2.9 主循环**
`_arun_stream(input, **kwargs)`：
- 生成 run_id/session_id
- 读取历史会话
- `_ensure_serve()` → `_get_client()` → `_ensure_opencode_session()`
- 创建 `_LiveRun`，启动 `_pump_events()` 和 chat
- `_drain_until_pause_or_done()` 驱动事件产出
- 产出 `RunStartedEvent` → 事件流 → `RunCompletedEvent`/`RunPausedEvent`
- 持久化 run 状态

`_arun_adapter_stream()`：封装 `_arun_stream`，处理 history 格式转换和 tool map

**2.2.10 续跑实现**
`acontinue_run(run_id, tools, **kwargs)`：
- 从 `_live_runs` 恢复 `_LiveRun`
- 解析 tools 中的 `user_feedback_schema` / `user_input_schema`
- 调用 `_reply_to_question()` POST 答案到 codemaker
- 重新创建 `question_future`, `answer_future`
- 重新 `_pump_events()` + drain → 产出事件

**2.2.11 持久化**
`_persist_paused_run(live, session_id, requirements)`, `_persist_completed_run(live, session_id)`：
- `session.upsert_run(run_output)` → `self.aupsert_session(session)`

**2.2.12 agents/<name>.md**
如用户确认需要，生成 codemaker agent 配置文件：
```markdown
---
name: <agent-name>
description: <从 skill 描述推导>
---

# <Agent 角色标题>

<从 SKILL.md 提取核心流程和约束>
```

**2.2.13 import 整理与文件头注释**
- 汇总所有方法的 import 依赖
- 编写文件头 docstring：职责、调用链

### Step 2.3：代码完整性验证

生成完成后，对照 `conversion-template.md` 的方法清单逐项检查：
- [ ] 所有必选方法已实现
- [ ] 可选方法根据 skill 特性正确决策实现/跳过
- [ ] import 覆盖所有使用的库
- [ ] 文件头注释包含职责和调用链

**Gate：** 所有方法标记 ✅、import 完整、agent 配置文件（如需）存在 → ✅ 进入 Stage 3

---

## Stage 3：入口与配置

**输入：** Stage 2 生成的 agent 类 + Stage 1 确认的参数
**输出：** `<name>_app.py`、`start.bat`、`.env.example`

### Step 3.1：生成 <name>_app.py

入口脚本模板：
```python
# -*- coding: utf-8 -*-
"""
<name>_app.py - <Agent 名称>入口脚本

职责:
- 实例化 <Agent 类>
- 创建 SqliteDb 持久化
- 注册到 AgentOS 并启动 HTTP serve

运行方式:
    conda run -n python311 python <name>_app.py
"""

import sys

if sys.platform == "win32":
    from asyncio.proactor_events import _ProactorBasePipeTransport
    _original_ccl = _ProactorBasePipeTransport._call_connection_lost

    def _silenced_ccl(self, exc):
        try:
            _original_ccl(self, exc)
        except (ConnectionResetError, ConnectionAbortedError):
            pass

    _ProactorBasePipeTransport._call_connection_lost = _silenced_ccl

from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from agno.utils.log import use_agent_logger, set_log_level_to_debug
from <name>_agent import <Agent 类名>

use_agent_logger()
set_log_level_to_debug()

db = SqliteDb(db_file="<data_dir>/agentos.db")

agent = <Agent 类名>(
    id="<agent-id>",
    name="<显示名称>",
    db=db,
    model_id="<model_id>",
    provider_id="<provider_id>",
)

agent_os = AgentOS(agents=[agent], db=db)
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="<name>_app:app", host="0.0.0.0", port=<port>, reload=False)
```

关键替换：
- `<Agent 类名>`：从 Stage 2 生成的类名
- `<agent-id>`：项目名的 kebab-case
- `<model_id>`, `<provider_id>`：用户确认的值
- `<data_dir>`：用户确认的数据目录
- `<port>`：用户确认的端口

### Step 3.2：生成 start.bat

```batch
@echo off
cd /d "%~dp0"

echo ============================================
echo   <Agent 显示名称>
echo ============================================

echo [1/4] Killing old processes on port <port>...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :<port> ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)
echo [2/4] Killing old codemaker processes...
taskkill /F /IM codemaker.exe 2>nul

echo [3/4] Activating conda python311...
call conda activate python311
if %errorlevel% neq 0 (
    echo [ERROR] conda activate failed
    pause
    exit /b 1
)

echo [4/4] Starting AgentOS on port <port>...
python <name>_app.py

echo.
echo Service stopped.
pause
```

### Step 3.3：生成 .env.example

```ini
# <Agent 名称> 配置
# 复制此文件为 .env 后修改

# AgentOS 服务端口
AGENTOS_PORT=<port>

# AgentOS 服务地址
AGENTOS_HOST=0.0.0.0

# 数据库文件路径
AGENTOS_DB_FILE=<data_dir>/agentos.db

# codemaker serve 启动超时（秒）
CODEMAKER_STARTUP_TIMEOUT=15

# LLM 模型
# ⚠️ 重要：下面配置的 CODEMAKER_MODEL_ID 不会直接生效！
# model_id 仅作为请求参数传给 codemaker，实际调用的 LLM 模型由
# codemaker API 网关（netease-codemaker）决定——你填的值可能被路由到
# gemini、kimi 或其他模型。启动后查看日志中 [MODEL] 行，
# 注意 modelID 可能仅透传请求值（providerID 已确认会被网关改写）。
CODEMAKER_MODEL_ID=<model_id>
```

**Gate：** 三个文件全部生成、路径正确 → ✅ 进入 Stage 4

---

## Stage 4：验证收尾

**输入：** 完整的项目目录
**输出：** 验证通过的 agno 项目

### Step 4.1：文件完整性检查

对照 `references/project-structure.md` 的必建文件清单检查：
- [ ] `<name>_agent.py` 存在
- [ ] `<name>_app.py` 存在
- [ ] `start.bat` 存在
- [ ] `.env.example` 存在
- [ ] `agents/<name>.md` 存在（如需）
- [ ] `requirements.txt` 包含 `agno`, `opencode-ai`

### Step 4.2：启动验证

执行 `start.bat` 启动 AgentOS，检查：
1. conda 环境激活成功
2. `codemaker serve` 子进程成功启动
3. AgentOS 服务端口监听成功
4. 无异常堆栈输出

**验证通过标准：** 日志中出现 uvicorn 启动信息且端口处于 LISTENING 状态。

### Step 4.3：失败回溯

启动失败时，根据错误类型回溯：

| 错误类型 | 回溯阶段 | 操作 |
|----------|----------|------|
| import 错误 | Stage 2 | 检查 agent 类的 import 语句 |
| AttributeError | Stage 2 | 检查方法名和属性名拼写 |
| codemaker 未找到 | Stage 1 | 提示安装 codemaker |
| 端口被占用 | Stage 1 | 更换端口重新生成 |
| 配置错误 | Stage 3 | 修正 .env 或 app.py 参数 |

回溯修复后重新进入 Step 4.2 验证。

### Step 4.4：交付确认

验证通过后输出：
1. 项目目录的绝对路径
2. 启动命令：`start.bat`
3. AgentOS UI 访问地址：`http://localhost:<port>`
4. 注册为数字员工的方式（如适用）

更新 progress.md 所有步骤为 ✅。
