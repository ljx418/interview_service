# P9.1-M5 自动化验收报告审计

状态：验收脚本和 eval 已落盘；最终状态以脚本运行结果为准。

## 验收目标

生成中文 HTML 自动化验收报告，供人类审计 P9.1 自动化开发是否满足 PRD、目标架构、drawio 和出门条件。报告必须高可读、包含真实界面截图，并明确未验证范围。

## 必须包含

- 目标架构和当前实现；
- 自动化步骤和命令结果；
- PRD 规格检视、代码检视、文档审计；
- 行政区划市场地图截图：初始视图、下钻视图、薪资图层、多视口；
- Socratic Intake 截图和两个不同技术背景的多轮对话 transcript；
- 未验证范围：真实市场 provider、招聘平台抓取、真实 ASR、真实外部 provider、自动投递、MCP/Skill 连通性。

## 验收命令

```bash
npm --prefix apps/chatbox run build
python3 scripts/generate_p9_1_market_socratic_acceptance.py
python3 -m pytest tests/evals/test_p9_1_market_socratic_acceptance_eval.py
git diff --check
```

## 打回条件

- 截图不可见、缺失或小于有效证据阈值；
- 报告无法让人类判断目标架构、当前实现、PRD 覆盖和未验证范围；
- 报告出现 false-green 声明；
- 自动化测试、构建或 eval 失败。

