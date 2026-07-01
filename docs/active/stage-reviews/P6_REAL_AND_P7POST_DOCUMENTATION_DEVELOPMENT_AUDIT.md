# P6-REAL / P7-post Documentation Development Audit

日期：2026-06-30

## 1. 审计范围

本轮只执行文档开发和 drawio 更新，目标是让 P6-REAL 真实 provider 受控验收与 P7-post P5-REAL 真实资料复验具备可执行规格。

本轮未执行：

- 未调用 MiniMax、DeepSeek、OpenAI-compatible 或其他真实外部 provider；
- 未读取用户真实简历、真实项目资料、真实 JD 或个人目录；
- 未读取、写入、展示或验证真实 API Key；
- 未修改前端、后端或测试代码；
- 未执行 workspace 删除、cleanup apply、migration apply；
- 未进入 SaaS、ASR、会议平台、自动投递、MCP/CLI 开发。

## 2. 输入文档

- `docs/active/00_README.md`
- `docs/active/01_STAGE_PRD.md`
- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/06_TRACEABILITY_MATRIX.md`
- `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`
- `docs/active/19_P6_PROVIDER_BACKED_LONG_CONTEXT_CHAT_PLAN.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio`

## 3. 关键修订

| 修订项 | 结论 |
| --- | --- |
| 当前阶段定位 | 从 P5.5 自动化候选实现阶段切换为 P6-REAL / P7-post 文档准入阶段 |
| 状态分层 | 统一为 `已实现自动化候选`、`待真实验收`、`后续独立阶段` |
| P6-REAL 执行单 | 补齐 provider、model、API Key 本地配置、调用次数、预算、数据类别、timeout/retry/fallback、报告展示字段 |
| P7-post P5-REAL 执行单 | 补齐真实资料路径、允许展示字段、禁止展示字段、脱敏报告和未授权保持未执行 |
| drawio | 重新整理为 6 页，覆盖目标体验、目标架构、代码实体、开发计划、里程碑门槛和安全边界 |
| 虚假验收防线 | 明确 fake provider transcript 不等于真实 LLM 质量，synthetic personas 不等于真实个人资料 |

## 4. 文档支撑度结论

当前文档已经足以支撑下一步进入 P6-REAL / P7-post 的受控执行准备：后续如果用户授权真实 provider 或真实资料路径，可以按文档执行小样本验收、生成脱敏报告并做 PRD 规格检视。

当前文档仍不能直接支撑默认真实 provider 调用、默认真实资料读取、workspace 删除/迁移 apply、SaaS、ASR、会议平台或自动投递。这些能力必须保持高风险确认或 P8+ 独立立项。

## 5. 剩余高风险确认点

- P6-REAL 执行前必须由用户确认 provider、model、API Key 本地配置方式、最大调用次数、预算、数据类别和报告展示字段；
- P7-post P5-REAL 执行前必须由用户提供明确资料路径和允许展示字段；
- 若用户不提供真实资料，P5-REAL 结论必须保持未执行；
- 若用户不提供真实 provider 授权，真实 LLM 质量结论必须保持未执行；
- 删除、清理 apply、迁移 apply、ASR、会议平台、自动投递、SaaS 均不得默认执行。

## 5.1 复评结论：文档是否足以支撑本阶段

结论：当前文档足以支撑本阶段的“文档准入”和后续受控执行准备，但不支持跳过用户授权直接进入真实外呼或真实资料复验。

| 评估项 | 结论 | 依据 |
| --- | --- | --- |
| 开发目标完整性 | 支撑 | PRD、目标架构、里程碑、验收门槛和追踪矩阵均明确 P6-REAL / P7-post 的目标、非目标、输入、输出和打回条件 |
| 架构实体具体性 | 支撑 | drawio 和目标架构列出 Chatbox、FastAPI、ChatCore、Long Context、Provider Adapter、Provider Runtime、Profile、Workspace、报告脚本等具体实体 |
| 自动化开发可执行性 | 支撑受控执行准备 | 文档明确执行单、报告模板、验收门槛和证据边界；真实 provider 调用和真实资料读取仍需用户确认 |
| 出门验收可判定性 | 支撑 | 验收门槛区分文档门槛、P6-REAL 门槛、P7-post 门槛和高风险打回条件 |
| 虚假验收防线 | 支撑 | 明确 fake provider、synthetic personas、脱敏 fixture、dry-run 不能替代真实 provider、真实个人资料或不可逆操作 |
| 产品化完整达成 | 不支撑直接宣称 | 本阶段完成后只能进入受控真实验收准备或小样本真实验收；不能宣称 SaaS、ASR、会议平台、自动投递或最终产品化通过 |

当前未消除且无法通过文档完全消除的风险：

- 真实 provider 质量风险：只有执行真实外呼并生成脱敏证据后才能判断；
- 真实资料多样性风险：只有用户提供明确资料路径后才能复验；
- 成本和隐私风险：必须通过用户确认调用次数、预算、数据类别和报告字段来控制；
- 不可逆操作风险：workspace 删除、cleanup apply 和 migration apply 仍需独立高风险确认，当前阶段不得默认执行。

备选技术路线暂不需要用户选择。推荐路线仍是“本地/mock/fake provider 自动化候选作为基线，用户授权后执行小样本真实 provider 和真实资料复验”。该路线牺牲一次性大范围真实验收速度，但最大限度降低密钥泄露、隐私外发和虚假验收风险。

## 6. 验证记录

已执行：

```bash
git diff --check
python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
p = Path('docs/active/jobpilot-stage-gap-and-acceptance.drawio')
root = ET.parse(p).getroot()
pages = root.findall('diagram')
print(f'drawio_parse=ok pages={len(pages)}')
assert len(pages) <= 8
PY
rg -n "待新增/修改|待开发|待强化" docs/active/02_TARGET_ARCHITECTURE.md docs/active/jobpilot-stage-gap-and-acceptance.md
rg -n "<未执行结论关键词>" docs/active
```

结果：

- `git diff --check`：通过；
- drawio XML parse：通过，页数为 6；
- `02_TARGET_ARCHITECTURE.md` 和 drawio 文本镜像中未发现未限定的 `待新增/修改`、`待开发`、`待强化` 状态；
- 未执行结论关键词扫描仅命中“不得声明 / 不代表 / 禁止出现 / 打回条件”等否定语境，未发现把真实 provider、真实资料或最终产品化写成已通过的正向结论。
