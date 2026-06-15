# M9 PiAgent Chat Core 接入计划与审计

## 关联规格

- PRD 路径：Chatbox 仍是默认入口，用户输入必须继续生成可确认、可追溯、可导出的求职产物。
- 目标架构：Chatbox 不承载 Agent 编排；对话编排应位于后端 Chat Intent Router 和 Domain Tool Planner。
- P0 边界：接入 PiAgent 不能绕过本地 workspace、Domain Tools、artifact 状态、source refs、questions_to_confirm、schema validation 和 formal_assist 安全边界。

## 当前审计结论

本地工作区未找到可直接移植的 PiAgent 源码，也未发现已安装的 `piagent`、`pi-agent` 或 `pi_agent` Python 包。

因此本阶段不直接声明“PiAgent 已完成移植”。直接迁入未知来源源码属于高风险流程，必须先确认源码路径、许可证和依赖边界。

## 开发计划

- 新增 `services/chat` 层，定义稳定的 ChatCore 接口。
- 将当前 `/api/chat/message` 的关键词意图路由抽成 `KeywordChatCore`，保持 P0 默认行为不变。
- 新增 `PiAgentChatCore` adapter：
  - 支持从项目内移植模块加载 PiAgent；
  - 支持 `JOBPILOT_CHAT_CORE=piagent` 切换；
  - 支持 `JOBPILOT_CHAT_CORE_STRICT=1` 在 PiAgent 不可用时报错；
  - 默认非严格模式下回退到 `KeywordChatCore`，避免 P0 被未知依赖破坏。
- `/api/chat/message` 改为调用 ChatCore，不直接内联意图路由。
- 增加 eval，验证默认 core 行为不变、PiAgent 不可用时可控回退、严格模式清晰失败。

## 验收标准

- `python3 -m pytest` 通过；
- `npm --prefix apps/chatbox run build` 通过；
- 使用 `examples/` 匿名真实感数据端到端路径仍可跑通；
- PRD 规格检视确认 Chatbox 仍是薄入口，PiAgent 接入点没有绕过本地优先、artifact 和事实安全边界。

## 审计意见

- 致命风险：无，前提是本阶段不迁入未知来源源码。
- 重大风险：直接复制未审计源码可能引入许可证、网络调用、隐私和依赖风险。处理：先落 adapter 和严格模式，等待人类提供源码路径后再做迁移审计。
- 虚假验收风险：不能把 fallback 通过说成 PiAgent 已接入成功。处理：测试和文档必须区分 adapter ready 与 PiAgent source migrated。
- 范围风险：不实现 MCP/CLI、真实外部模型调用、多 Agent 图形编排或复杂 memory。

## 当前结论

可以进入 M9 实质开发：实现 PiAgent 接入边界、默认回退和验收测试。实际 PiAgent 源码迁移需等待源码路径与许可证确认。

## 完成记录

- 新增 `services/chat/core.py`：定义 `ChatCore` 协议、默认 `KeywordChatCore` 和 `get_chat_core()`。
- 新增 `services/chat/piagent_adapter.py`：支持从 `services/piagent`、`vendor/piagent` 或已安装 `piagent` 包加载 `handle_message`、`PiAgentCore.handle_message` 或 `create_core().handle_message`。
- `/api/chat/message` 已改为调用 `get_chat_core().handle_message(...)`，FastAPI endpoint 不再内联关键词路由。
- 新增环境变量：
  - `JOBPILOT_CHAT_CORE=piagent`：尝试启用 PiAgent adapter；
  - `JOBPILOT_CHAT_CORE_STRICT=1`：PiAgent 不可用时直接失败，避免 fallback 被误验收为 PiAgent。
- 新增 `tests/evals/test_piagent_chat_core_integration_eval.py`：覆盖默认 core 行为、PiAgent 缺失回退、严格模式失败、模拟移植模块可被调用。

## 验收结果

