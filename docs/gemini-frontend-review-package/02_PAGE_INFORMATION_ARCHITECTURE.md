# 页面信息架构

## 页面结构

P4 推荐页面由 6 个层级组成：

```text
Experience Shell
→ Status Strip
→ Conversation Plane
  → Empty State Suggested Prompts
  → Composer
  → Loading / Error Recovery
→ Workbench Plane
→ Artifact Review Cards
```

## 1. Experience Shell

职责：

- 给用户稳定的工作台语境；
- 告知产品是本地优先求职材料工具；
- 保持界面安静、专业、可重复使用。

不应承担：

- 营销 hero；
- 大面积装饰；
- 过度解释产品功能。

## 2. Status Strip

展示：

- 当前 workspace 是否可用；
- 当前模式：示例模式 / 我的资料；
- provider 状态：mock 默认 / 外部已配置但本次未调用 / 将外呼需确认；
- 本地隐私边界。

原则：

- 状态条重要，但不能压过任务入口；
- provider 语义必须避免误导用户以为默认外呼。

## 3. Empty State Suggested Prompts

Chatbox 空状态中的核心入口：

- 导入资料；
- 粘贴 JD；
- 生成申请包；
- 准备面试。

每个入口必须包含：

- 动作名称；
- 何时使用；
- 当前是否可执行；
- 缺少前置资料时的下一步。

交互规则：

- suggested prompt 位于 Conversation Plane 内；
- 点击后填入 composer 或直接触发对话；
- 不作为 Chatbox 之外的独立任务区；
- prompt 触发后空状态退出，显示用户消息和 Agent thinking 状态。

## 4. Conversation Plane

展示：

- 用户输入；
- 系统响应；
- 执行计划；
- 失败原因；
- 下一步建议。

原则：

- 有效输入不能无响应；
- 错误不能静默；
- loading / thinking 必须说明正在做什么；
- 错误必须包含恢复 action；
- 不把裸 JSON 作为唯一结果；
- 长 JD 或长材料应可折叠。

## 5. Workbench Plane

展示：

- 当前任务阶段；
- 下一步；
- 关键产物；
- 待确认项；
- 导出状态。

原则：

- Workbench 只管理结果，不承担聊天输入；
- 不显示过多历史阶段矩阵；
- 用户应该能扫一眼知道“现在材料是否可用”。
- 初始状态提示“导入资料后，求职产物将在此生成”；
- 390px 下 Workbench 折叠为底部抽屉或次级面板，避免压缩 Chatbox。

## 6. Artifact Review Cards

产物类型：

- 岗位解析；
- 匹配报告；
- 申请包草稿；
- 面试准备；
- 训练任务。

卡片信息顺序：

1. 产物名称；
2. 可用状态；
3. 一句话摘要；
4. 待确认风险；
5. 主要操作；
6. 可展开的来源和版本信息。
