# Skill → Agno 转换模板参考

本文档提供 `BaseExternalAgent` 的标准骨架和 SSE 事件映射表，供 Stage 2 代码生成时参考。不提供完整实现——AI 需根据实际 skill 的业务逻辑填充。

---

## 1. 类骨架

### 1.1 Agent 类定义

```python
from agno.agents.base import BaseExternalAgent
from agno.run.agent import (RunCompletedEvent, RunContentEvent, RunContinuedEvent,
    RunErrorEvent, RunInput, RunOutput, RunOutputEvent, RunPausedEvent,
    RunStartedEvent, ToolCallCompletedEvent, ToolCallStartedEvent)
from agno.run.base import RunStatus
from agno.run.requirement import RunRequirement
from agno.tools.function import UserFeedbackOption, UserFeedbackQuestion
from agno.utils.log import log_exception, log_info, log_warning

@dataclass
class XxxAgent(BaseExternalAgent):
    framework: str = "<project-name>"
    model_id: str = "<user-confirmed>"
    provider_id: str = "<user-confirmed>"
    system_prompt: Optional[str] = None
    serve_startup_timeout: float = 15.0

    _serve_proc: Optional[subprocess.Popen] = field(default=None, init=False)
    _base_url: Optional[str] = field(default=None, init=False)
    _serve_lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    _opencode_sessions: Dict[str, str] = field(default_factory=dict, init=False)
    _live_runs: Dict[str, _LiveRun] = field(default_factory=dict, init=False)
```

### 1.2 _LiveRun dataclass

```python
@dataclass
class _LiveRun:
    """Per-run in-memory state."""
    run_id: str
    user_id: Optional[str]
    input_text: str
    opencode_session_id: str
    event_queue: asyncio.Queue
    question_future: asyncio.Future
    answer_future: asyncio.Future
    pump_task: Optional[asyncio.Task] = None
    chat_task: Optional[asyncio.Task] = None
    accumulated_content: str = ""
    last_streamed_text: str = ""
    accumulated_tools: List[ToolExecution] = field(default_factory=list)
    tool_map: Dict[str, ToolExecution] = field(default_factory=dict)
    pending_question: Optional[Dict[str, Any]] = None
    pending_request_id: Optional[str] = None
    pending_questions_in_order: Optional[List[Dict[str, Any]]] = None
    actual_model: str = ""
    actual_provider: str = ""
```

---

## 2. 必选/可选方法清单