- `python3 -m pytest`：21 passed。
- `npm --prefix apps/chatbox run build`：通过。
- HTTP 端到端验收：通过。使用 `examples/` 匿名真实感数据完成 workspace、资料导入、ChatCore 默认路径下的资料整理、JD 分析、申请包生成和会话恢复。
- 端到端验收证据：恢复会话包含 6 条消息、6 个 artifact。
- 临时验收服务已停止。

## PRD 规格检视

M9 没有把未知 PiAgent 源码伪装为已完成迁移，而是完成了后端 ChatCore 可替换边界。Chatbox 仍是薄入口，Domain Tools、artifact 写入、source refs、questions_to_confirm、workspace 沙箱和 P0 mock 验收基线保持不变。未新增 MCP/CLI、外部模型默认调用、多 Agent dashboard、复杂 memory、ASR 或会议平台能力。

实际 PiAgent 源码迁移仍未完成，原因是本地未发现目标源码且许可证未确认。该问题属于高风险流程，必须由人类提供源码路径或仓库、许可证口径和允许移植范围后再继续。

---

# M10 PiAgent 源码拉取与迁移审计

## 用户目标

用户要求使用 GitHub CLI 将 PiAgent 拉取到 workspace 文件夹内，阅读该项目，并尝试迁移到当前项目。

## 执行记录

- 已尝试 `gh search repos piagent`：失败，原因是本机 GitHub CLI 未登录，提示需要 `gh auth login` 或 `GH_TOKEN`。
- 已通过 GitHub 公共 API 搜索 PiAgent 候选仓库。
- 已尝试 `gh repo clone aslanpour/PiAgent vendor/piagent_source -- --depth 1`：失败，原因同样是 GitHub CLI 未登录。
- 已退回使用 `git clone --depth 1 https://github.com/aslanpour/PiAgent.git vendor/piagent_source` 拉取公开源码。
- 当前源码路径：`vendor/piagent_source`。
- 当前拉取 commit：`78a8cad Update pi-agent-v1.10.7.py`。

## 仓库审计

候选仓库：

- GitHub：`https://github.com/aslanpour/PiAgent`
- README 标题：`AdaptiveEdge`
- README 描述：`A Self Adaptive Cloud Fog and Edge Platform`
- 主要语言：Python
- LICENSE：未发现 `LICENSE`、`COPYING` 或等价许可证文件
- 主要源码：
  - `pi-agent-v1.10.7.py`
  - `setup-v1.10.7.py`
  - `excel_writer.py`
  - `usb_meter_connection.py`
  - `deployments/*.yaml`

关键依赖和行为：

- Flask / Waitress HTTP 服务；
- `requests`、`psutil`、`numpy`、`statistics`；
- Raspberry Pi 相关依赖：`RPi.GPIO`、`pijuice`、`bluetooth`；
- OpenFaaS / Kubernetes / Helm / kubectl 相关命令；
- 调度函数：`scheduler_planner_greedy`、`scheduler_planner_binpacking`、`scheduler_planner_local`、`scheduler_planner_default`、`scheduler_planner_random`；
- `pi_service` 接收 `plan/on/stop/metrics/charge` 等边缘节点控制命令。

## 迁移判断

该仓库不是 Chatbox / LLM / Tool-calling Agent core，而是 Raspberry Pi 和 OpenFaaS 场景下的自适应边缘计算调度平台。它不提供以下当前项目需要的对话核心能力：

- `handle_message(workspace_id, session_id, message)`；
- 用户意图识别；
- 面向 JobPilot Domain Tools 的工具计划；
- source refs / questions_to_confirm / artifact 状态协议；
- formal_assist 面试提示安全边界；
- 本地求职 workspace 语义。

同时该仓库存在重大迁移风险：

- 未发现许可证文件，不能安全复制核心源码进入当前项目；
- 顶层导入硬件和系统依赖，普通开发机和 CI 环境无法稳定 import；
- 运行路径可能调用网络、蓝牙、GPIO、Helm、kubectl 和 OpenFaaS，超出当前 P0 本地求职 Agent 服务范围；
- 数据结构与当前 PRD/目标架构完全不同，无法直接替换 ChatCore。

