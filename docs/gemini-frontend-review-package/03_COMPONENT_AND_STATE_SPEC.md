# 组件与状态规格

## Status Strip

状态文案建议：

- `本地工作区可用`
- `示例模式`
- `我的资料模式`
- `Mock provider：不会外呼`
- `外部模型未调用（隐私安全）`
- `外部调用需要确认`

禁止文案：

- `External configured` 作为唯一提示；
- 未授权时暗示外部模型已运行；
- 把 examples 结果写成用户真实资料结果。

## Empty State Suggested Prompt

字段：

- title；
- description；
- readiness：ready / needs_input / blocked；
- action label；
- secondary hint。

状态：

- ready：可直接执行；
- needs_input：缺少简历、项目 README 或 JD；
- blocked：需要用户确认外部调用或敏感资料。

交互：

- 点击 ready prompt：填入 composer 或直接发送；
- 点击 needs_input prompt：填入引导文本并聚焦 composer；
- 点击 blocked prompt：显示确认说明，不自动外呼。

## Chat Message

类型：

- user；
- assistant_summary；
- assistant_plan；
- assistant_loading；
- assistant_error；
- assistant_next_step。

要求：

- 错误消息必须有恢复动作；
- loading 消息必须展示正在执行的步骤；
- 计划消息最多显示 3-5 个步骤；
- 长内容可折叠；
- 不展示内部 stack trace。

## Workbench Summary

展示：

- 当前目标；
- 当前阶段；
- 下一步；
- 待确认项数量；
- 可导出文件。

要求：

- 面板不应变成复杂 dashboard；
- 只展示当前最相关内容；
- 历史信息放入折叠或二级层级。
- 初始状态显示“导入资料后，求职产物将在此生成”。
- 移动端以底部抽屉、折叠区域或次级区域呈现，不挤压 Chatbox。

## Artifact Card

标题使用用户语言：

- `岗位解析`
- `匹配报告`
- `申请包草稿`
- `面试准备`
- `复盘训练任务`

状态：

- `可用`
- `待确认`
- `需补充资料`
- `可导出`
- `导出受阻`

操作：

- primary：补充事实 / 去确认 / 导出；
- secondary：查看详情 / 编辑 / 重新生成 / 来源。

工程信息规则：

- artifact id、version id 不作为主标题；
- source refs 和 version 可放入“来源与版本”折叠区；
- JSON 只能作为开发者详情，不是默认阅读方式。
- 阻塞状态下卡片边框高亮，并用辅导语气解释为什么要补充证据。

## Responsive Rules

1280px：

- 双栏布局；
- 左侧任务和对话，右侧推进台和产物；
- Composer 固定在对话区底部。

720px：

- 单栏堆叠；
- Chatbox 空状态 suggested prompts、Conversation、Workbench 顺序排列；
- 产物卡折叠。

390px：

- 顶部状态条压缩为两行以内；
- suggested prompts 在 Chatbox 空状态内纵向排列；
- Composer 不遮挡消息；
- Workbench 折叠为底部抽屉或次级区域；
- 当前任务和主要产物操作必须可达。
