# 视觉系统与组件规格

## 设计方向

这是一个“求职材料工作台”，不是营销页，也不是复杂 BI dashboard。视觉应当专业、克制、可信、可长时间使用。

设计应避免：

- 大型营销 hero；
- 紫蓝粉渐变背景；
- 装饰性 orb、bokeh、无意义插画；
- 伪造客户 logo、伪造指标；
- 裸 JSON 做主视觉；
- 所有按钮同等视觉权重。

## Design Decisions

- Color palette: graphite neutral, deep teal primary, calm blue info, amber warning, red danger.
- Typography: Chinese system UI stack, compact workbench scale, no oversized hero type.
- Spacing system: 4px base, common steps 4/8/12/16/20/24/32.
- Border-radius strategy: 6-8px cards and controls, no overly round pill-card UI except compact status chips.
- Shadow hierarchy: mostly borders and subtle elevation; avoid glossy card stacks.
- Motion style: short 160-220ms transitions for state changes, respect reduced motion.

## 关键组件

### Top Status Strip

- 本地就绪；
- 示例模式 / 我的资料 segmented control；
- 外部模型未调用（隐私安全）；
- 当前使用匿名示例数据或本地资料。

### Conversation Plane

- 空态建议任务必须在 Chatbox 内。
- 消息流支持自由追问、状态查询、计划回复、错误回复。
- Thinking 状态要展示具体步骤，而不是单独 spinner。
- 长文本可折叠。

### Composer

- 上传资料；
- 多行文本输入；
- 发送任务；
- Enter 发送、Shift+Enter 换行；
- 390px 下按钮和输入不得互相遮挡。

### Workbench Plane

- 当前目标；
- 产物列表；
- 待确认项；
- 版本信息；
- 导出状态；
- 移动端抽屉。

### Artifact Card

每张产物卡必须有：

- 求职语义标题；
- 一句话价值摘要；
- source refs 或来源说明；
- questions_to_confirm；
- primary action；
- secondary actions；
- 状态标签。

## 可访问性要求

- 所有可点击控件有可理解 label。
- segmented control 使用 `aria-pressed`。
- Workbench drawer 使用 `aria-expanded` 和 `aria-controls`。
- 触控目标不小于 44px。
- 键盘焦点清楚。
- 文本不溢出按钮、卡片和状态标签。