| # | 方法 | 类型 | 说明 |
|---|------|------|------|
| 1 | `__init__` | **必选** | 设置 `framework`, `model_id`, `provider_id`, 内部字段 |
| 2 | `_find_free_port()` | **必选** | `socket.bind(("127.0.0.1", 0))` 返回空闲端口 |
| 3 | `_ensure_serve()` | **必选** | spawn codemaker serve 子进程，轮询端口连通 |
| 4 | `_terminate_serve()` | **必选** | 终止子进程，`atexit` 注册 + `__del__` |
| 5 | `_get_client()` | **必选** | `AsyncOpencode(base_url=self._base_url, timeout=None)` |
| 6 | `_full_system_prompt()` | **必选** | 读取 SKILL.md + criteria/*.md → 拼接 system prompt |
| 7 | `_ensure_opencode_session()` | **必选** | 缓存复用 → `client.session.create(extra_body={})` |
| 8 | `_pump_events()` | **必选** | httpx `GET /event` SSE 流 → `_handle_raw_event()` |
| 9 | `_handle_raw_event()` | **必选** | 事件 type 路由分发（7+ 种事件类型） |
| 10 | `_handle_part_dict()` | **必选** | `message.part.updated` 中 text/tool 分派 |
| 11 | `_drain_until_pause_or_done()` | **必选** | 三路 select (event_queue + question_future + chat_task) |
| 12 | `_arun_stream()` | **必选** | 覆盖 BaseExternalAgent 主循环 |
| 13 | `_arun_adapter_stream()` | **必选** | 封装 _arun_stream，处理 history + tool map |
| 14 | `acontinue_run()` | **可选** | 仅 HITL 模式实现 |
| 15 | `_acontinue_run_stream()` | **可选** | 仅 HITL 模式实现 |
| 16 | `_reply_to_question()` | **可选** | 仅 question 工具存在时实现，POST `/question/{id}/reply` |
| 17 | `_persist_paused_run()` | **可选** | 仅需持久化时实现 |
| 18 | `_persist_completed_run()` | **可选** | 仅需持久化时实现 |
| 19 | `_build_run_output()` | **可选** | 辅助构建 RunOutput |
| 20 | `_arun_adapter()` | **必选** | 聚合文本输出用于同步调用 |

---

## 3. SSE 事件映射表

所有 codemaker SSE 事件 → agno 事件的完整映射。`_handle_raw_event()` 按此表实现路由分发。

| # | codemaker SSE `type` | 处理 | agno 事件 | 退出 pump |
|---|---------------------|------|-----------|:---:|
| 1 | `session.created` | 忽略 | 无 | 否 |
| 2 | `message.part.updated` (text) | 去重 delta → `RunContentEvent` | `RunContentEvent` | 否 |
| 3 | `message.part.updated` (tool, pending/running) | 创建 `ToolCallStartedEvent` | `ToolCallStartedEvent` | 否 |
| 4 | `message.part.updated` (tool, completed) | 更新 result → `ToolCallCompletedEvent` | `ToolCallCompletedEvent` | 否 |
| 5 | `message.part.updated` (tool="question") | **跳过**——question 走专用通道 `question.asked` | 无 | 否 |
| 6 | `message.updated` (assistant) | 提取 `info.modelID` / `info.providerID` → 日志 | 无 | 否 |
| 7 | `question.asked` | 构建 `RunPausedEvent` → set `question_future` | `RunPausedEvent` | 否 |
| 8 | `question.answered` | 忽略（续跑已经通过 `/reply` 触发） | 无 | 否 |
| 9 | `session.diff` | 记录 keys 日志 | 无 | 否 |
| 10 | `session.idle` | 写入 `event_queue.put(None)` | 结束信号 | **是** |
| 11 | `session.error` | 写入 `RunErrorEvent` + `None` | `RunErrorEvent` | **是** |
| 12 | `message.part.delta` | **静默跳过**（极高频率，不记录日志） | 无 | 否 |
| 13 | 其他未知 | `log_info(type, props_keys)` 记录（不丢弃） | 无 | 否 |

### 3.1 事件过滤规则

在 `_handle_raw_event()` 中，**每个事件必须校验 `sessionID`**：
- 如果 `props.sessionID != live.opencode_session_id` → `return False`（不属于当前 session）

### 3.2 未知事件处理

```python
# 静默跳过高频噪音
if ev_type == "message.part.delta":
    return False

# 记录未知类型供后续扩展
log_info(f"[SSE] unhandled event type={ev_type} props_keys={list(props.keys())}")
return False
```

---

## 4. HITL 暂停/续跑流程

### 4.1 `question.asked` → `RunPausedEvent`

```python
# 多选：user_feedback_schema
options = [UserFeedbackOption(label=o["label"], description=o.get("description", ""))
           for o in q.get("options", [])]
schema = UserFeedbackQuestion(
    question=q.get("question", ""),
    header=q.get("header", ""),
    options=options,
    multi_select=q.get("multiple", False),
)

# 自由输入：user_input_schema（无 options 时）
schema = [{"name": "answer", "field_type": "str", "description": q.get("question", "")}]
```

### 4.2 `acontinue_run` 续跑

```python
async def acontinue_run(self, run_id, tools, **kwargs):
    live = self._live_runs.pop(run_id)
    answers = {}

    for t in tools:
        t_dict = t if isinstance(t, dict) else t.to_dict()
        # 多选：user_feedback_schema[*].value
        for uf in t_dict.get("user_feedback_schema", []):
            answers[uf["header"]] = uf.get("value", [])

        # 自由输入：user_input_schema[*].value
        for ui in t_dict.get("user_input_schema", []):
            answers[ui["name"]] = ui.get("value", "")

    # 调用 codemaker /question/{id}/reply
    await self._reply_to_question(live, answers)

    # 重建 futures，重新 pump
    live.question_future = asyncio.get_event_loop().create_future()
    live.answer_future = asyncio.get_event_loop().create_future()
    live.pending_question = None

    # 重新 drain → 产出事件
```

---

## 5. 子进程管理关键代码

```python
def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

def _ensure_serve(self) -> str:
    if self._serve_proc and self._serve_proc.poll() is None:
        return self._base_url  # 复用

    port = self._find_free_port()
    self._serve_proc = subprocess.Popen(
        ["codemaker", "serve", "--port", str(port)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        shell=(sys.platform == "win32"),
    )
    atexit.register(self._terminate_serve)

    # 等待端口就绪（轮询 + 超时）
    deadline = time() + self.serve_startup_timeout
    while time() < deadline:
        if self._serve_proc.poll() is not None:
            raise RuntimeError("codemaker serve exited prematurely")
        try:
            with socket.create_connection(("127.0.0.1", port), 0.25):
                self._base_url = f"http://127.0.0.1:{port}"
                return self._base_url
        except OSError:
            sleep(0.1)
    self._terminate_serve()
    raise RuntimeError("codemaker serve not reachable")

def _terminate_serve(self) -> None:
    # terminate → wait(3s) → kill
```

---

## 6. 常见陷阱

| # | 陷阱 | 预防 |
|---|------|------|
| 1 | `_arun_stream` 返回后 BaseExternalAgent 自动写 `RunCompletedEvent`，覆盖 paused 状态 | 发现 `RunPausedEvent` 立即 `return`，不依赖父类收尾 |
| 2 | Windows `ProactorEventLoop` 下 `ConnectionResetError` → 启动崩溃 | `_app.py` 头部加 `_ProactorBasePipeTransport._call_connection_lost` 静默补丁 |
| 3 | `session.chat()` 返回但 `session.idle` 未到达 → 永久 `RUNNING` | `_drain_until_pause_or_done` 加 `chat_task` 第三路等待 |
| 4 | `question.asked` 与 `chat_task` 完成出现竞态 | pause 优先级高于完成（D2 决策） |
| 5 | `model_id`/`provider_id` 配置值 ≠ 真实路由值，日志中 modelID 可能仅透传请求值 | 从 `message.updated` 提取到的是 codemaker 回传的 modelID（可能为请求 echo）。真实模型需直调 `/chat/completions` 看响应 `model` 字段 |
| 6 | `shell=True` 仅在 Windows 下使用 | `shell=(sys.platform == "win32")` |
| 7 | uvicorn `reload=True` 强制 `SelectorEventLoop` → subprocess 不可用 | `serve(reload=False)` |