## 当前结论

迁移被打回确认：`aslanpour/PiAgent` 不适合作为本项目 ChatCore 源码迁移目标。

当前保留 `vendor/piagent_source` 作为已拉取候选源码副本，便于人工确认是否拉错仓库。除源码副本和本文档审计记录外，不把该 PiAgent 源码接入运行路径，不修改默认 P0 行为。

## 后续条件

继续真正迁移前需要人类确认至少一项：

- 这个 `aslanpour/PiAgent` 就是目标项目，并接受“只能作为边缘调度算法参考，不能作为 ChatCore 直接迁移”的结论；
- 或提供正确的 PiAgent 仓库 URL / 本地路径；
- 或完成 GitHub CLI 登录后指定准确仓库。

在未确认前，当前项目继续使用 M9 已实现的 ChatCore adapter，保持 `KeywordChatCore` 为默认 P0 验收基线。

---

# M11 正确 Pi 项目源码迁移审计

## 用户更正

用户确认目标项目是：

```text
https://github.com/earendil-works/pi
```

## 下载与构建记录

- `gh repo clone` 仍因本机 GitHub CLI 未登录不可用；
- `git clone --depth 1 https://github.com/earendil-works/pi.git vendor/earendil_pi_source` 两次失败，原因分别为 GitHub HTTP/2 framing error 和 443 连接超时；
- 已通过 GitHub 公共 API 确认仓库元信息：
  - 描述：`AI agent toolkit: unified LLM API, agent loop, TUI, coding agent CLI`
  - 默认分支：`main`
  - License：MIT
  - 主要语言：TypeScript
- 已通过 GitHub zip 归档下载并解压源码到 `vendor/earendil_pi_source`；
- 已执行 `npm ci --ignore-scripts`，依赖安装成功；
- 已尝试构建：
  - `npm --workspace @earendil-works/pi-ai run build`：失败；
  - `npm --workspace @earendil-works/pi-agent-core run build`：失败，因为依赖 `@earendil-works/pi-ai` 未成功构建。

## 正确项目审计

该仓库是 Pi Agent Harness monorepo，核心包包括：

- `packages/agent`：`@earendil-works/pi-agent-core`，提供 `Agent`、agent loop、tool calling、state management 和 event streaming；
- `packages/ai`：`@earendil-works/pi-ai`，提供多 provider LLM API；
- `packages/coding-agent`：交互式 coding agent CLI；
- `packages/tui`：终端 UI。

`packages/agent` 与 JobPilot 目标架构中的 Chat Intent Router / Domain Tool Planner 概念匹配，但存在工程差异：

- Pi 是 TypeScript/Node 22+ ESM 包；
- JobPilot 后端是 Python/FastAPI；
- Pi core 需要构建后的 `packages/ai/dist` 和 `packages/agent/dist` 才能由 Node runtime 导入；
- Pi 的 tool schema、event stream 和 LLM provider 协议与 JobPilot 的 Python Domain Tools、artifact/source refs 协议不同，需要 bridge，而不是直接替换。

## 构建失败原因

`pi-ai` build 会运行模型索引生成脚本，尝试访问：

- `models.dev`
- `openrouter.ai`
- `ai-gateway.vercel.sh`

当前环境无法解析这些域名，脚本 fallback 生成了部分模型数据，但随后 TypeScript 编译失败：

```text
src/models.ts: Type 'TProvider' cannot be used to index type ...
```

构建命令返回失败，因此不能作为正式 build gate 通过。后续探测显示本地 `dist` 文件已部分生成且 `Agent` 可被 Node import，但这只证明 Pi core 可加载，不代表已经完成 JobPilot Domain Tools 桥接。

## 本阶段迁移实现

已将 JobPilot 的 Pi adapter 升级为真实 TypeScript bridge 边界：

