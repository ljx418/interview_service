# P9.1 真实市场数据 Provider 调研

状态：文档调研，不代表 provider 已接入。

## 1. 调研结论

P9.1 不应默认抓取招聘平台。更稳妥路线是 opt-in API provider：

1. 未配置 provider：只使用 fixture、用户粘贴、已导入 JD 和公开示例。
2. 用户配置 provider：通过明确授权、API Key 本地保存策略、调用预算和日志脱敏后再执行。
3. provider 调用后：每个聚合指标必须保留 source refs 和 provider 边界。

## 2. 候选 provider

| Provider | 文档入口 | 适用 | P9.1 处理 |
| --- | --- | --- | --- |
| Adzuna | `https://developer.adzuna.com/` | 职位搜索 API，适合海外职位和公开聚合 | opt-in 候选 |
| TheirStack | `https://theirstack.com/en/docs/api-reference` | 技术岗位、公司和技术栈数据 | opt-in 候选 |
| JSearch | `https://www.openwebninja.com/api/jsearch` | 聚合职位搜索，适合快速原型 | opt-in 候选 |
| Jooble | `https://help.jooble.org/en/support/solutions/articles/60001448238-rest-api-documentation` | 全球职位搜索 API | opt-in 候选 |
| 用户粘贴 / 公司官网公开 JD | 用户手动输入 | 合规、可审计 | 默认支持 |

## 3. 禁止路线

- 默认抓取 BOSS、猎聘、拉勾、LinkedIn；
- 使用账号、cookie、验证码绕过、反爬绕过；
- 未经授权打开招聘平台页面；
- 长期运行爬虫或后台队列；
- 对外自动沟通或自动投递。

## 4. 文档级接口建议

```text
GET /api/market/providers
POST /api/market/search-runs
GET /api/market/search-runs/{run_id}
GET /api/market/snapshots/{snapshot_id}
```

这些接口只是 P9.1 规划，后续是否实现需要用户批准开发阶段。

## 5. 验收原则

- provider 未配置时，不得显示真实市场数据；
- provider 配置但未调用时，不得显示已调用；
- provider 调用失败时，不得用 fixture 静默替代；
- 聚合数字必须可追溯；
- 报告必须列出 provider、query、调用时间、结果数量、失败信息和 source refs。

