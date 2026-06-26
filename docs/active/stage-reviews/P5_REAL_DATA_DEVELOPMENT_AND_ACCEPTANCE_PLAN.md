# P5-REAL 真实授权资料开发及验收计划

日期：2026-06-26
阶段：P5 真实资料本地闭环 / P5-REAL 与 P5-Freeze
状态：计划与执行器已准备；等待用户提供明确的简历、项目资料和目标 JD 文件路径后执行。

## 1. 范围锁定

本轮只收口 P5，不把职业画像与能力评估插入 P5 冻结范围。职业画像与能力评估作为 P5.5 候选阶段单独立项，不能写成 P5 已实现能力。

P5-REAL 的目标是使用用户明确指定的真实资料，在本地/mock 边界内完成：

```text
简历 + 项目资料 + 目标 JD
→ 本地导入
→ 文本抽取质量检查
→ 资料解析和 source refs
→ JD 解析和匹配报告
→ 申请包生成
→ blocking 导出拦截
→ 确认事实
→ Markdown/DOCX 导出
→ 连续追问
→ 脱敏 HTML 报告
```

## 2. 用户授权输入

执行前必须由用户提供三个明确文件路径：

- `JOBPILOT_REAL_RESUME_PATH`：简历文件；
- `JOBPILOT_REAL_PROJECT_PATH`：项目资料、项目 README 或作品说明；
- `JOBPILOT_REAL_JD_PATH`：目标 JD 文件。

允许展示字段：

- 仅脱敏摘要；
- 可展示资料类型、产物类型、确认项级别、状态机状态、导出结果和文件名级别信息；
- 默认隐藏姓名、联系方式、邮箱、账号、地址、证件号、私密链接、API Key 和未授权长原文。

禁止事项：

- 不得递归扫描用户目录；
- 不得读取未指定文件；
- 不得把完整真实资料写入仓库、报告、日志或测试 fixture；
- 不得调用 MiniMax、DeepSeek、OpenAI-compatible 或其他真实外部 provider。

## 3. 子阶段计划

### P5-REAL-M0：启动审计

执行内容：

- 检查 P5/P6/P7/P8 边界是否仍一致；
- 检查用户是否提供三类明确路径；
- 检查 `JOBPILOT_LLM_PROVIDER` 是否为 `mock` 或 `fixture`；
- 检查目标报告范围是否为仅脱敏摘要；
- 生成临时 `.tmp/p5-real-data-closure.scenario.json` 和 `.tmp/p5-real-data-closure.manifest.json`。

打回条件：

- 缺少任一资料路径；
- 用户只提供目录而不是明确文件；
- provider 不是 mock/local；
- 文档出现“P5 已冻结”或“真实外部 provider 默认路径已通过”的正向声明。

### P5-REAL-M1：文本抽取质量验收

执行内容：

- 对三类文件执行文本抽取；
- 检查抽取文本长度、可读字符比例和资料类型；
- 只把文件复制进本地 workspace；
- 生成资料摘要、source refs 和待确认项。

打回条件：

- PDF/DOCX 或其他格式抽取为空、乱码或二进制噪声；
- 简历、项目资料或 JD 无法支撑后续闭环；
- 导入失败被写成成功。

### P5-REAL-M2：真实资料用户路径验收

执行内容：

- 启动本地 API 和 Chatbox；
- 使用 Chrome/CDP 执行真实界面路径；
- 在截图前注入 redacted summary 样式；
- 覆盖 1200、1440、1600、1920、720、390 视口；
- 完成未确认导出失败、确认后导出成功和连续追问。

打回条件：

- 截图暴露未授权个人信息；
- blocking confirmation 未处理仍能导出；
- 普通追问误写 artifact；
- 多视口出现按钮重叠、文字溢出或关键操作不可达。

### P5-REAL-M3：报告与 PRD 规格检视

执行内容：

- 生成 `docs/reports/P5_REAL_DATA_CLOSURE_ACCEPTANCE_REPORT.html`；
- 报告列出目标架构、当前实现、用户路径、截图证据、PRD 规格检视和未验证范围；
- 报告只展示脱敏摘要，不展示真实资料全文或长原文。

打回条件：

- 报告把 P5-REAL 写成 P5-Freeze；
- 报告把真实外部 provider、SaaS、ASR、会议平台、自动投递或产品化发布写成已通过；
- 报告证据图不可见或不是实际界面截图。

### P5-Freeze：最终冻结审计

执行内容：

- P5-REAL 通过后执行 `.venv/bin/python -m pytest`；
- 执行 `npm --prefix apps/chatbox run build`；
- 执行 drawio XML parse；
- 更新 P5 人工体验审查清单；
- 生成 P5 final closure audit；
- 最终同步 README、TODO、active docs 和 drawio 口径。

打回条件：

- 任一回归失败；
- 文档口径不一致；
- 人工体验记录未通过；
- final closure audit 发现致命或重大规格偏差。

## 4. 执行命令

P5-REAL 场景生成：

```bash
JOBPILOT_LLM_PROVIDER=mock \
JOBPILOT_REAL_RESUME_PATH=/path/to/resume.md \
JOBPILOT_REAL_PROJECT_PATH=/path/to/project.md \
JOBPILOT_REAL_JD_PATH=/path/to/jd.md \
python3 scripts/generate_p5_real_data_acceptance.py
```

浏览器验收执行前必须提醒用户浏览器可能抢占焦点：

```bash
node scripts/browser_tools/browser-acceptance.mjs \
  --start-chrome \
  --scenario .tmp/p5-real-data-closure.scenario.json \
  --output-dir docs/reports/p5-real-data-closure-evidence \
  --report docs/reports/P5_REAL_DATA_CLOSURE_ACCEPTANCE_REPORT.html
```

回归复验：

```bash
.venv/bin/python -m pytest
npm --prefix apps/chatbox run build
python3 - <<'PY'
from xml.etree import ElementTree as ET
pages = ET.parse('docs/active/jobpilot-stage-gap-and-acceptance.drawio').getroot().findall('diagram')
print(f'drawio pages={len(pages)}')
assert len(pages) <= 8
PY
```

## 5. 审计意见

当前可以进入 P5-REAL 授权门准备，但不能执行真实资料读取，直到用户提供三个明确文件路径。

无新增致命规格偏差：

- P5-REAL 使用现有本地工具链和 mock/local provider；
- 不新增后端 API，不做 schema migration，不进行不可逆迁移；
- 不把 P5.5 职业画像、P6 provider、P7 产品化或 P8+ 高风险能力混入 P5；
- 报告默认仅脱敏摘要。

仍需人工处理的高风险流程：

- 用户提供真实资料路径；
- 用户确认报告展示范围；
- 若用户要求真实外部 provider，必须另行进入 P6 opt-in 计划。