- 新增 `services/chat/pi_node_bridge.mjs`；
- `PiAgentChatCore` 现在会识别 `vendor/earendil_pi_source`；
- 如果 `packages/ai/dist/index.js` 或 `packages/agent/dist/index.js` 不存在，返回 `PI_AGENT_NOT_BUILT`；
- 如果 Pi core 可 import 但 JobPilot Domain Tools 尚未接入 Pi tool loop，返回 `PI_JOBPILOT_TOOL_BRIDGE_NOT_IMPLEMENTED`；
- 非严格模式下回退到 `KeywordChatCore`，并记录：

```json
{
  "requested": "piagent",
  "active": "keyword",
  "reason": "pi_agent_not_built | pi_jobpilot_tool_bridge_not_implemented"
}
```

- 严格模式下抛出 `PiAgentUnavailableError`，避免把 fallback 误验收成 Pi runtime。

## 当前结论

正确 Pi 项目已经下载、审计，并完成 JobPilot 侧可切换 bridge 边界。Pi core 在当前机器上可被 Node bridge 探测到，但 JobPilot Domain Tools 尚未接入 Pi tool loop，因此 Pi runtime 仍未真正进入生产运行路径。

这不是 P0 阻塞项。当前项目继续保持 `KeywordChatCore` 作为默认验收基线；`JOBPILOT_CHAT_CORE=piagent` 会尝试 Pi bridge，但在工具桥未完成时可控回退。

## 后续条件

要完成真实 Pi runtime 接入，需要至少满足以下条件之一：

- 上游 Pi 源码能在当前环境成功执行 `packages/ai` 和 `packages/agent` build；
- 或使用已发布 npm 包 `@earendil-works/pi-agent-core` 与 `@earendil-works/pi-ai`，并完成依赖许可证和供应链审计；
- 或为 JobPilot 编写专用 Node bridge，只复用 Pi agent loop 的稳定 dist，而不引入 coding-agent CLI 和 TUI。

在真实接入前，必须继续保留 JobPilot 的 workspace、artifact、source refs、questions_to_confirm、formal_assist 安全边界和 Markdown hard gate。

---

# M12 P1 前置：Pi Agent Core 基础对话

## 目标

在正式进入 P1 复杂工具编排前，先让 Chatbox 能通过 Pi Agent Core 完成基础普通对话，验证 Python/FastAPI 到 TypeScript/Node Pi runtime 的最小桥接路径。

## 开发计划

- 继续使用 `JOBPILOT_CHAT_CORE=piagent` 作为显式开关；
- `services/chat/pi_node_bridge.mjs` 直接实例化 `@earendil-works/pi-agent-core` 的 `Agent`；
- 使用本地 deterministic `streamFn`，不调用外部 LLM provider，不要求 API key；
- 不接入 JobPilot Domain Tools，避免普通聊天阶段绕过 artifact/source refs/confirmation 边界；
- Pi bridge 成功后，由 Python adapter 将 user/assistant 消息写入 JobPilot chat session，保证 Chatbox 可恢复；
- 默认模式仍是 `KeywordChatCore`，P0 申请包/JD/面试路径不变。

## 验收标准

- `JOBPILOT_CHAT_CORE=piagent` 下发送普通问候，返回 `chat_core.active = piagent_core_basic`；
- Pi 基础回复写入 `chat_message`，刷新后可通过 session API 恢复；
- 发送“申请包/JD/岗位”等业务请求时，Pi 基础模式不得伪造 artifact；
- `python3 -m pytest` 通过；
- `npm --prefix apps/chatbox run build` 通过；
- PRD 检视确认未把未完成的 Pi tool loop 当成业务产物生成能力。

## 审计意见

- 致命风险：无，前提是 Pi 基础对话不生成求职 artifact。
- 重大风险：用户可能误以为 Pi 已接管完整 JobPilot 工具链。处理：返回的 `chat_core.tool_bridge` 明确为 `not_enabled`，文档明确业务工具仍由 JobPilot 工具链负责。
- 虚假验收风险：不能只证明 Node bridge import 成功，必须证明 Pi `Agent.prompt()` 被调用并写入 chat session。
- 范围风险：不实现 MCP/CLI、外部 LLM、Pi coding agent CLI、TUI、复杂 memory 或 JobPilot tools in Pi loop。

