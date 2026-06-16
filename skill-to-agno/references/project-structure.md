# 目标 agno 项目文件结构

本文档定义从 skill 转换后产出的 agno 项目的标准目录布局和必建文件清单。

---

## 目录布局

```
<project-name>/                      ← 项目根目录（用户指定）
├── <name>_agent.py                  ← Agent 核心类（BaseExternalAgent 子类）
├── <name>_app.py                    ← 入口脚本（AgentOS 注册 + serve）
├── start.bat                        ← 快速启动脚本（Windows）
├── .env.example                     ← 环境配置模板
├── requirements.txt                 ← Python 依赖清单（如需新增）
├── agents/                          ← codemaker agent 配置目录
│   └── <name>.md                    ← agent 配置文件（可选，需用户确认）
└── tmp/                             ← 运行时数据目录
    └── agentos.db                   ← SQLite 数据库（运行时自动创建）
```

---

## 必建文件清单

| # | 文件 | 必要 | 说明 |
|---|------|:---:|------|
| 1 | `<name>_agent.py` | ✅ | BaseExternalAgent 子类，~300行，自管 codemaker serve 子进程 |
| 2 | `<name>_app.py` | ✅ | 入口脚本，实例化 Agent + SqliteDb + AgentOS，启动 HTTP 服务 |
| 3 | `start.bat` | ✅ | 清理旧进程 → 激活 conda → 启动 Python，含错误处理 |
| 4 | `.env.example` | ✅ | 端口、主机、数据库路径、模型配置 |
| 5 | `agents/<name>.md` | ⬜ | codemaker agent 配置文件，含 frontmatter 和系统 prompt |
| 6 | `requirements.txt` | ⬜ | 仅当项目有额外依赖时创建/更新 |

---

## 各文件职责

### <name>_agent.py

- 继承 `agno.agents.base.BaseExternalAgent`
- 管理 `codemaker serve` 子进程（启动、端口、清理）
- 通过 `opencode-ai` SDK 创建 session 并发起 chat
- 订阅 `GET /event` SSE 端点，映射为 agno 事件
- 支持 HITL 暂停/续跑（如 skill 需要）
- 注入 system prompt（读取 SKILL.md + criteria/*.md）

### <name>_app.py

- Windows ProactorEventLoop 补丁（`_call_connection_lost` 静默）
- 初始化 `agno.utils.log` 日志
- 创建 `SqliteDb` 实例
- 创建 `XxxAgent` 实例
- 注册到 `AgentOS`，通过 `agent_os.serve()` 启动

### start.bat

- 第一步：netstat 查找端口占用 → taskkill 清理
- 第二步：taskkill 清理残留 codemaker 进程
- 第三步：conda activate python311
- 第四步：python <name>_app.py

### .env.example

- `AGENTOS_PORT`, `AGENTOS_HOST`, `AGENTOS_DB_FILE`
- `CODEMAKER_STARTUP_TIMEOUT`
- `CODEMAKER_MODEL_ID`（附说明：路由由 codemaker 网关决定）

### agents/<name>.md

```markdown
---
name: <agent-name>
description: <从 skill description 推导>
---

# <Agent 角色标题>

<审查流程、维度、约束>
```

---

## 无需建立的文件

以下文件**不应**由 skill-to-agno 生成：

| 文件 | 原因 |
|------|------|
| `.env` | 包含敏感信息，用户手动创建 |
| `tmp/agentos.db` | 运行时自动创建 |
| `__pycache__/` | Python 自动生成 |
| `README.md` | 用户按需自行编写 |