## 完成记录

- `services/chat/pi_node_bridge.mjs` 已改为实例化 Pi `Agent`；
- 新增本地 deterministic `streamFn`，用于基础对话，不访问外部模型；
- `PiAgentChatCore` 在 bridge 成功时会将 user/assistant 消息写入当前 JobPilot chat session；
- Pi 基础对话返回 `chat_core.active = piagent_core_basic` 和 `tool_bridge = not_enabled`；
- JobPilot 默认 P0 模式仍为 `KeywordChatCore`。

## PRD 规格检视

M12 满足“Chatbox 能通过 Pi Agent Core 实现基础对话”的前置目标，但不声称 Pi 已完成 JobPilot 业务工具编排。当前实现没有绕过 workspace、artifact、source refs、questions_to_confirm、formal_assist 安全边界，也没有引入外部模型默认调用。下一阶段若要让 Pi 生成 JD 分析、申请包或面试材料，必须先把 JobPilot Domain Tools 注册为 Pi `AgentTool`，并继续执行 artifact/schema/eval gates。

---

# M13 Pi Agent Core 业务编排接管

## 目标

在 P1 前让 Pi 直接接管 Chatbox 的基础业务编排：用户从聊天框输入资料整理、JD、申请包或面试准备请求时，由 Pi Agent Core 通过 `AgentTool` 产出 JobPilot 工具计划，再由 Python 后端执行现有 Domain Tools。

## 开发计划

- 在 `services/chat/pi_node_bridge.mjs` 中注册 `jobpilot_orchestrate` AgentTool；
- Pi bridge 根据用户消息产出明确 intent：
  - `extract_profile`
  - `analyze_job`
  - `create_application_package`
  - `prepare_interview`
  - `basic_chat`
- 对业务 intent，Pi `Agent.prompt()` 必须真实执行 tool call，并在 tool result `details` 中返回工具计划；
- Python `PiAgentChatCore` 读取 Pi 工具计划后调用现有 `services.tools.jobpilot`：
  - `extract_facts`
  - `parse_jd`
  - `match_profile`
  - `create_application_package`
  - `prepare_interview`
- Python 继续负责 workspace、SQLite、artifact_refs、source_refs、questions_to_confirm 和 chat session 持久化；
- 不引入外部 LLM，不执行 Pi coding-agent CLI/TUI，不让 Node bridge 直接写数据库或文件产物。

## 验收标准

- `JOBPILOT_CHAT_CORE=piagent` 下发送真实 JD，返回 `chat_core.active = piagent_business_orchestrator`；
- Pi orchestration metadata 中包含 `source = pi_agent_tool_call` 和 `tool_plan`；
- JD 请求产生 `job` 和 `match_report` artifact；
- 申请包请求基于最近 JD 产生 `application_package` artifact；
- 面试请求基于最近 JD 产生 `interview_prep` artifact；
- 普通问候仍走 `piagent_core_basic`，不得伪造 artifact；
- chat session 可恢复 user/assistant 消息与 artifact refs；
- `python3 -m pytest`、前端 build 和真实 examples 端到端 HTTP 验收通过。

## 审计意见

- 致命风险：无，前提是 Pi 只接管编排，不直接绕过 Python Domain Tools 写 artifact。
- 重大风险：把 deterministic intent matcher 误称为完整 LLM Agent。处理：文档和返回字段明确当前是 Pi Agent Core + local deterministic stream/tool plan，不默认调用外部模型。
- 虚假验收风险：只返回业务文本但未执行 Pi tool loop。处理：eval 需要断言 `orchestration.source = pi_agent_tool_call`，并验证真实 artifact 产生。
- 范围风险：本阶段不做多 Agent、外部模型 provider、MCP Server、CLI、复杂 memory、ASR 或会议平台接入。

## 进入开发结论

审计意见已闭环，无新增致命或重大规格偏差。可以进入 M13 实质开发。

## 完成记录

- `services/chat/pi_node_bridge.mjs` 已注册 `jobpilot_orchestrate` Pi `AgentTool`；
- Pi bridge 对业务请求会通过 `Agent.prompt()` 触发 tool call，并返回：
  - `orchestration.intent`
  - `orchestration.tool_plan`
  - `orchestration.source = pi_agent_tool_call`
  - `chat_core.active = piagent_business_orchestrator`
  - `chat_core.tool_bridge = python_jobpilot_domain_tools`
- `services/chat/piagent_adapter.py` 已按 Pi orchestration intent 执行现有 JobPilot Domain Tools；
- 已接入并验证：
  - 资料整理：`extract_profile -> extract_facts`
  - JD 分析：`analyze_job -> parse_jd + match_profile`
  - 申请包：`create_application_package -> create_application_package`
  - 面试准备：`prepare_interview -> prepare_interview`
- 普通问候仍保留 `piagent_core_basic`，不生成 artifact；
- Python 继续负责 workspace、SQLite、artifact refs、chat session 持久化和本地文件边界。

## 子阶段验收结果

- `python3 -m pytest tests/evals/test_piagent_chat_core_integration_eval.py -q`：7 passed；
- 该 eval 使用 `examples/` 中的匿名真实感简历、项目 README 和 Junior Frontend JD；
- eval 断言 Pi 编排来源为 `pi_agent_tool_call`，并验证真实 `job`、`match_report`、`application_package`、`interview_prep` artifact 产生；
- eval 断言 chat session 中 user/assistant 消息和 artifact refs 可恢复。

## PRD 规格检视

M13 符合当前阶段目标：Chatbox 继续作为极简入口，业务编排从 Python 关键词路由迁移到 Pi Agent Core 的 tool-call 计划，真实业务产物仍通过 JobPilot Domain Tools 生成。该实现没有扩大到 P1/P2 范围，没有引入默认外部模型调用、MCP Server、CLI、多 Agent dashboard、复杂 memory、ASR 或会议平台接入。

剩余风险不是规格偏差，而是工程成熟度风险：当前 Pi 的 intent 选择仍是本地 deterministic streamFn，不是外部 LLM provider 推理。该风险已在返回字段和文档中标注，不阻塞 P1 前“Pi 接管基础业务编排”的目标，但后续若要接入真实 LLM provider，必须重新做 provider、prompt contract、隐私和 eval 审计。

## 最终验收结果

- `python3 -m pytest`：24 passed；
- `npm --prefix apps/chatbox run build`：通过；
- HTTP 端到端验收：通过；
- HTTP 验收环境：
  - `JOBPILOT_CHAT_CORE=piagent`
  - `uvicorn services.api.main:app --host 127.0.0.1 --port 8008`
  - 使用 `examples/resumes/transition_frontend_resume.md`
  - 使用 `examples/projects/todoplus_README.md`
  - 使用 `examples/jds/junior_frontend_jd.md`
- HTTP 验收路径：
  - 初始化 workspace；
  - 导入简历和项目 README；
  - 创建 chat session；
  - 发送“整理资料”，产生 `career_facts`；
  - 发送真实 JD，产生 `job` 和 `match_report`；
  - 发送“生成申请包”，产生 `application_package`；
  - 发送“生成面试准备”，产生 `interview_prep`；
  - 恢复 chat session，确认 8 条消息和 assistant artifact refs。

## 最终审计意见

M13 通过。当前实现已经满足“P1 前通过聊天框实现基础业务对话，core 直接使用 Pi Agent Core 接管业务编排”的目标。

没有发现需要暂停确认的致命或重大规格偏差。需要明确保留的事实是：当前 Pi 接管的是 Chat Intent Router / Domain Tool Planner 层，真实业务工具执行仍在 Python 后端完成。这与 PRD 和目标架构一致，因为 artifact、source refs、questions_to_confirm、workspace 沙箱和导出边界仍由 JobPilot 服务控制。
